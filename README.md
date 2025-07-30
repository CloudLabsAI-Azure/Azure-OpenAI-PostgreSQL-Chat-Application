# Azure OpenAI PostgreSQL Chat Application

A sophisticated chat application that bridges natural language and database queries using Azure OpenAI and PostgreSQL. Users can ask questions in plain English, and the application will convert them to SQL, execute against PostgreSQL, and return human-readable results with advanced analytics and security features.

## Features

### Core Functionality
- 🤖 **Natural Language to SQL**: Convert plain English questions to SQL queries using Azure OpenAI
- 🗄️ **PostgreSQL Integration**: Execute queries against PostgreSQL database with connection pooling
- 📊 **SQL to Natural Language**: Convert database results back to conversational responses
- 🌐 **Web Interface**: Clean, modern chat interface built with Flask and responsive design
- ⚡ **Real-time Chat**: Interactive chat experience with typing indicators and instant responses

### Advanced Analytics
- 📈 **Python Data Visualization**: Interactive charts using Plotly, matplotlib, and seaborn
- 📊 **Comprehensive Analytics Dashboard**: Real-time metrics with 95% width responsive layout
- � **Advanced Metrics**: Customer analysis, sales trends, and predictive insights
- 📉 **Interactive Charts**: Sales trends, category analysis, and geographical data visualization

### Security & Data Fetching
- 🔐 **Enhanced Security**: Multi-layer security with input validation, SQL injection protection, and XSS prevention
- 🛡️ **Rate Limiting**: Intelligent rate limiting per endpoint with configurable limits
- 📡 **Multi-Source Data Fetching**: RSS feeds, financial APIs, CSV data, and social media trends
- 🔒 **Security Headers**: CORS, CSP, and other security headers via Flask-Talisman
- 🎯 **Input Validation**: Comprehensive input sanitization and threat detection

## Architecture

```
User Question → Azure OpenAI → SQL Query → PostgreSQL → Results → Azure OpenAI → Natural Language Response
```
## API Endpoints

### Core Endpoints
- `GET /` - Main chat interface
- `POST /api/chat` - Process natural language queries
- `GET /api/analytics` - Get comprehensive analytics dashboard
- `GET /api/health` - Health check endpoint

### Data Fetching Endpoints
- `GET /api/data/fetch-all` - Fetch data from all sources
- `GET /api/data/news` - Get latest news from RSS feeds
- `GET /api/data/financial` - Fetch financial market data
- `GET /api/data/social-trends` - Get social media trends
- `GET /api/data/csv` - Load CSV data from external sources

### Security Endpoints
- `POST /api/security/validate` - Validate input for security threats

## Prerequisites

- Python 3.8+
- Azure OpenAI service
- PostgreSQL database
- Azure subscription with appropriate permissions

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (see Configuration section)
4. Deploy Azure resources using the provided Bicep templates
5. Run the application:
   ```bash
   python src/app.py
   ```

## Configuration

Required environment variables:
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION`: API version (e.g., "2024-02-01")
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your GPT model deployment name
- `POSTGRES_HOST`: PostgreSQL server hostname
- `POSTGRES_DATABASE`: Database name
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password (use Azure Key Vault in production)
- `SECRET_KEY`: Flask secret key for session management
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `ENCRYPTION_KEY`: Key for data encryption

## Deployment

This application is designed to be deployed on Azure Container Apps with the following Azure resources:
- Azure OpenAI Service
- Azure Database for PostgreSQL
- Azure Container Apps
- Azure Key Vault (for secrets)
- Azure Log Analytics (for monitoring)

Use the provided Bicep templates in the `infra/` directory for automated deployment.

## Usage

### Basic Chat Interface
1. Open the web interface at `http://localhost:5000`
2. Type your question in natural language (e.g., "Show me all customers from New York")
3. The application will:
   - Convert your question to SQL using Azure OpenAI
   - Execute the query against PostgreSQL
   - Convert the results back to natural language
   - Display the conversational response with analytics

## Sample Questions

### 👥 Customer Questions
```
"Show me all customers from New York"
"How many customers do we have in total?"
"List customers who have placed orders"
"Find customers with email addresses containing 'gmail'"
"Show me the newest customer"
"Which customers have spent more than $1000?"
"Find customers who haven't placed any orders in the last 6 months"
"Show me customers grouped by state"
"List the top 5 customers by total spending"
"Find all customers from California or Texas"
```

### 🛍️ Product Questions
```
"What products do we sell?"
"Show me products that cost more than $100"
"Which products are in the Electronics category?"
"What's our most expensive product?"
"List products that are out of stock"
"Show me all furniture items"
"Find products with names containing 'laptop'"
"Which products have never been ordered?"
"Show me the top 10 best-selling products"
"List products by category with their average price"
```

### 📦 Order Questions
```
"Show me all orders from the last month"
"What's the total value of all completed orders?"
"List orders that are still pending"
"Show me John Doe's orders"
"What's the average order amount?"
"Find the largest order by total amount"
"Show me orders with more than 3 items"
"List all orders placed today"
"Find orders between $500 and $1000"
"Show me orders grouped by status"
```

### 🔍 Advanced Analytics Questions
```
"Which customer has spent the most money?"
"What's the most popular product category?"
"Show me orders with more than 2 items"
"List customers who haven't placed any orders"
"What's the total revenue from Electronics products?"
"Show me the order history for customer with email 'jane.smith@email.com'"
"Calculate the monthly revenue for this year"
"Find the average order value by customer state"
"Show me the conversion rate from customers to orders"
"What's the profit margin for each product category?"
```

### 📈 Business Intelligence Questions
```
"How many orders were placed each month?"
"What's the average number of items per order?"
"Which products have never been ordered?"
"Show me customers grouped by state"
"What's the breakdown of orders by status?"
"Calculate the customer lifetime value"
"Show me seasonal trends in sales"
"What's the order fulfillment rate?"
"Find the most profitable customers"
"Analyze sales performance by region"
```

### 📊 Data Analysis Questions
```
"Create a chart showing sales trends over the last 7 days"
"Generate a pie chart of orders by category"
"Show me a bar chart of top customers"
"Plot the geographical distribution of sales"
"Create a visualization of monthly revenue trends"
"Show me customer segmentation analysis"
"Generate insights about product performance"
"Create predictive analytics for next month's sales"
"Show correlation between customer location and spending"
"Visualize inventory levels across categories"
```

### 🌐 External Data Questions
```
"Show me current financial market data"
"What are the latest news headlines?"
"Get social media trends related to our products"
"Fetch current exchange rates"
"Show me cryptocurrency prices"
"Load external CSV data for analysis"
"Get weather data for our store locations"
"Fetch competitor pricing information"
"Show economic indicators"
"Get industry trend data"
```

### Advanced Features
- **Analytics Dashboard**: View real-time metrics, charts, and insights
- **Data Visualization**: Interactive Plotly charts with Python-generated analytics
- **External Data**: Fetch live data from news feeds, financial APIs, and social media
- **Security Validation**: Test input validation and security features

### API Usage Examples
```bash
# Get comprehensive analytics
curl http://localhost:5000/api/analytics

# Fetch all external data sources
curl http://localhost:5000/api/data/fetch-all

# Get financial market data
curl http://localhost:5000/api/data/financial

# Validate input security
curl -X POST http://localhost:5000/api/security/validate \
  -H "Content-Type: application/json" \
  -d '{"input": "SELECT * FROM users"}'
```

## Development

### Project Structure
```
├── src/
│   ├── app.py              # Main Flask application with security
│   ├── database.py         # PostgreSQL connection and operations
│   ├── openai_service.py   # Azure OpenAI integration
│   ├── analytics_service.py # Python data visualization service
│   ├── security.py         # Security and authentication manager
│   ├── data_fetcher.py     # Multi-source data fetching service
│   └── utils.py            # Utility functions
├── templates/
│   └── index.html          # Enhanced web interface template
├── static/
│   ├── style.css           # Responsive styles with 95% width layout
│   └── script.js           # Frontend JavaScript with Plotly integration
├── infra/                  # Azure infrastructure templates
└── requirements.txt        # Python dependencies with security packages
```

### Running Locally

1. Set up a local PostgreSQL database
2. Configure environment variables
3. Run: `python src/app.py`
4. Open http://localhost:5000

## Security Considerations

### Built-in Security Features
- **Multi-layer Input Validation**: SQL injection and XSS protection
- **Rate Limiting**: Configurable limits per endpoint (30 requests/minute for chat, 10 for analytics)
- **Security Headers**: CORS, CSP, and HSTS via Flask-Talisman
- **Input Sanitization**: Comprehensive threat detection and content filtering
- **Session Management**: Secure JWT tokens with configurable expiry
- **IP Whitelisting**: Configurable IP address restrictions
- **Data Encryption**: AES encryption for sensitive data storage
- **Password Hashing**: bcrypt for secure password storage

### Azure Security Integration
- All secrets managed through Azure Key Vault
- Azure Managed Identity for service-to-service authentication
- Audit logging for all database operations
- Azure Monitor integration for security event tracking

### Development Security
- Environment variable protection
- Secure cookie configuration
## Contributing

1. Follow the coding guidelines in `.github/copilot-instructions.md`
2. Ensure all tests pass
3. Update documentation as needed
4. Submit pull requests for review
