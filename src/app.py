"""
Azure OpenAI PostgreSQL Chat Application
Main Flask application that provides a chat interface for natural language database queries.
Enhanced with comprehensive security and data fetching capabilities.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone

from database import DatabaseManager
from openai_service import OpenAIService
from analytics_service import AnalyticsService
from utils import validate_input, sanitize_sql, format_response
from security import SecurityManager, validate_input_security, security_manager
from data_fetcher import DataFetcher

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the parent directory for templates and static files
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(parent_dir, 'templates')
static_dir = os.path.join(parent_dir, 'static')

# Initialize Flask app with security
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Security configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', str(uuid.uuid4()))
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize security extensions
CORS(app, origins=['http://localhost:5000', 'https://your-domain.com'])

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Security headers
talisman = Talisman(
    app,
    force_https=False,  # Set to True in production
    strict_transport_security=False,  # Set to True in production
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://cdn.plot.ly",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
        'connect-src': "'self'"
    }
)

# Initialize services
db_manager = DatabaseManager()
openai_service = OpenAIService()
analytics_service = AnalyticsService(db_manager)
data_fetcher = DataFetcher(db_manager)

@app.route('/')
def index():
    """Render the main chat interface."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages and process natural language queries.
    
    Returns:
        JSON response with SQL query, results, and natural language response
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        # Validate input
        if not validate_input(user_message):
            return jsonify({
                'error': 'Invalid input. Please provide a valid question.',
                'status': 'error'
            }), 400
        
        session_id = session.get('session_id')
        logger.info(f"Processing query for session {session_id}: {user_message}")
        
        # Step 1: Get database schema for context
        schema_context = db_manager.get_schema_info()
        
        # Step 2: Convert natural language to SQL using Azure OpenAI with schema context
        logger.info("Converting natural language to SQL...")
        sql_query = openai_service.natural_language_to_sql(user_message, schema_context)
        
        if not sql_query:
            return jsonify({
                'error': 'Unable to generate SQL query from your question.',
                'status': 'error'
            }), 400
        
        # Step 2: Validate and sanitize the generated SQL
        sanitized_sql = sanitize_sql(sql_query)
        if not sanitized_sql:
            return jsonify({
                'error': 'Generated SQL query contains potentially harmful operations.',
                'status': 'error'
            }), 400
        
        logger.info(f"Generated SQL: {sanitized_sql}")
        
        # Step 3: Execute SQL query against PostgreSQL
        logger.info("Executing SQL query...")
        query_results = db_manager.execute_query(sanitized_sql)
        
        if query_results is None:
            return jsonify({
                'error': 'Failed to execute database query.',
                'status': 'error'
            }), 500
        
        # Step 4: Convert results back to natural language
        logger.info("Converting results to natural language...")
        natural_response = openai_service.sql_results_to_natural_language(
            user_message, sanitized_sql, query_results
        )
        
        # Step 5: Log the interaction for auditing
        log_interaction(session_id, user_message, sanitized_sql, len(query_results))
        
        # Step 6: Format and return response
        formatted_response = format_response(
            user_message=user_message,
            sql_query=sanitized_sql,
            results=query_results,
            natural_response=natural_response
        )
        
        return jsonify({
            'response': natural_response,  # Only return the natural language response
            'row_count': len(query_results),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred while processing your request.',
            'status': 'error'
        }), 500



@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Get comprehensive analytics data with Python visualizations.
    
    Returns:
        JSON response with enhanced analytics data including charts and insights
    """
    try:
        # Get comprehensive analytics using the enhanced analytics service
        analytics_data = analytics_service.get_comprehensive_analytics()
        
        # Debug logging
        logger.info(f"Analytics data keys: {list(analytics_data.keys()) if analytics_data else 'None'}")
        if analytics_data:
            logger.info(f"Total revenue: {analytics_data.get('total_revenue', 'Not found')}")
            logger.info(f"Total orders: {analytics_data.get('total_orders', 'Not found')}")
            logger.info(f"Total customers: {analytics_data.get('total_customers', 'Not found')}")
            logger.info(f"Avg order value: {analytics_data.get('avg_order_value', 'Not found')}")
        
        return jsonify({
            'analytics': analytics_data,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error retrieving analytics: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to retrieve analytics data.',
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON response with service health status
    """
    try:
        # Check database connection
        db_healthy = db_manager.health_check()
        
        # Check OpenAI service
        openai_healthy = openai_service.health_check()
        
        overall_status = 'healthy' if db_healthy and openai_healthy else 'degraded'
        
        return jsonify({
            'status': overall_status,
            'database': 'healthy' if db_healthy else 'unhealthy',
            'openai': 'healthy' if openai_healthy else 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

def log_interaction(session_id, user_message, sql_query, result_count):
    """
    Log user interactions for auditing and analytics.
    
    Args:
        session_id (str): User session identifier
        user_message (str): Original user question
        sql_query (str): Generated SQL query
        result_count (int): Number of rows returned
    """
    try:
        interaction_data = {
            'session_id': session_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_message': user_message,
            'sql_query': sql_query,
            'result_count': result_count
        }
        
        # Log to application logs
        logger.info(f"Interaction logged: {interaction_data}")
        
        # TODO: Optionally store in database or send to Azure Monitor
        
    except Exception as e:
        logger.error(f"Failed to log interaction: {str(e)}")

@app.route('/api/data/fetch-all', methods=['GET'])
@limiter.limit("10 per minute")
def fetch_all_data():
    """
    Fetch data from all available sources.
    
    Returns:
        JSON response with comprehensive data from multiple sources
    """
    try:
        logger.info("Fetching data from all sources...")
        
        # Fetch data from all sources
        all_data = data_fetcher.fetch_all_data_sources()
        
        # Print summary to console
        data_fetcher.print_data_summary(all_data)
        
        return jsonify({
            'data': all_data,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error fetching all data: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to fetch data from all sources',
            'status': 'error'
        }), 500

@app.route('/api/data/news', methods=['GET'])
@limiter.limit("20 per minute")
def fetch_news_data():
    """
    Fetch news data from RSS feeds.
    
    Returns:
        JSON response with news articles
    """
    try:
        max_entries = request.args.get('max_entries', 20, type=int)
        
        news_data = data_fetcher.fetch_rss_feeds(max_entries=max_entries)
        
        return jsonify({
            'news': news_data,
            'count': len(news_data),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error fetching news data: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to fetch news data',
            'status': 'error'
        }), 500

@app.route('/api/data/financial', methods=['GET'])
@limiter.limit("15 per minute")
def fetch_financial_data_endpoint():
    """
    Fetch financial market data.
    
    Returns:
        JSON response with financial data
    """
    try:
        financial_data = data_fetcher.fetch_financial_data()
        
        return jsonify({
            'financial_data': financial_data,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error fetching financial data: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to fetch financial data',
            'status': 'error'
        }), 500

@app.route('/api/data/social-trends', methods=['GET'])
@limiter.limit("15 per minute")
def fetch_social_trends():
    """
    Fetch social media trends.
    
    Returns:
        JSON response with social trends
    """
    try:
        trends_data = data_fetcher.fetch_social_media_trends()
        
        return jsonify({
            'social_trends': trends_data,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error fetching social trends: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to fetch social trends',
            'status': 'error'
        }), 500

@app.route('/api/security/validate', methods=['POST'])
@limiter.limit("30 per minute")
def validate_input_endpoint():
    """
    Validate user input for security threats.
    
    Returns:
        JSON response with validation results
    """
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({
                'error': 'Input field required',
                'status': 'error'
            }), 400
        
        validation_result = security_manager.validate_input(
            data['input'], 
            max_length=data.get('max_length', 1000)
        )
        
        return jsonify({
            'validation': validation_result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error validating input: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to validate input',
            'status': 'error'
        }), 500

@app.route('/api/data/csv', methods=['GET'])
@limiter.limit("10 per minute")
def fetch_csv_data_endpoint():
    """
    Fetch CSV data from configured sources.
    
    Returns:
        JSON response with CSV data
    """
    try:
        csv_data = data_fetcher.fetch_csv_data()
        
        # Convert DataFrames to JSON-serializable format
        result = {}
        for url, df in csv_data.items():
            if not df.empty:
                result[url] = {
                    'data': df.to_dict('records'),
                    'shape': df.shape,
                    'columns': df.columns.tolist()
                }
            else:
                result[url] = {'error': 'Failed to load data'}
        
        return jsonify({
            'csv_data': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error fetching CSV data: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to fetch CSV data',
            'status': 'error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found', 'status': 'error'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error', 'status': 'error'}), 500

if __name__ == '__main__':
    # Development server configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting Flask application on port {port}, debug={debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )
