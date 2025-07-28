"""
Utility functions for input validation, SQL sanitization, and response formatting.
"""

import re
import logging
from typing import List, Dict, Any, Optional
import sqlparse
from sqlparse import sql, tokens

logger = logging.getLogger(__name__)

def validate_input(user_input: str) -> bool:
    """
    Validate user input for basic security and format checks.
    
    Args:
        user_input (str): User's input message
        
    Returns:
        bool: True if input is valid, False otherwise
    """
    if not user_input or not isinstance(user_input, str):
        return False
    
    # Remove whitespace and check length
    cleaned_input = user_input.strip()
    if len(cleaned_input) == 0 or len(cleaned_input) > 1000:
        return False
    
    # Check for obviously malicious patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # XSS attempts
        r'javascript:',                # JavaScript URLs
        r'vbscript:',                 # VBScript URLs
        r'on\w+\s*=',                 # Event handlers
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, cleaned_input, re.IGNORECASE):
            logger.warning(f"Potentially dangerous input detected: {pattern}")
            return False
    
    return True

def sanitize_sql(sql_query: str) -> Optional[str]:
    """
    Sanitize and validate SQL query for security.
    
    Args:
        sql_query (str): SQL query to sanitize
        
    Returns:
        str: Sanitized SQL query, or None if unsafe
    """
    if not sql_query:
        return None
    
    try:
        # Parse the SQL query
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            return None
        
        statement = parsed[0]
        
        # Check if it's a SELECT statement
        if not _is_select_statement(statement):
            logger.warning("Non-SELECT statement detected")
            return None
        
        # Check for dangerous keywords
        if _contains_dangerous_keywords(sql_query):
            logger.warning("Dangerous keywords detected in SQL")
            return None
        
        # Format and clean the SQL
        formatted_sql = sqlparse.format(
            sql_query,
            reindent=True,
            keyword_case='upper',
            identifier_case='lower',
            strip_comments=True
        )
        
        # Add LIMIT if not present (safety measure)
        formatted_sql = _ensure_limit_clause(formatted_sql)
        
        return formatted_sql.strip()
        
    except Exception as e:
        logger.error(f"Error sanitizing SQL: {str(e)}")
        return None

def _is_select_statement(statement) -> bool:
    """
    Check if the parsed statement is a SELECT statement.
    
    Args:
        statement: Parsed SQL statement
        
    Returns:
        bool: True if SELECT statement, False otherwise
    """
    try:
        first_token = None
        for token in statement.flatten():
            if token.ttype not in (tokens.Whitespace, tokens.Comment.Single, tokens.Comment.Multiline):
                first_token = token
                break
        
        return first_token and first_token.value.upper() == 'SELECT'
        
    except Exception:
        return False

def _contains_dangerous_keywords(sql_query: str) -> bool:
    """
    Check for dangerous SQL keywords that shouldn't be in read-only queries.
    
    Args:
        sql_query (str): SQL query to check
        
    Returns:
        bool: True if dangerous keywords found, False otherwise
    """
    dangerous_keywords = [
        r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b',
        r'\bCREATE\b', r'\bALTER\b', r'\bTRUNCATE\b', r'\bEXEC\b',
        r'\bEXECUTE\b', r'\bCALL\b', r'\bMERGE\b', r'\bGRANT\b',
        r'\bREVOKE\b', r'\bCOMMIT\b', r'\bROLLBACK\b', r'\bSAVEPOINT\b',
        r'\bLOCK\b', r'\bUNLOCK\b', r'\bSET\b', r'\bRESET\b',
        r'\bSHOW\b', r'\bDESCRIBE\b', r'\bEXPLAIN\b', r'\bANALYZE\b'
    ]
    
    for keyword in dangerous_keywords:
        if re.search(keyword, sql_query, re.IGNORECASE):
            return True
    
    return False

def _ensure_limit_clause(sql_query: str) -> str:
    """
    Ensure SQL query has a LIMIT clause for performance and safety.
    
    Args:
        sql_query (str): SQL query
        
    Returns:
        str: SQL query with LIMIT clause
    """
    # Check if LIMIT already exists
    if re.search(r'\bLIMIT\s+\d+', sql_query, re.IGNORECASE):
        return sql_query
    
    # Add LIMIT clause
    return f"{sql_query.rstrip(';')} LIMIT 100"

def format_response(user_message: str, sql_query: str, results: List[Dict[str, Any]], 
                   natural_response: str) -> str:
    """
    Format the complete response for the user interface.
    
    Args:
        user_message (str): Original user question
        sql_query (str): Generated SQL query
        results (List[Dict]): Query results
        natural_response (str): Natural language interpretation
        
    Returns:
        str: Formatted response
    """
    try:
        result_count = len(results)
        
        # Start with the natural language response
        formatted_response = natural_response
        
        # Add result summary if helpful
        if result_count > 5:
            formatted_response += f"\n\n📊 **Summary**: Found {result_count} total results."
        
        # Add sample data if results exist and are structured
        if results and len(results) > 0:
            # Check if results are simple enough to display
            first_result = results[0]
            if len(first_result) <= 5 and all(len(str(v)) < 100 for v in first_result.values()):
                formatted_response += "\n\n**Sample data:**\n"
                
                # Display first few results in a readable format
                display_count = min(3, len(results))
                for i, result in enumerate(results[:display_count]):
                    formatted_response += f"\n{i+1}. "
                    formatted_items = []
                    for key, value in result.items():
                        formatted_items.append(f"{key}: {value}")
                    formatted_response += ", ".join(formatted_items)
                
                if result_count > display_count:
                    formatted_response += f"\n... and {result_count - display_count} more results"
        
        return formatted_response
        
    except Exception as e:
        logger.error(f"Error formatting response: {str(e)}")
        return natural_response

def clean_text(text: str) -> str:
    """
    Clean text input for safe processing.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove null bytes
    cleaned = cleaned.replace('\x00', '')
    
    # Limit length
    if len(cleaned) > 2000:
        cleaned = cleaned[:2000] + "..."
    
    return cleaned

def extract_table_names_from_sql(sql_query: str) -> List[str]:
    """
    Extract table names from a SQL query for logging and validation.
    
    Args:
        sql_query (str): SQL query
        
    Returns:
        List[str]: List of table names found in the query
    """
    try:
        # Simple regex to find table names after FROM and JOIN
        table_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(table_pattern, sql_query, re.IGNORECASE)
        
        # Remove duplicates and return
        return list(set(matches))
        
    except Exception as e:
        logger.error(f"Error extracting table names: {str(e)}")
        return []

def estimate_query_complexity(sql_query: str) -> str:
    """
    Estimate the complexity of a SQL query for performance monitoring.
    
    Args:
        sql_query (str): SQL query
        
    Returns:
        str: Complexity level (simple, moderate, complex)
    """
    try:
        query_upper = sql_query.upper()
        
        # Count complexity indicators
        complexity_score = 0
        
        # JOINs increase complexity
        complexity_score += len(re.findall(r'\bJOIN\b', query_upper))
        
        # Subqueries increase complexity
        complexity_score += len(re.findall(r'\(\s*SELECT\b', query_upper))
        
        # Aggregate functions
        complexity_score += len(re.findall(r'\b(COUNT|SUM|AVG|MIN|MAX|GROUP_CONCAT)\s*\(', query_upper))
        
        # GROUP BY and ORDER BY
        if 'GROUP BY' in query_upper:
            complexity_score += 1
        if 'ORDER BY' in query_upper:
            complexity_score += 1
        
        # Window functions
        complexity_score += len(re.findall(r'\bOVER\s*\(', query_upper))
        
        # CTEs (Common Table Expressions)
        complexity_score += len(re.findall(r'\bWITH\b', query_upper))
        
        # Determine complexity level
        if complexity_score == 0:
            return "simple"
        elif complexity_score <= 3:
            return "moderate"
        else:
            return "complex"
            
    except Exception as e:
        logger.error(f"Error estimating query complexity: {str(e)}")
        return "unknown"
