"""
Azure OpenAI Service for natural language to SQL conversion and result interpretation.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
import time
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from openai import AzureOpenAI
import re

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service for interacting with Azure OpenAI to convert between natural language and SQL.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client with managed identity authentication."""
        self.endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        self.api_version = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-02-01')
        self.deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        if not all([self.endpoint, self.deployment_name]):
            raise ValueError("Azure OpenAI configuration is incomplete. Check environment variables.")
        
        # Use managed identity for authentication in Azure environments
        # Falls back to other credential types for local development
        try:
            # For local development, use API key if available
            api_key = os.environ.get('AZURE_OPENAI_API_KEY')
            if api_key:
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=api_key,
                    api_version=self.api_version
                )
                logger.info("Azure OpenAI client initialized with API key")
            else:
                # Use managed identity for Azure environments
                credential = DefaultAzureCredential()
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_version=self.api_version,
                    azure_ad_token_provider=lambda: credential.get_token("https://cognitiveservices.azure.com/.default").token
                )
                logger.info("Azure OpenAI client initialized with managed identity")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            raise
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    def natural_language_to_sql(self, user_question: str, schema_context: Optional[Dict] = None) -> Optional[str]:
        """
        Convert natural language question to SQL query using Azure OpenAI.
        
        Args:
            user_question (str): User's natural language question
            schema_context (Dict, optional): Database schema information for context
            
        Returns:
            str: Generated SQL query, or None if generation failed
        """
        try:
            # Build the system prompt with schema context
            system_prompt = self._build_sql_generation_prompt(schema_context)
            
            # Build user prompt
            user_prompt = f"""
            Convert this natural language question to a SQL query:
            "{user_question}"
            
            Requirements:
            - Return only the SQL query, no explanations
            - Use proper PostgreSQL syntax
            - Include appropriate WHERE clauses for filtering
            - Use JOINs when multiple tables are needed
            - Limit results to 100 rows maximum for performance
            - Use ILIKE for case-insensitive text matching
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call Azure OpenAI with retry logic
            response = self._call_openai_with_retry(messages, max_tokens=500)
            
            if response:
                sql_query = self._extract_sql_from_response(response)
                logger.info(f"Generated SQL query: {sql_query}")
                return sql_query
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating SQL from natural language: {str(e)}")
            return None
    
    def sql_results_to_natural_language(self, original_question: str, sql_query: str, 
                                      results: List[Dict[str, Any]]) -> str:
        """
        Convert SQL query results back to natural language response.
        
        Args:
            original_question (str): Original user question
            sql_query (str): Executed SQL query
            results (List[Dict]): Query results
            
        Returns:
            str: Natural language interpretation of results
        """
        try:
            # Prepare results summary
            result_count = len(results)
            
            if result_count == 0:
                return "I didn't find any results matching your question. You might want to try rephrasing your query or check if the data exists."
            
            # Sample first few results for context
            sample_results = results[:5] if result_count > 5 else results
            
            system_prompt = """
            You are a helpful assistant that explains database query results in natural language.
            Convert the SQL query results into a conversational, easy-to-understand response.
            
            Guidelines:
            - Be conversational and friendly
            - Summarize the data clearly
            - Mention the number of results found
            - Highlight key insights or patterns
            - If there are many results, focus on the most important ones
            - Use bullet points or numbered lists when appropriate
            - Don't include technical SQL details in the response
            """
            
            user_prompt = f"""
            Original question: "{original_question}"
            SQL query executed: {sql_query}
            Number of results: {result_count}
            Sample results (first 5): {json.dumps(sample_results, indent=2, default=str)}
            
            Please provide a natural language explanation of these results that directly answers the user's question.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self._call_openai_with_retry(messages, max_tokens=800)
            
            if response:
                return response.strip()
            else:
                return f"Found {result_count} results, but I had trouble explaining them. Here's a summary of the data: {str(sample_results)}"
                
        except Exception as e:
            logger.error(f"Error converting results to natural language: {str(e)}")
            return f"Found {len(results)} results, but encountered an error while explaining them."
    
    def _build_sql_generation_prompt(self, schema_context: Optional[Dict] = None) -> str:
        """
        Build system prompt for SQL generation with schema context.
        
        Args:
            schema_context (Dict, optional): Database schema information
            
        Returns:
            str: System prompt for SQL generation
        """
        base_prompt = """
        You are an expert SQL query generator for PostgreSQL databases.
        Convert natural language questions into accurate, efficient SQL queries.
        
        This is an e-commerce database with the following tables:
        - customers: customer information (customer_id, first_name, last_name, email, phone, address, city, state, country, postal_code)
        - products: product catalog (product_id, product_name, description, category, price, stock_quantity, is_active)
        - orders: customer orders (order_id, customer_id, order_date, total_amount, order_status, shipping_address)
        - order_items: items within orders (order_item_id, order_id, product_id, quantity, unit_price, total_price)
        
        Guidelines:
        - Generate only SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
        - Use PostgreSQL-specific syntax and functions
        - Always include LIMIT clause (max 100 rows) for performance
        - Use proper JOIN syntax when multiple tables are involved
        - Use ILIKE for case-insensitive text matching
        - Handle date/time queries appropriately
        - Use aggregate functions (COUNT, SUM, AVG) when appropriate
        - Include proper WHERE clauses for filtering
        - For customer queries, use the customers table
        - For product queries, use the products table
        - For order queries, join orders with customers and/or order_items as needed
        """
        
        if schema_context and 'tables' in schema_context:
            schema_info = "\n\nAvailable database schema:\n"
            for table_name, table_info in schema_context['tables'].items():
                schema_info += f"\nTable: {table_name}\n"
                schema_info += "Columns:\n"
                for column in table_info.get('columns', []):
                    col_name = column.get('column_name', '')
                    col_type = column.get('data_type', '')
                    nullable = column.get('is_nullable', '')
                    schema_info += f"  - {col_name} ({col_type}, nullable: {nullable})\n"
            
            return base_prompt + schema_info
        
        return base_prompt
    
    def _call_openai_with_retry(self, messages: List[Dict], max_tokens: int = 1000) -> Optional[str]:
        """
        Call Azure OpenAI with retry logic for resilience.
        
        Args:
            messages (List[Dict]): Chat messages
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: Generated response, or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.1,  # Low temperature for consistent SQL generation
                    top_p=0.9,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                if response.choices and len(response.choices) > 0:
                    return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"OpenAI API call attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    sleep_time = self.retry_delay * (2 ** attempt)
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All OpenAI API call attempts failed: {str(e)}")
        
        return None
    
    def _extract_sql_from_response(self, response: str) -> Optional[str]:
        """
        Extract SQL query from OpenAI response, handling various formats.
        
        Args:
            response (str): Raw response from OpenAI
            
        Returns:
            str: Cleaned SQL query
        """
        try:
            # Remove markdown code blocks if present
            sql_pattern = r'```(?:sql)?\s*(.*?)\s*```'
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            
            if match:
                sql_query = match.group(1).strip()
            else:
                # If no code blocks, use the entire response
                sql_query = response.strip()
            
            # Clean up the SQL query
            sql_query = sql_query.strip(';').strip()
            
            # Basic validation - must start with SELECT
            if not sql_query.upper().startswith('SELECT'):
                logger.warning(f"Generated query doesn't start with SELECT: {sql_query}")
                return None
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error extracting SQL from response: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """
        Perform a health check on the Azure OpenAI service.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            test_messages = [
                {"role": "user", "content": "Return the word 'healthy' if you can read this message."}
            ]
            
            response = self._call_openai_with_retry(test_messages, max_tokens=10)
            return response is not None and 'healthy' in response.lower()
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return False
