"""
Database Manager for PostgreSQL operations.
Handles connection management, query execution, and schema information.
"""

import os
import logging
import psycopg2
from psycopg2 import pool, sql
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages PostgreSQL database connections and operations with connection pooling.
    """
    
    def __init__(self, min_connections=1, max_connections=10):
        """
        Initialize database manager with connection pool.
        
        Args:
            min_connections (int): Minimum number of connections in pool
            max_connections (int): Maximum number of connections in pool
        """
        self.db_config = {
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'database': os.environ.get('POSTGRES_DATABASE', 'postgres'),
            'user': os.environ.get('POSTGRES_USER', 'postgres'),
            'password': os.environ.get('POSTGRES_PASSWORD', ''),
            'port': int(os.environ.get('POSTGRES_PORT', 5432)),
            'sslmode': os.environ.get('POSTGRES_SSL_MODE', 'prefer')
        }
        
        self.connection_pool = None
        self._init_connection_pool(min_connections, max_connections)
    
    def _init_connection_pool(self, min_connections, max_connections):
        """
        Initialize PostgreSQL connection pool.
        
        Args:
            min_connections (int): Minimum connections
            max_connections (int): Maximum connections
        """
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                **self.db_config
            )
            logger.info("Database connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with automatic cleanup.
        
        Yields:
            psycopg2.connection: Database connection
        """
        connection = None
        try:
            connection = self.connection_pool.getconn()
            if connection:
                yield connection
            else:
                raise Exception("Failed to get connection from pool")
                
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {str(e)}")
            raise
            
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters for parameterized queries
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Set statement timeout for safety
                    cursor.execute("SET statement_timeout = '30s'")
                    
                    # Execute query with parameters if provided
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    # Fetch results
                    results = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    
                    # Convert to list of dictionaries
                    formatted_results = []
                    for row in results:
                        formatted_results.append(dict(zip(column_names, row)))
                    
                    logger.info(f"Query executed successfully, returned {len(formatted_results)} rows")
                    return formatted_results
                    
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error executing query: {str(e)}")
            return None
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an UPDATE, INSERT, or DELETE query.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters
            
        Returns:
            int: Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Set statement timeout
                    cursor.execute("SET statement_timeout = '30s'")
                    
                    # Execute query
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    # Commit transaction
                    conn.commit()
                    
                    affected_rows = cursor.rowcount
                    logger.info(f"Update query executed successfully, affected {affected_rows} rows")
                    return affected_rows
                    
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL error during update: {str(e)}")
            return -1
            
        except Exception as e:
            logger.error(f"Unexpected error executing update: {str(e)}")
            return -1
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Retrieve database schema information for context.
        
        Returns:
            Dict[str, Any]: Schema information including tables and columns
        """
        try:
            schema_info = {
                'tables': {},
                'views': {},
                'total_tables': 0,
                'total_columns': 0
            }
            
            # Get table information
            table_query = """
            SELECT 
                table_name,
                table_type,
                table_schema
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_name;
            """
            
            tables = self.execute_query(table_query)
            if not tables:
                return schema_info
            
            # Get column information for each table
            for table in tables:
                table_name = table['table_name']
                table_type = table['table_type']
                table_schema = table['table_schema']
                
                column_query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = %s
                ORDER BY ordinal_position;
                """
                
                columns = self.execute_query(column_query, (table_name, table_schema))
                
                table_info = {
                    'type': table_type,
                    'schema': table_schema,
                    'columns': columns or [],
                    'column_count': len(columns) if columns else 0
                }
                
                if table_type == 'BASE TABLE':
                    schema_info['tables'][table_name] = table_info
                else:
                    schema_info['views'][table_name] = table_info
                
                schema_info['total_columns'] += table_info['column_count']
            
            schema_info['total_tables'] = len(schema_info['tables'])
            logger.info(f"Retrieved schema info for {schema_info['total_tables']} tables")
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Failed to retrieve schema information: {str(e)}")
            return {'error': str(e)}
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample data from a table for context.
        
        Args:
            table_name (str): Name of the table
            limit (int): Number of sample rows to return
            
        Returns:
            List[Dict[str, Any]]: Sample data
        """
        try:
            # Validate table name to prevent SQL injection
            safe_table_name = sql.Identifier(table_name)
            query = sql.SQL("SELECT * FROM {} LIMIT %s").format(safe_table_name)
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (limit,))
                    results = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    
                    return [dict(zip(column_names, row)) for row in results]
                    
        except Exception as e:
            logger.error(f"Failed to get sample data for table {table_name}: {str(e)}")
            return []
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics data for the dashboard.
        
        Returns:
            Dict[str, Any]: Analytics data including metrics and chart data
        """
        try:
            analytics = {}
            
            # Get total metrics
            metrics_query = """
            SELECT 
                COUNT(DISTINCT o.order_id) as total_orders,
                COUNT(DISTINCT c.customer_id) as total_customers,
                COALESCE(SUM(o.total_amount), 0) as total_revenue,
                COALESCE(AVG(o.total_amount), 0) as avg_order_value
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status NOT IN ('cancelled', 'returned')
            """
            
            metrics = self.execute_query(metrics_query)
            if metrics and len(metrics) > 0:
                analytics.update(metrics[0])
            
            # Get top categories by revenue
            categories_query = """
            SELECT 
                p.category,
                COUNT(DISTINCT oi.order_id) as orders_count,
                SUM(oi.quantity) as units_sold,
                SUM(oi.total_price) as revenue
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_status NOT IN ('cancelled', 'returned') OR o.order_status IS NULL
            GROUP BY p.category
            ORDER BY revenue DESC NULLS LAST
            LIMIT 5
            """
            
            analytics['topCategories'] = self.execute_query(categories_query) or []
            
            # Get sales by state
            state_query = """
            SELECT 
                c.state,
                COUNT(DISTINCT c.customer_id) as customer_count,
                COALESCE(SUM(o.total_amount), 0) as total_spending,
                COUNT(o.order_id) as total_orders
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status NOT IN ('cancelled', 'returned') OR o.order_status IS NULL
            GROUP BY c.state
            ORDER BY total_spending DESC NULLS LAST
            LIMIT 8
            """
            
            analytics['salesByState'] = self.execute_query(state_query) or []
            
            # Get top customers
            customers_query = """
            SELECT 
                c.first_name || ' ' || c.last_name as customer_name,
                c.city || ', ' || c.state as location,
                COUNT(o.order_id) as total_orders,
                COALESCE(SUM(o.total_amount), 0) as total_spent
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status NOT IN ('cancelled', 'returned') OR o.order_status IS NULL
            GROUP BY c.customer_id, c.first_name, c.last_name, c.city, c.state
            ORDER BY total_spent DESC NULLS LAST
            LIMIT 5
            """
            
            analytics['topCustomers'] = self.execute_query(customers_query) or []
            
            # Get sales trend by year (instead of last 7 days)
            trend_query = """
            SELECT 
                EXTRACT(YEAR FROM o.order_date) as year,
                COUNT(*) as order_count,
                COALESCE(SUM(o.total_amount), 0) as total_sales,
                AVG(o.total_amount) as avg_order_value,
                COUNT(DISTINCT o.customer_id) as unique_customers
            FROM orders o
            WHERE o.order_status NOT IN ('cancelled', 'returned')
            AND o.order_date >= CURRENT_DATE - INTERVAL '5 years'
            GROUP BY EXTRACT(YEAR FROM o.order_date)
            ORDER BY year
            """
            
            analytics['salesTrend'] = self.execute_query(trend_query) or []
            
            # Get order status distribution
            status_query = """
            SELECT 
                order_status,
                COUNT(*) as count,
                SUM(total_amount) as total_amount
            FROM orders
            GROUP BY order_status
            ORDER BY count DESC
            """
            
            analytics['orderStatus'] = self.execute_query(status_query) or []
            
            logger.info("Analytics data retrieved successfully")
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to retrieve analytics data: {str(e)}")
            return {}

    def health_check(self) -> bool:
        """
        Perform a health check on the database connection.
        
        Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            result = self.execute_query("SELECT 1 as health_check")
            return result is not None and len(result) > 0
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    def close_connections(self):
        """Close all connections in the pool."""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                logger.info("All database connections closed")
                
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
    
    def __del__(self):
        """Cleanup connections when object is destroyed."""
        self.close_connections()
