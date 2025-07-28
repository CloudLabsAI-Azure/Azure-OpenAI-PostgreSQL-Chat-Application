-- Sample database schema for the Azure OpenAI PostgreSQL Chat Application
-- This file contains example tables that demonstrate the application's capabilities

-- Create database (run this as a superuser or with createdb privileges)
-- Note: You may need to run this separately from the rest of the script
-- since you cannot create a database from within a database transaction

-- Uncomment the following lines if you need to create the database
-- DROP DATABASE IF EXISTS chatappdb;
-- CREATE DATABASE chatappdb
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'en_US.utf8'
--     LC_CTYPE = 'en_US.utf8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     IS_TEMPLATE = False;

-- Connect to the chatappdb database before running the rest of this script
-- \c chatappdb;

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    postal_code VARCHAR(20),
    date_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    date_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_status VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT,
    notes TEXT
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_city ON customers(city);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);

-- Insert sample data for demonstration

-- Sample customers
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, postal_code) VALUES
('John', 'Doe', 'john.doe@email.com', '555-0101', '123 Main St', 'New York', 'NY', '10001'),
('Jane', 'Smith', 'jane.smith@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001'),
('Bob', 'Johnson', 'bob.johnson@email.com', '555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601'),
('Alice', 'Williams', 'alice.williams@email.com', '555-0104', '321 Elm St', 'Houston', 'TX', '77001'),
('Charlie', 'Brown', 'charlie.brown@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 'AZ', '85001')
ON CONFLICT (email) DO NOTHING;

-- Sample products
INSERT INTO products (product_name, description, category, price, stock_quantity) VALUES
('Laptop Computer', 'High-performance laptop for professional use', 'Electronics', 1299.99, 25),
('Wireless Mouse', 'Ergonomic wireless mouse with precision tracking', 'Electronics', 29.99, 100),
('Office Chair', 'Comfortable ergonomic office chair', 'Furniture', 299.99, 15),
('Standing Desk', 'Adjustable height standing desk', 'Furniture', 599.99, 8),
('Coffee Mug', 'Ceramic coffee mug with company logo', 'Office Supplies', 12.99, 200),
('Notebook Set', 'Set of 3 premium notebooks', 'Office Supplies', 24.99, 75),
('Desk Lamp', 'LED desk lamp with adjustable brightness', 'Electronics', 79.99, 30),
('Water Bottle', 'Stainless steel insulated water bottle', 'Office Supplies', 19.99, 150)
ON CONFLICT DO NOTHING;

-- Sample orders (using customer and product IDs from the inserts above)
INSERT INTO orders (customer_id, order_date, total_amount, order_status, shipping_address)
VALUES 
(1, CURRENT_TIMESTAMP - INTERVAL '25 days', 1329.98, 'completed', '123 Main St, New York, NY 10001'),
(2, CURRENT_TIMESTAMP - INTERVAL '20 days', 599.99, 'completed', '456 Oak Ave, Los Angeles, CA 90001'),
(3, CURRENT_TIMESTAMP - INTERVAL '15 days', 324.98, 'completed', '789 Pine Rd, Chicago, IL 60601'),
(4, CURRENT_TIMESTAMP - INTERVAL '10 days', 92.98, 'shipped', '321 Elm St, Houston, TX 77001'),
(5, CURRENT_TIMESTAMP - INTERVAL '5 days', 44.98, 'pending', '654 Maple Dr, Phoenix, AZ 85001');

-- Sample order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES 
-- Order 1: Laptop + Mouse
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
-- Order 2: Standing Desk
(2, 4, 1, 599.99),
-- Order 3: Office Chair + Notebook Set
(3, 3, 1, 299.99),
(3, 6, 1, 24.99),
-- Order 4: Desk Lamp + Coffee Mug
(4, 7, 1, 79.99),
(4, 5, 1, 12.99),
-- Order 5: Water Bottle + Notebook Set
(5, 8, 1, 19.99),
(5, 6, 1, 24.99);

-- Create a view for order summaries
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    o.order_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email AS customer_email,
    o.order_date,
    o.total_amount,
    o.order_status,
    COUNT(oi.order_item_id) AS item_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, c.first_name, c.last_name, c.email, o.order_date, o.total_amount, o.order_status
ORDER BY o.order_date DESC;

-- Create a function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update last_updated timestamps
CREATE TRIGGER update_customers_last_updated 
    BEFORE UPDATE ON customers 
    FOR EACH ROW EXECUTE FUNCTION update_last_updated_column();

CREATE TRIGGER update_products_last_updated 
    BEFORE UPDATE ON products 
    FOR EACH ROW EXECUTE FUNCTION update_last_updated_column();

-- Grant appropriate permissions (adjust as needed for your security requirements)
-- These would typically be run with administrative privileges
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO chatapp_user;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO chatapp_user;

COMMENT ON TABLE customers IS 'Customer information for the e-commerce platform';
COMMENT ON TABLE products IS 'Product catalog with pricing and inventory';
COMMENT ON TABLE orders IS 'Customer orders with status and totals';
COMMENT ON TABLE order_items IS 'Individual items within each order';
COMMENT ON VIEW order_summary IS 'Convenient view of order information with customer details';

-- Add more diverse customers from different regions
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, postal_code) VALUES
-- West Coast customers
('Sarah', 'Wilson', 'sarah.wilson@gmail.com', '555-0106', '789 Pacific Ave', 'Seattle', 'WA', '98101'),
('Mike', 'Davis', 'mike.davis@gmail.com', '555-0107', '321 Golden Gate Blvd', 'San Francisco', 'CA', '94102'),
('Lisa', 'Rodriguez', 'lisa.rodriguez@yahoo.com', '555-0108', '456 Sunset Strip', 'Los Angeles', 'CA', '90028'),
('David', 'Chen', 'david.chen@outlook.com', '555-0109', '654 Tech Drive', 'San Jose', 'CA', '95110'),

-- East Coast customers
('Emily', 'Thompson', 'emily.thompson@gmail.com', '555-0110', '123 Broadway', 'New York', 'NY', '10001'),
('James', 'Anderson', 'james.anderson@email.com', '555-0111', '789 Liberty St', 'Boston', 'MA', '02101'),
('Maria', 'Garcia', 'maria.garcia@hotmail.com', '555-0112', '456 Ocean Ave', 'Miami', 'FL', '33101'),
('Robert', 'Martinez', 'robert.martinez@gmail.com', '555-0113', '321 Capitol Hill', 'Washington', 'DC', '20001'),

-- Midwest customers
('Jennifer', 'White', 'jennifer.white@yahoo.com', '555-0114', '654 Lake Shore Dr', 'Chicago', 'IL', '60601'),
('Kevin', 'Taylor', 'kevin.taylor@outlook.com', '555-0115', '789 Motor City Blvd', 'Detroit', 'MI', '48201'),
('Amanda', 'Brown', 'amanda.brown@gmail.com', '555-0116', '123 Music Row', 'Nashville', 'TN', '37201'),
('Christopher', 'Lee', 'christopher.lee@email.com', '555-0117', '456 Gateway Arch Dr', 'St. Louis', 'MO', '63101'),

-- South customers
('Michelle', 'Harris', 'michelle.harris@gmail.com', '555-0118', '789 Space Center Blvd', 'Houston', 'TX', '77058'),
('Daniel', 'Clark', 'daniel.clark@yahoo.com', '555-0119', '321 Peachtree St', 'Atlanta', 'GA', '30301'),
('Ashley', 'Lewis', 'ashley.lewis@outlook.com', '555-0120', '654 French Quarter', 'New Orleans', 'LA', '70112'),
('Ryan', 'Walker', 'ryan.walker@gmail.com', '555-0121', '123 River Walk', 'San Antonio', 'TX', '78201')

ON CONFLICT (email) DO NOTHING;

-- Add more diverse products across different categories
INSERT INTO products (product_name, description, category, price, stock_quantity) VALUES
-- Electronics
('4K Monitor', '27-inch 4K UHD monitor with HDR support', 'Electronics', 449.99, 20),
('Mechanical Keyboard', 'RGB mechanical gaming keyboard', 'Electronics', 129.99, 45),
('Webcam HD', '1080p webcam with auto-focus', 'Electronics', 89.99, 35),
('Bluetooth Headphones', 'Noise-canceling wireless headphones', 'Electronics', 199.99, 60),
('USB-C Hub', '7-in-1 USB-C hub with HDMI and ethernet', 'Electronics', 79.99, 80),
('Tablet 10-inch', 'Android tablet with stylus support', 'Electronics', 299.99, 25),
('Smart Watch', 'Fitness tracking smartwatch', 'Electronics', 249.99, 40),
('Portable SSD', '1TB external SSD drive', 'Electronics', 159.99, 30),

-- Furniture
('Executive Desk', 'Large executive desk with drawers', 'Furniture', 799.99, 5),
('Conference Table', '8-person conference table', 'Furniture', 1299.99, 3),
('Filing Cabinet', '4-drawer locking filing cabinet', 'Furniture', 349.99, 12),
('Bookshelf', '5-tier wooden bookshelf', 'Furniture', 199.99, 18),
('Ergonomic Footrest', 'Adjustable ergonomic footrest', 'Furniture', 49.99, 25),
('Monitor Arm', 'Dual monitor desk mount arm', 'Furniture', 89.99, 22),
('Desk Organizer', 'Bamboo desk organizer with compartments', 'Furniture', 39.99, 50),

-- Office Supplies
('Wireless Presenter', 'Wireless presenter with laser pointer', 'Office Supplies', 34.99, 40),
('Document Scanner', 'Portable document scanner', 'Office Supplies', 199.99, 15),
('Label Maker', 'Electronic label maker with tape', 'Office Supplies', 69.99, 20),
('Whiteboard', '4x3 feet magnetic whiteboard', 'Office Supplies', 129.99, 8),
('Paper Shredder', 'Cross-cut paper shredder', 'Office Supplies', 89.99, 10),
('Stapler Heavy Duty', 'Heavy-duty electric stapler', 'Office Supplies', 159.99, 12),
('Calculator Scientific', 'Advanced scientific calculator', 'Office Supplies', 29.99, 55),
('Pen Set Luxury', 'Premium pen set in gift box', 'Office Supplies', 79.99, 30),

-- New Categories
-- Software & Licenses
('Project Management Software', 'Annual license for project management tool', 'Software', 299.99, 100),
('Antivirus Premium', 'Premium antivirus software 1-year license', 'Software', 89.99, 200),
('Design Software Suite', 'Professional design software bundle', 'Software', 599.99, 50),
('Video Editing Pro', 'Professional video editing software', 'Software', 399.99, 75),

-- Accessories
('Phone Stand', 'Adjustable aluminum phone stand', 'Accessories', 24.99, 85),
('Cable Management Kit', 'Complete cable management solution', 'Accessories', 19.99, 100),
('Laptop Cooling Pad', 'RGB laptop cooling pad with fans', 'Accessories', 49.99, 35),
('Wireless Charger', 'Fast wireless charging pad', 'Accessories', 39.99, 60),
('Blue Light Glasses', 'Computer glasses with blue light filter', 'Accessories', 59.99, 45)

ON CONFLICT DO NOTHING;

-- Add more realistic orders with varied patterns
INSERT INTO orders (customer_id, order_date, total_amount, order_status, shipping_address) VALUES
-- Recent orders (last 30 days)
(6, CURRENT_TIMESTAMP - INTERVAL '2 days', 679.98, 'processing', '789 Pacific Ave, Seattle, WA 98101'),
(7, CURRENT_TIMESTAMP - INTERVAL '3 days', 1849.97, 'shipped', '321 Golden Gate Blvd, San Francisco, CA 94102'),
(8, CURRENT_TIMESTAMP - INTERVAL '4 days', 249.99, 'completed', '456 Sunset Strip, Los Angeles, CA 90028'),
(9, CURRENT_TIMESTAMP - INTERVAL '5 days', 389.98, 'completed', '654 Tech Drive, San Jose, CA 95110'),
(10, CURRENT_TIMESTAMP - INTERVAL '6 days', 159.99, 'completed', '123 Broadway, New York, NY 10001'),

-- Orders from 1-2 weeks ago
(11, CURRENT_TIMESTAMP - INTERVAL '8 days', 569.98, 'completed', '789 Liberty St, Boston, MA 02101'),
(12, CURRENT_TIMESTAMP - INTERVAL '9 days', 299.99, 'completed', '456 Ocean Ave, Miami, FL 33101'),
(13, CURRENT_TIMESTAMP - INTERVAL '10 days', 829.98, 'completed', '321 Capitol Hill, Washington, DC 20001'),
(14, CURRENT_TIMESTAMP - INTERVAL '12 days', 179.98, 'completed', '654 Lake Shore Dr, Chicago, IL 60601'),
(15, CURRENT_TIMESTAMP - INTERVAL '14 days', 699.99, 'completed', '789 Motor City Blvd, Detroit, MI 48201'),

-- Orders from 2-4 weeks ago
(16, CURRENT_TIMESTAMP - INTERVAL '16 days', 449.99, 'completed', '123 Music Row, Nashville, TN 37201'),
(17, CURRENT_TIMESTAMP - INTERVAL '18 days', 1299.99, 'completed', '456 Gateway Arch Dr, St. Louis, MO 63101'),
(18, CURRENT_TIMESTAMP - INTERVAL '20 days', 89.99, 'completed', '789 Space Center Blvd, Houston, TX 77058'),
(19, CURRENT_TIMESTAMP - INTERVAL '22 days', 359.98, 'completed', '321 Peachtree St, Atlanta, GA 30301'),
(20, CURRENT_TIMESTAMP - INTERVAL '25 days', 799.99, 'completed', '654 French Quarter, New Orleans, LA 70112'),

-- Older orders (1-3 months ago)
(1, CURRENT_TIMESTAMP - INTERVAL '35 days', 329.98, 'completed', '123 Main St, New York, NY 10001'),
(2, CURRENT_TIMESTAMP - INTERVAL '42 days', 889.98, 'completed', '456 Oak Ave, Los Angeles, CA 90001'),
(3, CURRENT_TIMESTAMP - INTERVAL '56 days', 199.99, 'completed', '789 Pine Rd, Chicago, IL 60601'),
(4, CURRENT_TIMESTAMP - INTERVAL '63 days', 729.98, 'completed', '321 Elm St, Houston, TX 77001'),
(5, CURRENT_TIMESTAMP - INTERVAL '78 days', 149.99, 'completed', '654 Maple Dr, Phoenix, AZ 85001'),

-- High-value enterprise orders
(7, CURRENT_TIMESTAMP - INTERVAL '15 days', 2999.97, 'completed', '321 Golden Gate Blvd, San Francisco, CA 94102'),
(13, CURRENT_TIMESTAMP - INTERVAL '30 days', 3599.96, 'completed', '321 Capitol Hill, Washington, DC 20001'),
(17, CURRENT_TIMESTAMP - INTERVAL '45 days', 2199.98, 'completed', '456 Gateway Arch Dr, St. Louis, MO 63101');

-- Add corresponding order items for the new orders
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
-- Order 6 (Sarah Wilson): Monitor + Keyboard
(6, 9, 1, 449.99),
(6, 10, 2, 129.99),

-- Order 7 (Mike Davis): High-value tech order
(7, 9, 2, 449.99), -- 2 monitors
(7, 1, 1, 1299.99), -- laptop
(7, 4, 1, 599.99), -- standing desk
(7, 12, 1, 199.99), -- headphones

-- Order 8 (Lisa Rodriguez): Smartwatch
(8, 15, 1, 249.99),

-- Order 9 (David Chen): Tablet + accessories
(9, 14, 1, 299.99),
(9, 13, 1, 89.99),

-- Order 10 (Emily Thompson): Storage
(10, 16, 1, 159.99),

-- Order 11 (James Anderson): Furniture combo
(11, 17, 1, 799.99), -- executive desk
(11, 21, 1, 49.99), -- footrest

-- Order 12 (Maria Garcia): Tablet
(12, 14, 1, 299.99),

-- Order 13 (Robert Martinez): Office setup
(13, 18, 1, 1299.99), -- conference table
(13, 19, 2, 349.99), -- filing cabinets

-- Order 14 (Jennifer White): Small accessories
(14, 25, 1, 34.99),
(14, 29, 1, 29.99),
(14, 33, 2, 24.99),

-- Order 15 (Kevin Taylor): Software
(15, 28, 1, 299.99),
(15, 30, 1, 399.99),

-- Order 16 (Amanda Brown): Monitor
(16, 9, 1, 449.99),

-- Order 17 (Christopher Lee): Conference table
(17, 18, 1, 1299.99),

-- Order 18 (Michelle Harris): Shredder
(18, 27, 1, 89.99),

-- Order 19 (Daniel Clark): Office supplies
(19, 24, 1, 129.99),
(19, 26, 1, 199.99),
(19, 29, 1, 29.99),

-- Order 20 (Ashley Lewis): Executive desk
(20, 17, 1, 799.99),

-- Order 21 (John Doe): Accessories
(21, 11, 1, 89.99),
(21, 22, 1, 89.99),
(21, 33, 6, 24.99),

-- Order 22 (Jane Smith): Tech bundle
(22, 12, 2, 199.99),
(22, 13, 2, 89.99),
(22, 35, 2, 39.99),
(22, 36, 2, 59.99),

-- Order 23 (Bob Johnson): Bookshelf
(23, 20, 1, 199.99),

-- Order 24 (Alice Williams): Office furniture
(24, 3, 2, 299.99),
(24, 10, 2, 129.99),

-- Order 25 (Charlie Brown): Calculator + pen set
(25, 29, 1, 29.99),
(25, 30, 1, 79.99),
(25, 5, 3, 12.99),

-- High-value enterprise orders
-- Order 26 (Mike Davis): Enterprise setup
(26, 1, 3, 1299.99), -- 3 laptops
(26, 9, 3, 449.99), -- 3 monitors
(26, 10, 3, 129.99), -- 3 keyboards

-- Order 27 (Robert Martinez): Government office
(27, 17, 2, 799.99), -- 2 executive desks
(27, 18, 1, 1299.99), -- conference table
(27, 19, 4, 349.99), -- 4 filing cabinets
(27, 3, 6, 299.99), -- 6 office chairs

-- Order 28 (Christopher Lee): Corporate IT
(28, 1, 2, 1299.99), -- 2 laptops
(28, 14, 3, 299.99), -- 3 tablets
(28, 28, 5, 299.99); -- 5 software licenses

-- Update some order totals to reflect bulk discounts (realistic business scenario)
UPDATE orders SET total_amount = 3899.97 WHERE order_id = 26; -- 10% bulk discount
UPDATE orders SET total_amount = 7999.94 WHERE order_id = 27; -- 15% bulk discount  
UPDATE orders SET total_amount = 4399.95 WHERE order_id = 28; -- 12% bulk discount

-- Add some seasonal/promotional data
INSERT INTO products (product_name, description, category, price, stock_quantity) VALUES
('Holiday Bundle', 'Special holiday bundle with laptop, mouse, and headphones', 'Bundles', 1399.99, 10),
('Back to School Kit', 'Student essentials: notebook, calculator, pen set', 'Bundles', 89.99, 50),
('Work From Home Setup', 'Complete WFH setup: webcam, headphones, lighting', 'Bundles', 349.99, 25),
('Gaming Starter Pack', 'Gaming essentials: mechanical keyboard, mouse, headset', 'Gaming', 299.99, 15);

-- Create analytics tables for dashboard
CREATE TABLE IF NOT EXISTS sales_analytics (
    id SERIAL PRIMARY KEY,
    date_recorded DATE DEFAULT CURRENT_DATE,
    total_sales DECIMAL(12, 2),
    total_orders INTEGER,
    avg_order_value DECIMAL(10, 2),
    top_category VARCHAR(50),
    new_customers INTEGER,
    repeat_customers INTEGER
);

-- Create customer analytics view
CREATE OR REPLACE VIEW customer_analytics AS
SELECT 
    c.state,
    COUNT(*) as customer_count,
    AVG(o.total_amount) as avg_spending,
    SUM(o.total_amount) as total_spending,
    COUNT(o.order_id) as total_orders
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.state
ORDER BY total_spending DESC NULLS LAST;

-- Create product performance view
CREATE OR REPLACE VIEW product_performance AS
SELECT 
    p.category,
    p.product_name,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as revenue,
    COUNT(DISTINCT oi.order_id) as orders_count,
    AVG(oi.unit_price) as avg_price
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category, p.product_name, p.product_id
ORDER BY revenue DESC NULLS LAST;

-- Create monthly sales trend view
CREATE OR REPLACE VIEW monthly_sales_trend AS
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    COUNT(*) as order_count,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
WHERE o.order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;

-- Create daily analytics data for the last 30 days
INSERT INTO sales_analytics (date_recorded, total_sales, total_orders, avg_order_value, top_category, new_customers, repeat_customers)
SELECT 
    date_series.date,
    COALESCE(daily_stats.total_sales, 0),
    COALESCE(daily_stats.total_orders, 0),
    COALESCE(daily_stats.avg_order_value, 0),
    COALESCE(daily_stats.top_category, 'Electronics'),
    FLOOR(RANDOM() * 10 + 1)::INTEGER,
    FLOOR(RANDOM() * 20 + 5)::INTEGER
FROM (
    SELECT CURRENT_DATE - INTERVAL '1 day' * generate_series(0, 29) as date
) date_series
LEFT JOIN (
    SELECT 
        DATE(o.order_date) as order_date,
        SUM(o.total_amount) as total_sales,
        COUNT(*) as total_orders,
        AVG(o.total_amount) as avg_order_value,
        (
            SELECT p.category 
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.product_id 
            JOIN orders o2 ON oi.order_id = o2.order_id 
            WHERE DATE(o2.order_date) = DATE(o.order_date)
            GROUP BY p.category 
            ORDER BY SUM(oi.total_price) DESC 
            LIMIT 1
        ) as top_category
    FROM orders o
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY DATE(o.order_date)
) daily_stats ON date_series.date = daily_stats.order_date
WHERE NOT EXISTS (
    SELECT 1 FROM sales_analytics sa WHERE sa.date_recorded = date_series.date
);

-- Add more sample orders with different patterns for analytics
INSERT INTO orders (customer_id, order_date, total_amount, order_status, shipping_address) VALUES
-- Add some returns and cancellations for realistic analytics
(1, CURRENT_TIMESTAMP - INTERVAL '3 days', 199.99, 'returned', '123 Main St, New York, NY 10001'),
(5, CURRENT_TIMESTAMP - INTERVAL '1 day', 89.99, 'cancelled', '654 Maple Dr, Phoenix, AZ 85001'),
(8, CURRENT_TIMESTAMP - INTERVAL '7 days', 349.99, 'returned', '456 Sunset Strip, Los Angeles, CA 90028'),

-- High-frequency customer orders (for customer loyalty analysis)
(2, CURRENT_TIMESTAMP - INTERVAL '1 hour', 49.99, 'processing', '456 Oak Ave, Los Angeles, CA 90001'),
(2, CURRENT_TIMESTAMP - INTERVAL '3 hours', 129.99, 'processing', '456 Oak Ave, Los Angeles, CA 90001'),
(7, CURRENT_TIMESTAMP - INTERVAL '2 hours', 79.99, 'shipped', '321 Golden Gate Blvd, San Francisco, CA 94102'),
(7, CURRENT_TIMESTAMP - INTERVAL '5 hours', 299.99, 'completed', '321 Golden Gate Blvd, San Francisco, CA 94102'),

-- Weekend orders (for time-based analytics)
(10, DATE_TRUNC('week', CURRENT_TIMESTAMP) + INTERVAL '6 days', 199.99, 'completed', '123 Broadway, New York, NY 10001'),
(11, DATE_TRUNC('week', CURRENT_TIMESTAMP) + INTERVAL '6 days', 89.99, 'completed', '789 Liberty St, Boston, MA 02101'),
(12, DATE_TRUNC('week', CURRENT_TIMESTAMP) + INTERVAL '5 days', 449.99, 'completed', '456 Ocean Ave, Miami, FL 33101'),

-- Bulk orders from business customers
(13, CURRENT_TIMESTAMP - INTERVAL '1 day', 2999.99, 'processing', '321 Capitol Hill, Washington, DC 20001'),
(17, CURRENT_TIMESTAMP - INTERVAL '2 days', 1899.99, 'shipped', '456 Gateway Arch Dr, St. Louis, MO 63101');

-- Add corresponding order items for analytics
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
-- Returned/cancelled orders
((SELECT MAX(order_id) FROM orders) - 11, 20, 1, 199.99), -- bookshelf return
((SELECT MAX(order_id) FROM orders) - 10, 5, 1, 89.99),   -- cancelled coffee mug order
((SELECT MAX(order_id) FROM orders) - 9, 25, 1, 349.99),  -- scanner return

-- High-frequency customer orders
((SELECT MAX(order_id) FROM orders) - 8, 33, 2, 24.99),   -- phone stands
((SELECT MAX(order_id) FROM orders) - 7, 10, 1, 129.99),  -- keyboard
((SELECT MAX(order_id) FROM orders) - 6, 7, 1, 79.99),    -- desk lamp
((SELECT MAX(order_id) FROM orders) - 5, 14, 1, 299.99),  -- tablet

-- Weekend orders
((SELECT MAX(order_id) FROM orders) - 4, 20, 1, 199.99),  -- bookshelf
((SELECT MAX(order_id) FROM orders) - 3, 27, 1, 89.99),   -- shredder
((SELECT MAX(order_id) FROM orders) - 2, 9, 1, 449.99),   -- monitor

-- Bulk business orders
((SELECT MAX(order_id) FROM orders) - 1, 1, 3, 1299.99),  -- 3 laptops
((SELECT MAX(order_id) FROM orders) - 1, 9, 3, 449.99),   -- 3 monitors
((SELECT MAX(order_id) FROM orders), 1, 2, 1299.99),      -- 2 laptops
((SELECT MAX(order_id) FROM orders), 3, 4, 299.99);       -- 4 chairs

-- Create customer segments table for advanced analytics
CREATE TABLE IF NOT EXISTS customer_segments (
    segment_id SERIAL PRIMARY KEY,
    segment_name VARCHAR(50) NOT NULL,
    description TEXT,
    min_orders INTEGER DEFAULT 0,
    min_total_spent DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customer_segments (segment_name, description, min_orders, min_total_spent) VALUES
('VIP', 'High-value customers with multiple large orders', 5, 2000.00),
('Regular', 'Frequent customers with moderate spending', 3, 500.00),
('New', 'Recent customers with limited purchase history', 1, 0.00),
('Inactive', 'Customers with no recent activity', 0, 0.00);

-- Create a comprehensive analytics view
CREATE OR REPLACE VIEW comprehensive_analytics AS
WITH customer_stats AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name as customer_name,
        c.city,
        c.state,
        COUNT(o.order_id) as total_orders,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        COALESCE(AVG(o.total_amount), 0) as avg_order_value,
        MAX(o.order_date) as last_order_date,
        CASE 
            WHEN COUNT(o.order_id) >= 5 AND SUM(o.total_amount) >= 2000 THEN 'VIP'
            WHEN COUNT(o.order_id) >= 3 AND SUM(o.total_amount) >= 500 THEN 'Regular'
            WHEN COUNT(o.order_id) >= 1 THEN 'New'
            ELSE 'Inactive'
        END as customer_segment
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.city, c.state
)
SELECT * FROM customer_stats;

-- Add some product reviews/ratings simulation through comments
COMMENT ON COLUMN products.product_name IS 'Product name with SEO optimization';
COMMENT ON COLUMN products.category IS 'Product category for filtering and analytics';
COMMENT ON COLUMN orders.order_status IS 'Order status: pending, processing, shipped, completed, cancelled, returned';
