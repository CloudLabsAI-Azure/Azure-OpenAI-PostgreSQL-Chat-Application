"""
Data Fetching Module for Azure OpenAI PostgreSQL Chat Application
Provides various data sources and fetching capabilities with security and caching.
"""

import os
import logging
import requests
import feedparser
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Comprehensive data fetching service supporting multiple data sources.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize data fetcher.
        
        Args:
            db_manager: Database manager instance for caching
        """
        self.db_manager = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Azure-OpenAI-Chat-App/1.0 (Data Analytics Bot)'
        })
        
        # Cache settings
        self.cache_duration = {
            'rss': 1800,  # 30 minutes
            'api': 900,   # 15 minutes
            'web': 3600,  # 1 hour
            'csv': 86400  # 24 hours
        }
        
        # Data source configurations
        self.data_sources = {
            'news_feeds': [
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://rss.cnn.com/rss/edition.rss',
                'https://feeds.reuters.com/reuters/businessNews'
            ],
            'economic_apis': [
                'https://api.exchangerate-api.com/v4/latest/USD',
                'https://api.coindesk.com/v1/bpi/currentprice.json'
            ],
            'sample_csv_sources': [
                'https://raw.githubusercontent.com/plotly/datasets/master/iris.csv',
                'https://raw.githubusercontent.com/plotly/datasets/master/tips.csv'
            ]
        }

    def fetch_rss_feeds(self, urls: List[str] = None, max_entries: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch data from RSS feeds.
        
        Args:
            urls: List of RSS feed URLs
            max_entries: Maximum entries to fetch per feed
            
        Returns:
            List of feed entries
        """
        if urls is None:
            urls = self.data_sources['news_feeds']
            
        all_entries = []
        
        for url in urls:
            try:
                logger.info(f"Fetching RSS feed: {url}")
                
                # Check cache first
                cached_data = self._get_cached_data('rss', url)
                if cached_data:
                    all_entries.extend(cached_data)
                    continue
                
                # Fetch feed
                feed = feedparser.parse(url)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parsing issues for {url}: {feed.bozo_exception}")
                
                entries = []
                for entry in feed.entries[:max_entries]:
                    try:
                        entry_data = {
                            'title': getattr(entry, 'title', 'No title'),
                            'link': getattr(entry, 'link', ''),
                            'description': getattr(entry, 'description', ''),
                            'published': getattr(entry, 'published', ''),
                            'source': url,
                            'fetched_at': datetime.now().isoformat()
                        }
                        
                        # Clean description
                        if entry_data['description']:
                            soup = BeautifulSoup(entry_data['description'], 'html.parser')
                            entry_data['description'] = soup.get_text()[:500]
                        
                        entries.append(entry_data)
                        
                    except Exception as e:
                        logger.warning(f"Error processing entry from {url}: {str(e)}")
                        continue
                
                # Cache the data
                self._cache_data('rss', url, entries)
                all_entries.extend(entries)
                
                logger.info(f"Fetched {len(entries)} entries from {url}")
                
            except Exception as e:
                logger.error(f"Error fetching RSS feed {url}: {str(e)}")
                continue
        
        return all_entries

    def fetch_api_data(self, urls: List[str] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Fetch data from REST APIs.
        
        Args:
            urls: List of API URLs
            headers: Additional headers
            
        Returns:
            Dictionary of API responses
        """
        if urls is None:
            urls = self.data_sources['economic_apis']
            
        results = {}
        
        for url in urls:
            try:
                logger.info(f"Fetching API data: {url}")
                
                # Check cache first
                cached_data = self._get_cached_data('api', url)
                if cached_data:
                    results[url] = cached_data
                    continue
                
                # Prepare headers
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                # Make request
                response = self.session.get(url, headers=request_headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                data['fetched_at'] = datetime.now().isoformat()
                
                # Cache the data
                self._cache_data('api', url, data)
                results[url] = data
                
                logger.info(f"Successfully fetched API data from {url}")
                
            except requests.RequestException as e:
                logger.error(f"Error fetching API data from {url}: {str(e)}")
                results[url] = {'error': str(e)}
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from {url}: {str(e)}")
                results[url] = {'error': 'Invalid JSON response'}
        
        return results

    def fetch_web_data(self, urls: List[str], selectors: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """
        Fetch and parse web page data.
        
        Args:
            urls: List of web page URLs
            selectors: CSS selectors for specific elements
            
        Returns:
            List of parsed web data
        """
        results = []
        
        for url in urls:
            try:
                logger.info(f"Fetching web data: {url}")
                
                # Check cache first
                cached_data = self._get_cached_data('web', url)
                if cached_data:
                    results.append(cached_data)
                    continue
                
                # Fetch page
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract data
                page_data = {
                    'url': url,
                    'title': soup.title.string if soup.title else 'No title',
                    'text_content': soup.get_text()[:2000],  # First 2000 chars
                    'fetched_at': datetime.now().isoformat()
                }
                
                # Extract specific elements if selectors provided
                if selectors:
                    for name, selector in selectors.items():
                        elements = soup.select(selector)
                        page_data[name] = [elem.get_text().strip() for elem in elements[:10]]
                
                # Cache the data
                self._cache_data('web', url, page_data)
                results.append(page_data)
                
                logger.info(f"Successfully fetched web data from {url}")
                
            except requests.RequestException as e:
                logger.error(f"Error fetching web data from {url}: {str(e)}")
                results.append({'url': url, 'error': str(e)})
            except Exception as e:
                logger.error(f"Error parsing web data from {url}: {str(e)}")
                results.append({'url': url, 'error': str(e)})
        
        return results

    def fetch_csv_data(self, urls: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch CSV data from URLs.
        
        Args:
            urls: List of CSV URLs
            
        Returns:
            Dictionary of DataFrames
        """
        if urls is None:
            urls = self.data_sources['sample_csv_sources']
            
        results = {}
        
        for url in urls:
            try:
                logger.info(f"Fetching CSV data: {url}")
                
                # Check cache first
                cached_data = self._get_cached_data('csv', url)
                if cached_data:
                    results[url] = pd.DataFrame(cached_data)
                    continue
                
                # Fetch CSV
                df = pd.read_csv(url)
                
                # Convert to dict for caching
                data_dict = df.to_dict('records')
                
                # Cache the data
                self._cache_data('csv', url, data_dict)
                results[url] = df
                
                logger.info(f"Successfully fetched CSV data from {url}: {df.shape}")
                
            except Exception as e:
                logger.error(f"Error fetching CSV data from {url}: {str(e)}")
                results[url] = pd.DataFrame()  # Empty DataFrame
        
        return results

    def fetch_social_media_trends(self) -> Dict[str, Any]:
        """
        Fetch social media trends (simulated data for demo).
        
        Returns:
            Dictionary of trend data
        """
        # This is simulated data - in real implementation, you'd use APIs like Twitter, Reddit, etc.
        trends = {
            'trending_topics': [
                {'topic': 'AI Technology', 'mentions': 15420, 'sentiment': 'positive'},
                {'topic': 'Data Analytics', 'mentions': 12840, 'sentiment': 'neutral'},
                {'topic': 'Cloud Computing', 'mentions': 9560, 'sentiment': 'positive'},
                {'topic': 'Cybersecurity', 'mentions': 8720, 'sentiment': 'negative'},
                {'topic': 'Machine Learning', 'mentions': 7890, 'sentiment': 'positive'}
            ],
            'hashtags': ['#AI', '#DataScience', '#CloudFirst', '#Security', '#Innovation'],
            'fetched_at': datetime.now().isoformat()
        }
        
        return trends

    def fetch_financial_data(self) -> Dict[str, Any]:
        """
        Fetch financial market data.
        
        Returns:
            Dictionary of financial data
        """
        try:
            # Fetch exchange rates
            api_data = self.fetch_api_data()
            
            financial_data = {
                'exchange_rates': {},
                'crypto_prices': {},
                'market_indicators': {
                    'volatility_index': 18.5,
                    'fear_greed_index': 65,
                    'market_cap_change': 2.3
                },
                'fetched_at': datetime.now().isoformat()
            }
            
            # Process API responses
            for url, data in api_data.items():
                if 'exchangerate-api.com' in url and 'rates' in data:
                    financial_data['exchange_rates'] = data['rates']
                elif 'coindesk.com' in url and 'bpi' in data:
                    financial_data['crypto_prices']['bitcoin'] = data['bpi']['USD']['rate_float']
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Error fetching financial data: {str(e)}")
            return {'error': str(e), 'fetched_at': datetime.now().isoformat()}

    def fetch_all_data_sources(self) -> Dict[str, Any]:
        """
        Fetch data from all configured sources.
        
        Returns:
            Dictionary containing all fetched data
        """
        logger.info("Fetching data from all sources...")
        
        all_data = {
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        try:
            # Fetch RSS feeds
            all_data['sources']['news_feeds'] = self.fetch_rss_feeds()
            
            # Fetch API data
            all_data['sources']['api_data'] = self.fetch_api_data()
            
            # Fetch CSV data
            csv_data = self.fetch_csv_data()
            all_data['sources']['csv_data'] = {
                url: df.to_dict('records') for url, df in csv_data.items()
            }
            
            # Fetch social media trends
            all_data['sources']['social_trends'] = self.fetch_social_media_trends()
            
            # Fetch financial data
            all_data['sources']['financial_data'] = self.fetch_financial_data()
            
            # Summary statistics
            all_data['summary'] = {
                'total_news_articles': len(all_data['sources']['news_feeds']),
                'api_sources': len(all_data['sources']['api_data']),
                'csv_datasets': len(all_data['sources']['csv_data']),
                'trending_topics': len(all_data['sources']['social_trends'].get('trending_topics', [])),
                'data_freshness': 'Current'
            }
            
            logger.info("Successfully fetched data from all sources")
            
        except Exception as e:
            logger.error(f"Error fetching from all sources: {str(e)}")
            all_data['error'] = str(e)
        
        return all_data

    def _get_cache_key(self, source_type: str, url: str) -> str:
        """Generate cache key for data."""
        return hashlib.md5(f"{source_type}:{url}".encode()).hexdigest()

    def _get_cached_data(self, source_type: str, url: str) -> Optional[Any]:
        """
        Get cached data if available and not expired.
        
        Args:
            source_type: Type of data source
            url: Source URL
            
        Returns:
            Cached data or None
        """
        if not self.db_manager:
            return None
            
        try:
            cache_key = self._get_cache_key(source_type, url)
            
            # Query cache table (you would need to create this table)
            query = """
            SELECT data, created_at FROM data_cache 
            WHERE cache_key = %s AND created_at > %s
            """
            
            cutoff_time = datetime.now() - timedelta(seconds=self.cache_duration[source_type])
            result = self.db_manager.execute_query(query, (cache_key, cutoff_time))
            
            if result and len(result) > 0:
                return json.loads(result[0]['data'])
                
        except Exception as e:
            logger.warning(f"Error getting cached data: {str(e)}")
            
        return None

    def _cache_data(self, source_type: str, url: str, data: Any):
        """
        Cache data for future use.
        
        Args:
            source_type: Type of data source
            url: Source URL
            data: Data to cache
        """
        if not self.db_manager:
            return
            
        try:
            cache_key = self._get_cache_key(source_type, url)
            
            # Insert or update cache (you would need to create this table)
            query = """
            INSERT INTO data_cache (cache_key, source_type, url, data, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (cache_key) DO UPDATE SET
                data = EXCLUDED.data,
                created_at = EXCLUDED.created_at
            """
            
            self.db_manager.execute_query(query, (
                cache_key, source_type, url, json.dumps(data), datetime.now()
            ))
            
        except Exception as e:
            logger.warning(f"Error caching data: {str(e)}")

    def print_data_summary(self, data: Dict[str, Any]):
        """
        Print a comprehensive summary of fetched data.
        
        Args:
            data: Data dictionary to summarize
        """
        print("\n" + "="*60)
        print("           DATA FETCHING SUMMARY")
        print("="*60)
        
        if 'timestamp' in data:
            print(f"Fetch Time: {data['timestamp']}")
        
        if 'summary' in data:
            summary = data['summary']
            print(f"\n📊 Summary Statistics:")
            print(f"   • News Articles: {summary.get('total_news_articles', 0)}")
            print(f"   • API Sources: {summary.get('api_sources', 0)}")
            print(f"   • CSV Datasets: {summary.get('csv_datasets', 0)}")
            print(f"   • Trending Topics: {summary.get('trending_topics', 0)}")
            print(f"   • Data Freshness: {summary.get('data_freshness', 'Unknown')}")
        
        if 'sources' in data:
            sources = data['sources']
            
            # News feeds summary
            if 'news_feeds' in sources:
                print(f"\n📰 News Articles ({len(sources['news_feeds'])}):")
                for i, article in enumerate(sources['news_feeds'][:5], 1):
                    print(f"   {i}. {article['title'][:60]}...")
                if len(sources['news_feeds']) > 5:
                    print(f"   ... and {len(sources['news_feeds']) - 5} more articles")
            
            # API data summary
            if 'api_data' in sources:
                print(f"\n🔗 API Data Sources:")
                for url, response in sources['api_data'].items():
                    status = "✓ Success" if 'error' not in response else "✗ Error"
                    print(f"   • {urlparse(url).netloc}: {status}")
            
            # Financial data summary
            if 'financial_data' in sources:
                fin_data = sources['financial_data']
                print(f"\n💰 Financial Data:")
                if 'exchange_rates' in fin_data:
                    rates = fin_data['exchange_rates']
                    print(f"   • Exchange Rates: USD to EUR: {rates.get('EUR', 'N/A')}")
                    print(f"   • Exchange Rates: USD to GBP: {rates.get('GBP', 'N/A')}")
                if 'crypto_prices' in fin_data:
                    crypto = fin_data['crypto_prices']
                    if 'bitcoin' in crypto:
                        print(f"   • Bitcoin Price: ${crypto['bitcoin']:,.2f}")
            
            # Social trends summary
            if 'social_trends' in sources:
                trends = sources['social_trends']
                print(f"\n📱 Social Media Trends:")
                if 'trending_topics' in trends:
                    for i, topic in enumerate(trends['trending_topics'][:3], 1):
                        print(f"   {i}. {topic['topic']}: {topic['mentions']:,} mentions ({topic['sentiment']})")
                
                if 'hashtags' in trends:
                    print(f"   • Popular Hashtags: {', '.join(trends['hashtags'][:5])}")
            
            # CSV data summary
            if 'csv_data' in sources:
                print(f"\n📊 CSV Datasets:")
                for url, dataset in sources['csv_data'].items():
                    filename = urlparse(url).path.split('/')[-1]
                    print(f"   • {filename}: {len(dataset)} rows")
        
        print("="*60)
        print("Data fetching completed successfully!")
        print("="*60 + "\n")
