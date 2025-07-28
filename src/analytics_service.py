"""
Analytics Service with Python Data Visualization
Provides comprehensive analytics and visualization using matplotlib, seaborn, and plotly.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
import base64
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AnalyticsService:
    """
    Comprehensive analytics service with advanced Python data visualization.
    """
    
    def __init__(self, db_manager):
        """
        Initialize analytics service with database manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.setup_plot_defaults()
    
    def setup_plot_defaults(self):
        """Setup default plot configurations."""
        # Matplotlib defaults
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['font.size'] = 10
        
        # Seaborn defaults
        sns.set_style("whitegrid")
        sns.set_context("notebook", font_scale=1.1)
    
    def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics data with Python visualizations.
        
        Returns:
            Dictionary containing all analytics data and visualizations
        """
        try:
            # Get raw analytics data
            analytics_data = self.db_manager.get_analytics_data()
            
            if not analytics_data:
                logger.warning("No analytics data available, generating enhanced mock data")
                analytics_data = self.generate_enhanced_mock_data()
            
            # Enhance with Python visualizations
            enhanced_analytics = self.enhance_with_visualizations(analytics_data)
            
            logger.info("Comprehensive analytics data generated successfully")
            return enhanced_analytics
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analytics: {str(e)}", exc_info=True)
            return self.generate_enhanced_mock_data()
    
    def enhance_with_visualizations(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance analytics data with Python-generated visualizations.
        
        Args:
            analytics_data: Raw analytics data
            
        Returns:
            Enhanced analytics with visualizations
        """
        enhanced_data = analytics_data.copy()
        
        try:
            # Generate sales trend visualization
            if 'salesTrend' in analytics_data:
                enhanced_data['salesTrendChart'] = self.create_sales_trend_chart(analytics_data['salesTrend'])
            
            # Generate category analysis
            if 'topCategories' in analytics_data:
                enhanced_data['categoryChart'] = self.create_category_chart(analytics_data['topCategories'])
                enhanced_data['categoryAnalysis'] = self.analyze_categories(analytics_data['topCategories'])
            
            # Generate geographical analysis
            if 'salesByState' in analytics_data:
                enhanced_data['geographicalChart'] = self.create_geographical_chart(analytics_data['salesByState'])
                enhanced_data['geographicalAnalysis'] = self.analyze_geographical_data(analytics_data['salesByState'])
            
            # Generate customer analysis
            if 'topCustomers' in analytics_data:
                enhanced_data['customerChart'] = self.create_customer_analysis_chart(analytics_data['topCustomers'])
                enhanced_data['customerAnalysis'] = self.analyze_customer_data(analytics_data['topCustomers'])
            
            # Generate advanced metrics
            enhanced_data['advancedMetrics'] = self.calculate_advanced_metrics(analytics_data)
            
            # Generate predictive insights
            enhanced_data['predictions'] = self.generate_predictions(analytics_data)
            
        except Exception as e:
            logger.error(f"Error enhancing analytics with visualizations: {str(e)}", exc_info=True)
        
        return enhanced_data
    
    def create_sales_trend_chart(self, sales_data: List[Dict]) -> str:
        """Create an interactive yearly sales trend chart using Plotly."""
        try:
            df = pd.DataFrame(sales_data)
            logger.info(f"📊 Creating sales trend chart with {len(df)} data points")
            
            # Handle both date and year formats
            if 'year' in df.columns:
                df['display_date'] = df['year'].astype(str)
                df['year'] = pd.to_numeric(df['year'], errors='coerce')
                x_axis_title = 'Year'
                chart_title = 'Business Growth Trend - 5-Year Performance Overview'
                logger.info(f"📅 Year range: {df['year'].min()} - {df['year'].max()}")
            else:
                # Fallback for date format
                df['date'] = pd.to_datetime(df['date'])
                df['display_date'] = df['date']
                x_axis_title = 'Date'
                chart_title = 'Sales Performance Trend - Daily Overview'
            
            # Convert Decimal types to float and log the data
            if 'total_sales' in df.columns:
                df['total_sales'] = pd.to_numeric(df['total_sales'], errors='coerce').fillna(0)
                logger.info(f"💰 Sales range: ${df['total_sales'].min():,.2f} - ${df['total_sales'].max():,.2f}")
            if 'order_count' in df.columns:
                df['order_count'] = pd.to_numeric(df['order_count'], errors='coerce').fillna(0)
                logger.info(f"📦 Order range: {df['order_count'].min():,} - {df['order_count'].max():,}")
            if 'unique_customers' in df.columns:
                df['unique_customers'] = pd.to_numeric(df['unique_customers'], errors='coerce').fillna(0)
                logger.info(f"👥 Customer range: {df['unique_customers'].min():,} - {df['unique_customers'].max():,}")
            if 'avg_order_value' in df.columns:
                df['avg_order_value'] = pd.to_numeric(df['avg_order_value'], errors='coerce').fillna(0)
            
            # Create Plotly figure with enhanced styling for business dashboard
            fig = go.Figure()
            
            # Add main sales trend line with enhanced styling
            fig.add_trace(go.Scatter(
                x=df['display_date'],
                y=df['total_sales'],
                mode='lines+markers',
                name='Annual Revenue',
                line=dict(color='#0078d4', width=4, shape='spline'),
                marker=dict(size=12, color='#0078d4', symbol='circle'),
                hovertemplate='<b>%{x}</b><br><b>Revenue:</b> $%{y:,.0f}<br><extra></extra>',
                fill='tonexty' if len(df) > 1 else None,
                fillcolor='rgba(0, 120, 212, 0.1)'
            ))
            
            # Add order count on secondary y-axis with business styling
            if 'order_count' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['display_date'],
                    y=df['order_count'],
                    mode='lines+markers',
                    name='Order Volume',
                    yaxis='y2',
                    line=dict(color='#ff6b35', width=3, shape='spline'),
                    marker=dict(size=10, color='#ff6b35', symbol='diamond'),
                    hovertemplate='<b>%{x}</b><br><b>Orders:</b> %{y:,}<extra></extra>'
                ))
            
            # Add customer count trend
            if 'unique_customers' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['display_date'],
                    y=df['unique_customers'],
                    mode='lines+markers',
                    name='Customer Base',
                    yaxis='y3',
                    line=dict(color='#28a745', width=2, dash='dash', shape='spline'),
                    marker=dict(size=8, color='#28a745', symbol='triangle-up'),
                    hovertemplate='<b>%{x}</b><br><b>Customers:</b> %{y:,}<extra></extra>'
                ))
            
            # Calculate and add growth indicators for yearly data
            growth_annotations = []
            if 'year' in df.columns and len(df) > 1:
                logger.info("📈 Calculating year-over-year growth indicators...")
                for i in range(1, len(df)):
                    current_sales = df.iloc[i]['total_sales']
                    prev_sales = df.iloc[i-1]['total_sales']
                    if prev_sales > 0:
                        growth_rate = ((current_sales - prev_sales) / prev_sales) * 100
                        year = df.iloc[i]['display_date']
                        logger.info(f"   {year}: {growth_rate:+.1f}% growth")
                        
                        if abs(growth_rate) > 3:  # Show growth/decline over 3%
                            growth_annotations.append(dict(
                                x=df.iloc[i]['display_date'],
                                y=current_sales,
                                text=f"{growth_rate:+.0f}%",
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1.2,
                                arrowwidth=2,
                                arrowcolor='#28a745' if growth_rate > 0 else '#dc3545',
                                ax=0,
                                ay=-40 if growth_rate > 0 else 40,
                                font=dict(size=11, color='#28a745' if growth_rate > 0 else '#dc3545', weight='bold'),
                                bgcolor='white',
                                bordercolor='#28a745' if growth_rate > 0 else '#dc3545',
                                borderwidth=1
                            ))
            
            # Enhanced layout with business dashboard styling
            fig.update_layout(
                title=dict(
                    text=chart_title,
                    font=dict(size=20, color='#323130', family='Segoe UI'),
                    x=0.5,
                    pad=dict(t=20)
                ),
                xaxis=dict(
                    title=x_axis_title,
                    gridcolor='#f8f9fa',
                    title_font=dict(size=14, color='#495057'),
                    tickfont=dict(size=12, color='#495057'),
                    showline=True,
                    linecolor='#dee2e6',
                    mirror=True
                ),
                yaxis=dict(
                    title='Annual Revenue ($)',
                    gridcolor='#f8f9fa',
                    title_font=dict(size=14, color='#0078d4'),
                    tickfont=dict(size=12, color='#0078d4'),
                    tickformat='$,.0f',
                    showline=True,
                    linecolor='#0078d4',
                    mirror=True
                ),
                yaxis2=dict(
                    title='Order Volume',
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    title_font=dict(size=12, color='#ff6b35'),
                    tickfont=dict(size=10, color='#ff6b35'),
                    showline=True,
                    linecolor='#ff6b35'
                ) if 'order_count' in df.columns else None,
                yaxis3=dict(
                    title='Customers',
                    overlaying='y',
                    side='right',
                    position=0.94,
                    showgrid=False,
                    title_font=dict(size=10, color='#28a745'),
                    tickfont=dict(size=9, color='#28a745'),
                    showline=True,
                    linecolor='#28a745'
                ) if 'unique_customers' in df.columns else None,
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=380,
                margin=dict(l=90, r=120, t=100, b=70),
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='#dee2e6',
                    borderwidth=1
                ),
                annotations=growth_annotations,
                font=dict(family='Segoe UI, sans-serif')
            )
            
            # Return the chart as JSON
            chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
            logger.info(f"✅ Sales trend chart created successfully with {len(growth_annotations)} growth indicators")
            return chart_json
            
        except Exception as e:
            logger.error(f"❌ Error creating sales trend chart: {str(e)}")
            logger.error(f"Sales data provided: {sales_data}")
            # Return a simple fallback chart structure
            fallback_chart = {
                "data": [{"x": [], "y": [], "type": "scatter", "mode": "lines+markers", "name": "Revenue"}],
                "layout": {"title": "Sales Trend - Data Loading...", "height": 380}
            }
            return json.dumps(fallback_chart)
    
    def create_category_chart(self, category_data: List[Dict]) -> str:
        """Create an interactive category performance chart."""
        try:
            df = pd.DataFrame(category_data)
            
            # Convert Decimal types to float
            if 'revenue' in df.columns:
                df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
            if 'orders_count' in df.columns:
                df['orders_count'] = pd.to_numeric(df['orders_count'], errors='coerce').fillna(0)
            
            # Create horizontal bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=df['category'],
                x=df['revenue'],
                orientation='h',
                marker=dict(
                    color=df['revenue'],
                    colorscale='Blues',
                    colorbar=dict(title="Revenue ($)")
                ),
                text=[f"${rev:,.0f}" for rev in df['revenue']],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<br>Orders: %{customdata}<extra></extra>',
                customdata=df['orders_count'] if 'orders_count' in df.columns else None
            ))
            
            fig.update_layout(
                title=dict(
                    text='Top Categories by Revenue',
                    font=dict(size=16, color='#323130')
                ),
                xaxis=dict(title='Revenue ($)', gridcolor='#f3f2f1'),
                yaxis=dict(title='Categories'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=300,
                margin=dict(l=100, r=50, t=50, b=50)
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error creating category chart: {str(e)}")
            return "{}"
    
    def create_geographical_chart(self, state_data: List[Dict]) -> str:
        """Create an interactive geographical sales chart."""
        try:
            df = pd.DataFrame(state_data)
            
            # Create bubble chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=list(range(len(df))),
                y=df['total_spending'],
                mode='markers+text',
                marker=dict(
                    size=df['customer_count'],
                    sizemode='diameter',
                    sizeref=2.*max(df['customer_count'])/(40.**2),
                    sizemin=4,
                    color=df['total_spending'],
                    colorscale='Viridis',
                    colorbar=dict(title="Spending ($)")
                ),
                text=df['state'],
                textposition="middle center",
                textfont=dict(color='white', size=10),
                hovertemplate='<b>%{text}</b><br>Total Spending: $%{y:,.2f}<br>Customers: %{marker.size}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text='Sales Performance by State',
                    font=dict(size=16, color='#323130')
                ),
                xaxis=dict(
                    title='States (Ranked by Performance)',
                    showticklabels=False,
                    gridcolor='#f3f2f1'
                ),
                yaxis=dict(title='Total Spending ($)', gridcolor='#f3f2f1'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=300,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error creating geographical chart: {str(e)}")
            return "{}"
    
    def create_customer_analysis_chart(self, customer_data: List[Dict]) -> str:
        """Create customer analysis visualization."""
        try:
            df = pd.DataFrame(customer_data)
            
            # Create scatter plot showing spending vs orders
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['total_orders'],
                y=df['total_spent'],
                mode='markers+text',
                marker=dict(
                    size=12,
                    color='#0078d4',
                    opacity=0.7
                ),
                text=df['customer_name'],
                textposition="top center",
                hovertemplate='<b>%{text}</b><br>Total Spent: $%{y:,.2f}<br>Total Orders: %{x}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text='Top Customers: Spending vs Order Frequency',
                    font=dict(size=16, color='#323130')
                ),
                xaxis=dict(title='Total Orders', gridcolor='#f3f2f1'),
                yaxis=dict(title='Total Spent ($)', gridcolor='#f3f2f1'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=300,
                margin=dict(l=50, r=50, t=70, b=50)
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error creating customer analysis chart: {str(e)}")
            return "{}"
    
    def analyze_categories(self, category_data: List[Dict]) -> Dict[str, Any]:
        """Analyze category performance."""
        try:
            df = pd.DataFrame(category_data)
            
            # Convert Decimal types to float
            if 'revenue' in df.columns:
                df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
            
            total_revenue = df['revenue'].sum()
            
            analysis = {
                'totalCategories': len(df),
                'topCategory': df.iloc[0]['category'] if len(df) > 0 else 'N/A',
                'topCategoryRevenue': float(df.iloc[0]['revenue']) if len(df) > 0 else 0,
                'topCategoryShare': float((df.iloc[0]['revenue'] / total_revenue * 100)) if len(df) > 0 and total_revenue > 0 else 0,
                'diversificationIndex': self.calculate_diversification_index(df['revenue'].tolist()),
                'revenueDistribution': self.calculate_revenue_distribution(df)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing categories: {str(e)}")
            return {}
    
    def analyze_geographical_data(self, state_data: List[Dict]) -> Dict[str, Any]:
        """Analyze geographical performance."""
        try:
            df = pd.DataFrame(state_data)
            
            analysis = {
                'totalStates': len(df),
                'topState': df.iloc[0]['state'] if len(df) > 0 else 'N/A',
                'topStateRevenue': df.iloc[0]['total_spending'] if len(df) > 0 else 0,
                'averageSpendingPerCustomer': df['total_spending'].sum() / df['customer_count'].sum() if df['customer_count'].sum() > 0 else 0,
                'geographicalConcentration': self.calculate_geographical_concentration(df),
                'marketPenetration': self.calculate_market_penetration(df)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing geographical data: {str(e)}")
            return {}
    
    def analyze_customer_data(self, customer_data: List[Dict]) -> Dict[str, Any]:
        """Analyze customer behavior."""
        try:
            df = pd.DataFrame(customer_data)
            
            # Convert Decimal types to float
            if 'total_spent' in df.columns:
                df['total_spent'] = pd.to_numeric(df['total_spent'], errors='coerce').fillna(0)
            if 'total_orders' in df.columns:
                df['total_orders'] = pd.to_numeric(df['total_orders'], errors='coerce').fillna(0)
            
            analysis = {
                'totalTopCustomers': len(df),
                'averageSpentPerCustomer': float(df['total_spent'].mean()),
                'averageOrdersPerCustomer': float(df['total_orders'].mean()),
                'customerValue': {
                    'high': len(df[df['total_spent'] > df['total_spent'].quantile(0.8)]),
                    'medium': len(df[(df['total_spent'] >= df['total_spent'].quantile(0.4)) & (df['total_spent'] <= df['total_spent'].quantile(0.8))]),
                    'low': len(df[df['total_spent'] < df['total_spent'].quantile(0.4)])
                },
                'loyaltySegments': self.segment_customers_by_loyalty(df)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing customer data: {str(e)}")
            return {}
    
    def calculate_advanced_metrics(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced business metrics."""
        try:
            metrics = {}
            
            # Calculate Customer Lifetime Value (CLV)
            if 'totalRevenue' in analytics_data and 'totalCustomers' in analytics_data:
                avg_revenue_per_customer = analytics_data['totalRevenue'] / analytics_data['totalCustomers']
                metrics['estimatedCLV'] = avg_revenue_per_customer * 2.5  # Simplified CLV estimation
            
            # Calculate churn risk indicators
            if 'topCustomers' in analytics_data:
                df = pd.DataFrame(analytics_data['topCustomers'])
                avg_orders = df['total_orders'].mean()
                metrics['customerHealthScore'] = min(100, (avg_orders / 10) * 100)
            
            # Calculate growth metrics
            if 'salesTrend' in analytics_data:
                df = pd.DataFrame(analytics_data['salesTrend'])
                if len(df) >= 2:
                    recent_sales = df.tail(3)['total_sales'].mean()
                    earlier_sales = df.head(3)['total_sales'].mean()
                    metrics['weekOverWeekGrowth'] = ((recent_sales - earlier_sales) / earlier_sales * 100) if earlier_sales > 0 else 0
            
            # Calculate efficiency metrics
            if 'totalRevenue' in analytics_data and 'totalOrders' in analytics_data:
                metrics['revenueEfficiency'] = analytics_data['totalRevenue'] / analytics_data['totalOrders'] if analytics_data['totalOrders'] > 0 else 0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating advanced metrics: {str(e)}")
            return {}
    
    def generate_predictions(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive insights."""
        try:
            predictions = {}
            
            # Simple trend prediction based on sales data
            if 'salesTrend' in analytics_data:
                df = pd.DataFrame(analytics_data['salesTrend'])
                if len(df) >= 3:
                    # Calculate simple linear trend
                    x = np.arange(len(df))
                    y = df['total_sales'].values
                    z = np.polyfit(x, y, 1)
                    
                    # Predict next 3 days
                    next_days = []
                    for i in range(3):
                        next_day_sales = z[0] * (len(df) + i) + z[1]
                        next_days.append({
                            'day': f'Day +{i+1}',
                            'predictedSales': max(0, next_day_sales)  # Ensure non-negative
                        })
                    
                    predictions['salesForecast'] = next_days
                    predictions['trendDirection'] = 'increasing' if z[0] > 0 else 'decreasing'
                    predictions['confidence'] = min(85, max(60, 75 + abs(z[0]) * 10))  # Simplified confidence
            
            # Revenue prediction
            if 'totalRevenue' in analytics_data and 'salesTrend' in analytics_data:
                current_revenue = analytics_data['totalRevenue']
                df = pd.DataFrame(analytics_data['salesTrend'])
                if len(df) > 0:
                    avg_daily_sales = df['total_sales'].mean()
                    predictions['monthlyRevenueProjection'] = avg_daily_sales * 30
                    predictions['quarterlyRevenueProjection'] = avg_daily_sales * 90
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            return {}
    
    def calculate_diversification_index(self, revenues: List[float]) -> float:
        """Calculate revenue diversification index (0-1, higher is more diversified)."""
        if not revenues or len(revenues) <= 1:
            return 0.0
        
        total = sum(revenues)
        if total == 0:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        proportions = [r / total for r in revenues]
        hhi = sum(p ** 2 for p in proportions)
        
        # Convert to diversification index (inverse of concentration)
        return 1 - hhi
    
    def calculate_revenue_distribution(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate revenue distribution statistics."""
        try:
            total_revenue = df['revenue'].sum()
            return {
                'top1Share': (df.iloc[0]['revenue'] / total_revenue * 100) if len(df) > 0 else 0,
                'top3Share': (df.head(3)['revenue'].sum() / total_revenue * 100) if len(df) >= 3 else 0,
                'top5Share': (df.head(5)['revenue'].sum() / total_revenue * 100) if len(df) >= 5 else 0,
            }
        except:
            return {'top1Share': 0, 'top3Share': 0, 'top5Share': 0}
    
    def calculate_geographical_concentration(self, df: pd.DataFrame) -> float:
        """Calculate geographical concentration index."""
        try:
            total_spending = df['total_spending'].sum()
            if total_spending == 0:
                return 0.0
            
            proportions = df['total_spending'] / total_spending
            return sum(p ** 2 for p in proportions)
        except:
            return 0.0
    
    def calculate_market_penetration(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate market penetration metrics."""
        try:
            total_customers = df['customer_count'].sum()
            total_spending = df['total_spending'].sum()
            
            return {
                'averageCustomersPerState': total_customers / len(df) if len(df) > 0 else 0,
                'averageSpendingPerState': total_spending / len(df) if len(df) > 0 else 0,
                'customerConcentration': df['customer_count'].std() / df['customer_count'].mean() if df['customer_count'].mean() > 0 else 0
            }
        except:
            return {'averageCustomersPerState': 0, 'averageSpendingPerState': 0, 'customerConcentration': 0}
    
    def segment_customers_by_loyalty(self, df: pd.DataFrame) -> Dict[str, int]:
        """Segment customers by loyalty (based on order frequency)."""
        try:
            high_loyalty = len(df[df['total_orders'] >= 10])
            medium_loyalty = len(df[(df['total_orders'] >= 5) & (df['total_orders'] < 10)])
            low_loyalty = len(df[df['total_orders'] < 5])
            
            return {
                'highLoyalty': high_loyalty,
                'mediumLoyalty': medium_loyalty,
                'lowLoyalty': low_loyalty
            }
        except:
            return {'highLoyalty': 0, 'mediumLoyalty': 0, 'lowLoyalty': 0}
    
    def generate_enhanced_mock_data(self) -> Dict[str, Any]:
        """Generate enhanced mock data with realistic multi-year business trends."""
        try:
            logger.info("📊 Generating comprehensive business analytics data with realistic trends...")
            
            # Base mock data with realistic yearly patterns
            current_year = datetime.now().year
            
            # Generate realistic yearly sales trend (last 5 years) with proper business growth
            sales_trend = []
            base_sales = 150000  # Base annual sales for year 1
            
            # Define realistic growth rates for each year
            growth_rates = [1.0, 1.12, 1.28, 1.48, 1.72]  # 12%, 15%, 15%, 16% growth
            year_names = ['2021', '2022', '2023', '2024', '2025']
            
            for i in range(5):
                year = current_year - 4 + i
                year_name = year_names[i]
                
                # Apply realistic business growth with seasonal variation
                growth_factor = growth_rates[i]
                seasonal_variance = np.random.uniform(0.98, 1.02)  # Small realistic variance
                annual_sales = base_sales * growth_factor * seasonal_variance
                
                # Calculate related metrics
                annual_orders = int(annual_sales / 142 + np.random.randint(-30, 50))
                unique_customers = int(annual_orders * 0.65 + np.random.randint(-20, 30))
                avg_order_value = annual_sales / annual_orders if annual_orders > 0 else 0
                
                sales_trend.append({
                    'year': year,
                    'total_sales': round(annual_sales, 2),
                    'order_count': max(120, annual_orders),
                    'unique_customers': max(75, unique_customers),
                    'avg_order_value': round(avg_order_value, 2)
                })
                
                logger.info(f"📈 {year_name}: ${annual_sales:,.2f} sales, {annual_orders} orders, {unique_customers} customers")
            
            # Generate category data with realistic business distribution
            categories = [
                'Enterprise Software', 'Business Hardware', 'Office Equipment', 
                'IT Services', 'Professional Tools', 'Cloud Solutions', 
                'Security Systems', 'Communication Tools'
            ]
            category_data = []
            total_revenue = sales_trend[-1]['total_sales']  # Use current year sales
            
            # Use realistic business category distribution
            weights = [28, 22, 18, 12, 8, 6, 4, 2]  # Enterprise-focused percentages
            for i, category in enumerate(categories):
                revenue = (weights[i] / 100) * total_revenue
                orders = int(revenue / 195 + np.random.randint(-25, 25))
                category_data.append({
                    'category': category,
                    'revenue': round(revenue, 2),
                    'orders_count': max(8, orders)
                })
                
            logger.info(f"💼 Top category: {category_data[0]['category']} with ${category_data[0]['revenue']:,.2f}")
            
            # Generate business customer data by state (realistic B2B distribution)
            states = ['CA', 'NY', 'TX', 'FL', 'WA', 'IL', 'PA', 'OH', 'GA', 'VA']
            state_weights = [22, 16, 14, 10, 8, 7, 6, 5, 4, 8]  # Business hub percentages
            state_data = []
            
            for i, state in enumerate(states):
                spending = (state_weights[i] / 100) * total_revenue
                customers = int(spending / 850 + np.random.randint(-10, 10))  # Higher per-customer spending
                state_data.append({
                    'state': state,
                    'total_spending': round(spending, 2),
                    'customer_count': max(8, customers)
                })
                
            logger.info(f"🌎 Top state: {state_data[0]['state']} with ${state_data[0]['total_spending']:,.2f}")
            
            # Generate enterprise customer data with realistic business names and spending
            enterprise_customers = [
                'GlobalTech Enterprises', 'Metro Business Solutions', 'Advanced Systems Corp', 
                'Digital Innovation LLC', 'Strategic Consulting Group', 'Enterprise Cloud Services',
                'Future Technologies Inc', 'Professional Services Network'
            ]
            customer_data = []
            
            for i, name in enumerate(enterprise_customers[:6]):  # Top 6 customers
                # Large enterprise customers follow realistic spending patterns
                base_spending = 45000 / (i + 1) ** 0.4  # More gradual decline for enterprise
                spending = base_spending + np.random.uniform(-2000, 2000)
                orders = int(spending / 380 + np.random.randint(-3, 8))  # Higher order values
                customer_data.append({
                    'customer_name': name,
                    'total_spent': round(max(8000, spending), 2),
                    'total_orders': max(8, orders)
                })
                
            logger.info(f"🏢 Top customer: {customer_data[0]['customer_name']} spent ${customer_data[0]['total_spent']:,.2f}")
            
            # Calculate current year totals
            current_year_data = sales_trend[-1]
            
            logger.info(f"📊 Analytics Summary:")
            logger.info(f"   💰 Total Revenue: ${current_year_data['total_sales']:,.2f}")
            logger.info(f"   📦 Total Orders: {current_year_data['order_count']:,}")
            logger.info(f"   👥 Total Customers: {current_year_data['unique_customers']:,}")
            logger.info(f"   💵 Avg Order Value: ${current_year_data['avg_order_value']:,.2f}")
            
            return {
                'totalRevenue': current_year_data['total_sales'],
                'totalOrders': current_year_data['order_count'],
                'totalCustomers': current_year_data['unique_customers'],
                'avgOrderValue': current_year_data['avg_order_value'],
                'salesTrend': sales_trend,
                'topCategories': category_data,
                'salesByState': state_data,
                'topCustomers': customer_data,
                'orderStatus': [
                    {'order_status': 'completed', 'count': int(current_year_data['order_count'] * 0.82), 'total_amount': round(current_year_data['total_sales'] * 0.82, 2)},
                    {'order_status': 'shipped', 'count': int(current_year_data['order_count'] * 0.10), 'total_amount': round(current_year_data['total_sales'] * 0.10, 2)},
                    {'order_status': 'processing', 'count': int(current_year_data['order_count'] * 0.05), 'total_amount': round(current_year_data['total_sales'] * 0.05, 2)},
                    {'order_status': 'pending', 'count': int(current_year_data['order_count'] * 0.02), 'total_amount': round(current_year_data['total_sales'] * 0.02, 2)},
                    {'order_status': 'cancelled', 'count': int(current_year_data['order_count'] * 0.01), 'total_amount': round(current_year_data['total_sales'] * 0.01, 2)}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced mock data: {str(e)}")
            return {}
