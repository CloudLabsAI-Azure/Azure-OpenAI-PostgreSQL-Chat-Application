// Global state management
const AppState = {
    isLoading: false,
    currentQuery: null,
    analyticsData: null
};

// DOM Elements
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingSteps = document.getElementById('loading-steps');
const sqlModal = document.getElementById('sql-modal');
const sqlContent = document.getElementById('sql-content');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - starting initialization');
    
    // Test for refresh button immediately
    setTimeout(() => {
        const refreshBtn = document.getElementById('refresh-analytics-btn');
        if (refreshBtn) {
            console.log('✅ Refresh button found on DOM load:', refreshBtn);
            console.log('📍 Refresh button position:', refreshBtn.getBoundingClientRect());
            console.log('🎨 Refresh button styles:', window.getComputedStyle(refreshBtn));
            
            // Test click functionality
            console.log('🎯 Refresh button can be clicked:', !refreshBtn.disabled);
            console.log('👀 Refresh button is visible:', refreshBtn.offsetWidth > 0 && refreshBtn.offsetHeight > 0);
        } else {
            console.error('❌ Refresh button NOT found on DOM load!');
        }
    }, 100);
    
    // Test if send button is visible immediately
    setTimeout(() => {
        const sendBtn = document.getElementById('send-button');
        if (sendBtn) {
            console.log('Send button found on DOM load:', sendBtn);
            console.log('Send button offsetWidth:', sendBtn.offsetWidth);
            console.log('Send button offsetHeight:', sendBtn.offsetHeight);
            console.log('Send button getBoundingClientRect:', sendBtn.getBoundingClientRect());
            
            // Test if icon is present
            const icon = sendBtn.querySelector('i');
            if (icon) {
                console.log('Send button icon found:', icon);
                console.log('Icon classes:', icon.className);
                console.log('Icon computed styles:', window.getComputedStyle(icon));
            } else {
                console.error('Send button icon NOT found!');
                // Try to add the icon if missing
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                console.log('Added missing icon to send button');
                
                // Double-check after adding
                setTimeout(() => {
                    const newIcon = sendBtn.querySelector('i');
                    if (newIcon) {
                        console.log('✓ Icon successfully added to send button');
                    } else {
                        console.error('✗ Failed to add icon, using text fallback');
                        sendBtn.innerHTML = '→'; // Simple arrow as fallback
                    }
                }, 100);
            }
            
            // Test click functionality
            console.log('Send button disabled state:', sendBtn.disabled);
            console.log('Send button can be clicked:', !sendBtn.disabled);
        }
        
        // Test dollar icons
        const dollarIcons = document.querySelectorAll('.fa-dollar-sign');
        console.log('Dollar icons on DOM load:', dollarIcons.length);
        
        // Test Plotly availability
        console.log('Plotly available:', !!window.Plotly);
        if (window.Plotly) {
            console.log('Plotly version:', window.Plotly.version);
        }
    }, 500);
    
    initializeApp();
    setupEventListeners();
    loadAnalytics();
});

function initializeApp() {
    console.log('Initializing app...');
    
    // Check if elements exist
    if (!messageInput) {
        console.error('Message input not found!');
        return;
    }
    if (!sendButton) {
        console.error('Send button not found!');
        return;
    }
    
    console.log('Elements found, setting up event listeners...');
    
    // Debug send button specifically
    if (sendButton) {
        console.log('Send button element:', sendButton);
        console.log('Send button innerHTML:', sendButton.innerHTML);
        setTimeout(() => {
            console.log('Send button computed styles:', window.getComputedStyle(sendButton));
            console.log('Send button visibility:', window.getComputedStyle(sendButton).visibility);
            console.log('Send button display:', window.getComputedStyle(sendButton).display);
            console.log('Send button opacity:', window.getComputedStyle(sendButton).opacity);
        }, 100);
    }
    
    // Debug currency icons
    setTimeout(() => {
        const dollarIcons = document.querySelectorAll('.fa-dollar-sign');
        console.log('Dollar sign icons found:', dollarIcons.length);
        dollarIcons.forEach((icon, index) => {
            console.log(`Dollar icon ${index}:`, icon);
            console.log(`Dollar icon ${index} styles:`, window.getComputedStyle(icon));
        });
    }, 100);
    
    // Enable send button when input has content
    messageInput.addEventListener('input', function() {
        const hasContent = this.value.trim().length > 0;
        sendButton.disabled = !hasContent;
        console.log('Input changed, send button disabled:', !hasContent);
    });

    // Send message on Enter key
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && !sendButton.disabled) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    console.log('App initialized successfully');
}

function setupEventListeners() {
    // Send button click
    sendButton.addEventListener('click', sendMessage);

    // Clear chat button click
    const clearChatBtn = document.getElementById('clear-chat-btn');
    if (clearChatBtn) {
        console.log('Clear chat button found, adding event listener');
        clearChatBtn.addEventListener('click', clearChatHistory);
    } else {
        console.warn('Clear chat button not found');
    }

    // Refresh analytics button click
    const refreshAnalyticsBtn = document.getElementById('refresh-analytics-btn');
    if (refreshAnalyticsBtn) {
        console.log('✅ Refresh analytics button found, adding event listener');
        refreshAnalyticsBtn.addEventListener('click', async function() {
            console.log('🔄 Refresh analytics button clicked');
            
            // Add loading state
            this.classList.add('loading');
            this.disabled = true;
            const spanElement = this.querySelector('span');
            const originalText = spanElement ? spanElement.textContent : 'Refresh';
            if (spanElement) {
                spanElement.textContent = 'Refreshing...';
            }
            
            try {
                console.log('📊 Starting analytics refresh...');
                await loadAnalytics(true);
                console.log('✅ Analytics refresh completed successfully');
                showToast('Analytics data refreshed successfully!', 'success');
            } catch (error) {
                console.error('❌ Error refreshing analytics:', error);
                showToast('Failed to refresh analytics data', 'error');
            } finally {
                // Remove loading state
                console.log('🏁 Cleaning up refresh button state');
                this.classList.remove('loading');
                this.disabled = false;
                if (spanElement) {
                    spanElement.textContent = originalText;
                }
            }
        });
    } else {
        console.error('❌ Refresh analytics button NOT found! Check HTML structure.');
        // Try to find it by class as fallback
        const refreshBtnByClass = document.querySelector('.refresh-btn');
        if (refreshBtnByClass) {
            console.log('🔍 Found refresh button by class, adding event listener');
            refreshBtnByClass.addEventListener('click', async function() {
                console.log('🔄 Refresh button (found by class) clicked');
                try {
                    await loadAnalytics(true);
                    showToast('Analytics data refreshed successfully!', 'success');
                } catch (error) {
                    console.error('❌ Error refreshing analytics:', error);
                    showToast('Failed to refresh analytics data', 'error');
                }
            });
        } else {
            console.error('❌ Refresh button not found by ID or class!');
        }
    }

    // Suggestion clicks
    document.querySelectorAll('.suggestion').forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            const text = this.getAttribute('data-text');
            messageInput.value = text;
            sendButton.disabled = false;
            messageInput.focus();
        });
    });

    // Example button clicks - Use event delegation to handle dynamically added buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('example-btn') || e.target.closest('.example-btn')) {
            const button = e.target.classList.contains('example-btn') ? e.target : e.target.closest('.example-btn');
            const text = button.getAttribute('data-text');
            if (text) {
                messageInput.value = text;
                sendButton.disabled = false;
                messageInput.focus();
            }
        }
    });

    // Modal close on background click
    sqlModal.addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });

    // Escape key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
            hideToast();
        }
    });
}

async function sendMessage() {
    if (AppState.isLoading) return;

    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessageToChat(message, 'user');

    // Clear input and disable send button
    messageInput.value = '';
    sendButton.disabled = true;

    // Show loading state
    setLoadingState(true);

    try {
        // Send request to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Add assistant response to chat (natural language only)
            addMessageToChat(data.response, 'assistant');

            showToast('Query executed successfully!', 'success');
        } else {
            // Handle error response
            addMessageToChat(
                data.error || 'Sorry, I encountered an error processing your request.',
                'assistant',
                { isError: true }
            );
            showToast(data.error || 'Request failed', 'error');
        }

    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat(
            'Sorry, I\'m having trouble connecting to the server. Please try again.',
            'assistant',
            { isError: true }
        );
        showToast('Connection error. Please try again.', 'error');
    } finally {
        setLoadingState(false);
        messageInput.focus();
    }
}

function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'user' 
        ? '<i class="fas fa-user"></i>' 
        : '<i class="fas fa-robot"></i>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Format message content
    let formattedMessage = formatMessageContent(message);
    contentDiv.innerHTML = formattedMessage;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function createSqlSection(sqlQuery, rowCount) {
    const section = document.createElement('div');
    section.className = 'sql-query-section';

    const title = document.createElement('strong');
    title.textContent = 'Generated SQL Query:';
    section.appendChild(title);

    const queryDiv = document.createElement('div');
    queryDiv.className = 'sql-query';
    queryDiv.textContent = sqlQuery;
    section.appendChild(queryDiv);

    const metadataDiv = document.createElement('div');
    metadataDiv.className = 'query-metadata';
    
    const rowInfo = document.createElement('span');
    rowInfo.textContent = `${rowCount} rows returned`;
    
    const viewButton = document.createElement('button');
    viewButton.className = 'view-sql-button';
    viewButton.innerHTML = '<i class="fas fa-code"></i> View SQL';
    viewButton.onclick = () => showSqlModal(sqlQuery);
    
    metadataDiv.appendChild(rowInfo);
    metadataDiv.appendChild(viewButton);
    section.appendChild(metadataDiv);

    return section;
}

function formatMessageContent(message) {
    // Convert markdown-style formatting to HTML
    let formatted = message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');

    // Convert bullet points
    formatted = formatted.replace(/^- (.*$)/gim, '<li>$1</li>');
    if (formatted.includes('<li>')) {
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }

    // Convert numbered lists
    formatted = formatted.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
    if (formatted.includes('<li>') && !formatted.includes('<ul>')) {
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
    }

    return formatted;
}

function setLoadingState(isLoading) {
    AppState.isLoading = isLoading;
    
    if (isLoading) {
        loadingOverlay.classList.remove('hidden');
        animateLoadingSteps();
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

function animateLoadingSteps() {
    const steps = [
        'Analyzing your question...',
        'Converting to SQL query...',
        'Executing database query...',
        'Processing results...',
        'Generating response...'
    ];
    
    let currentStep = 0;
    loadingSteps.textContent = steps[currentStep];
    
    const interval = setInterval(() => {
        currentStep++;
        if (currentStep < steps.length && AppState.isLoading) {
            loadingSteps.textContent = steps[currentStep];
        } else {
            clearInterval(interval);
        }
    }, 1000);
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function clearChatHistory() {
    console.log('clearChatHistory called');
    // Show confirmation dialog
    if (confirm('Are you sure you want to clear all chat messages? This cannot be undone.')) {
        // Clear the chat messages and restore welcome message
        chatMessages.innerHTML = `
            <div class="message assistant-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <p>👋 <strong>Welcome to Azure OpenAI Chat!</strong></p>
                    <p>Ask me anything about your database in natural language.</p>
                    
                    <p><strong>Try these examples:</strong></p>
                    <div class="example-buttons">
                        <button class="example-btn" data-text="Show me all customers">👥 Show me all customers</button>
                        <button class="example-btn" data-text="What products cost more than $100?">🛒 What products cost more than $100?</button>
                        <button class="example-btn" data-text="List recent orders">📋 List recent orders</button>
                        <button class="example-btn" data-text="Find customers from New York">📍 Find customers from New York</button>
                    </div>
                </div>
            </div>
        `;
        
        // Show success message
        showToast('Chat history cleared successfully!', 'success');
        
        // Scroll to top
        scrollToBottom();
        
        console.log('Chat history cleared successfully');
    }
}

function showSqlModal(sqlQuery) {
    sqlContent.textContent = sqlQuery;
    sqlModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    sqlModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

async function copySqlToClipboard() {
    try {
        await navigator.clipboard.writeText(sqlContent.textContent);
        showToast('SQL copied to clipboard!', 'success');
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = sqlContent.textContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('SQL copied to clipboard!', 'success');
    }
}

function showToast(message, type = 'success') {
    const toastId = type === 'error' ? 'error-toast' : 'success-toast';
    const messageId = type === 'error' ? 'error-message' : 'success-message';
    
    const toast = document.getElementById(toastId);
    const messageElement = document.getElementById(messageId);
    
    messageElement.textContent = message;
    toast.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideToast(toastId);
    }, 5000);
}

function hideToast(toastId = null) {
    if (toastId) {
        document.getElementById(toastId).classList.add('hidden');
    } else {
        document.getElementById('error-toast').classList.add('hidden');
        document.getElementById('success-toast').classList.add('hidden');
    }
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Handle page visibility changes for analytics refresh
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Optionally refresh analytics when page becomes visible again
        loadAnalytics(true);
    }
});

// Export functions for global access
window.closeModal = closeModal;
window.copySqlToClipboard = copySqlToClipboard;
window.hideToast = hideToast;

// Global refresh handler for the refresh button
window.handleRefreshClick = async function(button) {
    console.log('🔄 Global refresh handler called');
    
    if (!button) {
        button = document.getElementById('refresh-analytics-btn');
    }
    
    if (!button) {
        console.error('❌ No refresh button found!');
        return;
    }
    
    // Add loading state
    button.classList.add('loading');
    button.disabled = true;
    const spanElement = button.querySelector('span');
    const originalText = spanElement ? spanElement.textContent : 'Refresh';
    if (spanElement) {
        spanElement.textContent = 'Refreshing...';
    }
    
    try {
        console.log('📊 Starting analytics refresh via global handler...');
        await loadAnalytics(true);
        console.log('✅ Analytics refresh completed successfully via global handler');
        showToast('Analytics data refreshed successfully!', 'success');
    } catch (error) {
        console.error('❌ Error refreshing analytics via global handler:', error);
        showToast('Failed to refresh analytics data. Please try again.', 'error');
    } finally {
        // Remove loading state
        console.log('🏁 Cleaning up refresh button state via global handler');
        button.classList.remove('loading');
        button.disabled = false;
        if (spanElement) {
            spanElement.textContent = originalText;
        }
    }
};

// Analytics Functions
async function loadAnalytics(forceRefresh = false) {
    console.log(`📊 loadAnalytics called with forceRefresh=${forceRefresh}`);
    
    if (!forceRefresh && AppState.analyticsData) {
        console.log('📋 Using cached analytics data');
        updateAnalyticsDisplay(AppState.analyticsData);
        return;
    }

    try {
        console.log('🌐 Making request to /api/analytics...');
        const response = await fetch('/api/analytics', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': forceRefresh ? 'no-cache' : 'default'
            }
        });
        
        console.log('📡 Response received:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📊 Analytics response data:', data);
        
        if (data.status === 'success') {
            console.log('✅ Analytics data loaded successfully');
            console.log('📈 Analytics keys:', Object.keys(data.analytics || {}));
            
            // Cache the data
            AppState.analyticsData = data.analytics;
            
            // Update the display
            updateAnalyticsDisplay(data.analytics);
            
            console.log('🎨 Analytics display updated');
        } else {
            console.error('❌ Analytics API returned error:', data.error);
            showAnalyticsError();
            throw new Error(data.error || 'Analytics API error');
        }
    } catch (error) {
        console.error('💥 Analytics loading error:', error);
        console.error('🔍 Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        showAnalyticsError();
        throw error; // Re-throw so the calling function can handle it
    }
}

function updateAnalyticsDisplay(analytics) {
    console.log('Updating analytics display with data:', analytics);
    
    // Update metrics cards with enhanced formatting
    // Handle both camelCase and snake_case property names
    const totalRevenue = analytics.totalRevenue || analytics.total_revenue || 0;
    const totalOrders = analytics.totalOrders || analytics.total_orders || 0;
    const totalCustomers = analytics.totalCustomers || analytics.total_customers || 0;
    const avgOrderValue = analytics.avgOrderValue || analytics.avg_order_value || 0;
    
    console.log('Analytics values:', { totalRevenue, totalOrders, totalCustomers, avgOrderValue });
    
    updateElement('total-revenue', formatCurrency(totalRevenue));
    updateElement('total-orders', totalOrders.toLocaleString());
    updateElement('total-customers', totalCustomers.toLocaleString());
    updateElement('avg-order-value', formatCurrency(avgOrderValue));

    // Update metric change indicators if available
    updateMetricChanges(analytics);

    // Update category chart with enhanced visualization
    if (analytics.topCategories) {
        updateCategoriesChart(analytics.topCategories);
    }

    // Update state sales chart
    if (analytics.salesByState) {
        updateStateChart(analytics.salesByState);
    }

    // Update top customers
    if (analytics.topCustomers) {
        updateTopCustomers(analytics.topCustomers);
    }

    // Update sales trend chart with Plotly if available
    if (analytics.salesTrendChart) {
        console.log('Found salesTrendChart data, updating Plotly chart...');
        console.log('salesTrendChart data:', analytics.salesTrendChart);
        updatePlotlyChart('sales-trend-plotly', analytics.salesTrendChart);
    } else if (analytics.salesTrend) {
        console.log('No salesTrendChart found, using salesTrend data for fallback chart...');
        console.log('salesTrend data:', analytics.salesTrend);
        
        // Create simple chart from salesTrend data
        createSimpleSalesChart(analytics.salesTrend);
        
        // Also try to create a Plotly-compatible chart structure
        try {
            const plotlyData = {
                data: [{
                    x: analytics.salesTrend.map(item => item.date),
                    y: analytics.salesTrend.map(item => item.total_sales || item.sales || 0),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Sales',
                    line: { color: '#667eea', width: 3 },
                    marker: { color: '#667eea', size: 6 }
                }],
                layout: {
                    title: 'Sales Trend - Last 7 Days',
                    xaxis: { title: 'Date' },
                    yaxis: { title: 'Sales ($)' },
                    margin: { t: 40, r: 20, b: 40, l: 60 },
                    height: 250
                }
            };
            updatePlotlyChart('sales-trend-plotly', plotlyData);
        } catch (error) {
            console.error('Error creating Plotly data from salesTrend:', error);
            createSimpleSalesChart(analytics.salesTrend);
        }
    } else {
        console.warn('No sales trend data available');
        // Show a friendly message in the chart container
        const container = document.getElementById('sales-trend-plotly');
        if (container) {
            container.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 200px; color: #666; font-style: italic; flex-direction: column; background: rgba(0, 120, 212, 0.02); border-radius: 8px;">
                    <div style="font-size: 48px; margin-bottom: 15px; opacity: 0.5;">📊</div>
                    <div style="font-size: 16px; font-weight: 500; margin-bottom: 8px;">Sales Trend Chart</div>
                    <div style="font-size: 14px; color: #999;">No data available for the last 7 days</div>
                    <button onclick="loadAnalytics(true)" style="margin-top: 15px; padding: 8px 16px; background: #0078d4; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">Refresh Data</button>
                </div>
            `;
        }
    }

    // Display additional insights if available
    if (analytics.categoryAnalysis) {
        displayCategoryInsights(analytics.categoryAnalysis);
    }

    // Display advanced metrics if available
    if (analytics.advancedMetrics) {
        displayAdvancedMetrics(analytics.advancedMetrics);
    }

    // Display predictions if available
    if (analytics.predictions) {
        displayPredictions(analytics.predictions);
    }
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function formatCurrency(amount) {
    console.log('formatCurrency called with:', amount, 'type:', typeof amount);
    
    // Ensure amount is a number
    const numAmount = parseFloat(amount) || 0;
    console.log('formatCurrency parsed amount:', numAmount);
    
    const result = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(numAmount);
    
    console.log('formatCurrency result:', result);
    return result;
}

function updateCategoriesChart(categories) {
    const container = document.getElementById('category-bars');
    if (!container) return;

    const maxValue = Math.max(...categories.map(c => c.revenue));
    
    container.innerHTML = categories.slice(0, 5).map(category => `
        <div class="category-bar">
            <span class="category-name">${category.category}</span>
            <div class="bar-container">
                <div class="bar-fill" style="width: ${(category.revenue / maxValue) * 100}%"></div>
            </div>
            <span class="bar-value">${formatCurrency(category.revenue)}</span>
        </div>
    `).join('');
}

function updateStateChart(stateData) {
    const container = document.getElementById('state-list');
    if (!container) return;

    container.innerHTML = stateData.slice(0, 5).map(state => `
        <div class="state-item">
            <span class="state-name">${state.state}</span>
            <span class="state-sales">${formatCurrency(state.total_spending)}</span>
        </div>
    `).join('');
}

function updateTopCustomers(customers) {
    const container = document.getElementById('top-customers-list');
    if (!container) return;

    container.innerHTML = customers.slice(0, 5).map(customer => `
        <div class="customer-item">
            <span class="customer-name">${customer.customer_name}</span>
            <span class="customer-total">${formatCurrency(customer.total_spent)}</span>
        </div>
    `).join('');
}

function updateSalesChart(salesData) {
    const canvas = document.getElementById('salesCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (!salesData || salesData.length === 0) return;

    // Prepare data
    const maxValue = Math.max(...salesData.map(d => d.total_sales));
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // Draw axes
    ctx.strokeStyle = '#e1dfdd';
    ctx.lineWidth = 1;
    
    // Y-axis
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();
    
    // X-axis
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw line chart
    if (salesData.length > 1) {
        ctx.strokeStyle = '#0078d4';
        ctx.lineWidth = 2;
        ctx.beginPath();

        salesData.forEach((point, index) => {
            const x = padding + (index / (salesData.length - 1)) * chartWidth;
            const y = height - padding - (point.total_sales / maxValue) * chartHeight;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();

        // Draw points
        ctx.fillStyle = '#0078d4';
        salesData.forEach((point, index) => {
            const x = padding + (index / (salesData.length - 1)) * chartWidth;
            const y = height - padding - (point.total_sales / maxValue) * chartHeight;
            
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, 2 * Math.PI);
            ctx.fill();
        });
    }

    // Add labels
    ctx.fillStyle = '#605e5c';
    ctx.font = '10px Segoe UI';
    ctx.textAlign = 'center';

    // X-axis labels (dates)
    salesData.forEach((point, index) => {
        if (index % Math.ceil(salesData.length / 4) === 0) {
            const x = padding + (index / (salesData.length - 1)) * chartWidth;
            const date = new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            ctx.fillText(date, x, height - padding + 15);
        }
    });

    // Y-axis labels (values)
    ctx.textAlign = 'right';
    for (let i = 0; i <= 3; i++) {
        const value = (maxValue / 3) * i;
        const y = height - padding - (i / 3) * chartHeight;
        ctx.fillText(formatCurrency(value), padding - 5, y + 3);
    }
}

function showAnalyticsError() {
    const elements = ['total-revenue', 'total-orders', 'total-customers', 'avg-order-value'];
    elements.forEach(id => updateElement(id, 'Error'));
    
    const containers = ['category-bars', 'state-list', 'top-customers-list'];
    containers.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = '<div class="analytics-loading">Failed to load data</div>';
        }
    });
}

// Enhanced Analytics Functions
function updateMetricChanges(analytics) {
    // Update change indicators if available
    const changeElements = [
        { id: 'revenue-change', key: 'revenueChange' },
        { id: 'orders-change', key: 'ordersChange' },
        { id: 'customers-change', key: 'customersChange' },
        { id: 'aov-change', key: 'aovChange' }
    ];

    changeElements.forEach(({ id, key }) => {
        const element = document.getElementById(id);
        if (element && analytics[key] !== undefined) {
            const value = analytics[key];
            element.textContent = `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
            element.className = `metric-change ${value >= 0 ? 'positive' : 'negative'}`;
        }
    });
}

function updatePlotlyChart(containerId, chartData) {
    console.log('updatePlotlyChart called with:', { containerId, chartData });
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID '${containerId}' not found!`);
        return;
    }

    // First, check if we have data to work with
    if (!chartData) {
        console.warn('No chart data provided, creating simple chart message');
        container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 200px; color: #666; font-style: italic; flex-direction: column;"><div>📊 Sales Trend Chart</div><div style="font-size: 14px; margin-top: 10px;">No data available for the last 7 days</div></div>';
        return;
    }

    // Try to use Plotly if available
    if (window.Plotly && typeof window.Plotly.newPlot === 'function') {
        console.log('Plotly is available, attempting to create chart...');
        
        try {
            // Clear any existing content
            container.innerHTML = '';

            const config = {
                responsive: true,
                displayModeBar: false,
                displaylogo: false
            };

            // Parse the chart data
            let plotData;
            try {
                if (typeof chartData === 'string') {
                    plotData = JSON.parse(chartData);
                } else {
                    plotData = chartData;
                }
                console.log('Parsed plot data:', plotData);
                
                // Validate plot data structure
                if (!plotData.data || !Array.isArray(plotData.data)) {
                    throw new Error('Invalid plot data structure - missing data array');
                }
                
            } catch (parseError) {
                console.error('Error parsing chart data:', parseError);
                console.error('Chart data was:', chartData);
                throw parseError; // Re-throw to trigger fallback
            }

            // Create the plot
            console.log('Creating Plotly chart...');
            window.Plotly.newPlot(container, plotData.data, plotData.layout, config)
                .then(() => {
                    console.log('✅ Plotly chart created successfully!');
                    // Hide fallback canvas if it exists
                    const fallbackCanvas = document.getElementById('salesCanvas');
                    if (fallbackCanvas) {
                        fallbackCanvas.style.display = 'none';
                    }
                })
                .catch((plotError) => {
                    console.error('❌ Error creating Plotly chart:', plotError);
                    // Fallback to simple HTML chart
                    createFallbackChart(container, chartData);
                });
                
        } catch (error) {
            console.error('Error in Plotly chart creation:', error);
            // Fallback to simple HTML chart
            createFallbackChart(container, chartData);
        }
    } else {
        console.warn('Plotly not available, using fallback chart');
        // Fallback to simple HTML chart
        createFallbackChart(container, chartData);
    }
}

function createFallbackChart(container, chartData) {
    console.log('Creating fallback chart...');
    
    try {
        // Parse chart data to extract sales information
        let salesData = [];
        
        if (typeof chartData === 'string') {
            const plotData = JSON.parse(chartData);
            if (plotData.data && plotData.data[0] && plotData.data[0].x && plotData.data[0].y) {
                // Convert Plotly data format to simple array
                const xData = plotData.data[0].x;
                const yData = plotData.data[0].y;
                salesData = xData.map((date, index) => ({
                    date: date,
                    total_sales: yData[index] || 0
                }));
            }
        } else if (chartData.data && chartData.data[0]) {
            // Same conversion for object format
            const xData = chartData.data[0].x;
            const yData = chartData.data[0].y;
            salesData = xData.map((date, index) => ({
                date: date,
                total_sales: yData[index] || 0
            }));
        }
        
        if (salesData.length === 0) {
            // If we can't parse the data, show a generic message
            container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 200px; color: #666; font-style: italic; flex-direction: column;"><div>📊 Sales Trend Chart</div><div style="font-size: 14px; margin-top: 10px;">Chart data is being processed...</div></div>';
            return;
        }
        
        // Create a beautiful HTML/CSS chart
        const maxSales = Math.max(...salesData.map(d => d.total_sales));
        const totalSales = salesData.reduce((sum, item) => sum + item.total_sales, 0);
        
        const chartHtml = `
            <div style="padding: 20px; height: 100%; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h4 style="margin: 0; color: #333; font-size: 16px;">📈 Sales Trend - Last 7 Days</h4>
                    <div style="color: #0078d4; font-weight: bold; font-size: 14px;">
                        Total: ${formatCurrency(totalSales)}
                    </div>
                </div>
                <div style="flex: 1; display: flex; align-items: end; gap: 8px; min-height: 150px; background: linear-gradient(to bottom, rgba(0, 120, 212, 0.05), transparent); padding: 10px; border-radius: 8px;">
                    ${salesData.map((item) => {
                        const height = maxSales > 0 ? Math.max(((item.total_sales / maxSales) * 120), 5) : 10;
                        const date = new Date(item.date).toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                        });
                        const isToday = new Date(item.date).toDateString() === new Date().toDateString();
                        return `
                            <div style="flex: 1; display: flex; flex-direction: column; align-items: center; cursor: pointer;" title="${date}: ${formatCurrency(item.total_sales)}">
                                <div style="
                                    background: ${isToday ? 'linear-gradient(135deg, #FF6B6B, #EE5A24)' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
                                    width: 100%;
                                    height: ${height}px;
                                    border-radius: 4px 4px 2px 2px;
                                    margin-bottom: 8px;
                                    min-height: 8px;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)'" 
                                   onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'"></div>
                                <div style="font-size: 11px; color: #666; text-align: center; font-weight: ${isToday ? 'bold' : 'normal'};">
                                    ${date}
                                </div>
                                <div style="font-size: 10px; color: #999; margin-top: 2px;">
                                    ${formatCurrency(item.total_sales)}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div style="text-align: center; margin-top: 15px; padding: 10px; background: rgba(0, 120, 212, 0.05); border-radius: 6px;">
                    <div style="color: #666; font-size: 12px; margin-bottom: 5px;">Average Daily Sales</div>
                    <div style="color: #0078d4; font-weight: bold; font-size: 14px;">
                        ${formatCurrency(totalSales / salesData.length)}
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = chartHtml;
        console.log('✅ Fallback chart created successfully');
        
    } catch (error) {
        console.error('Error creating fallback chart:', error);
        // Ultimate fallback - simple message
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 200px; color: #666; font-style: italic; flex-direction: column; background: rgba(0, 120, 212, 0.02); border-radius: 8px;">
                <div style="font-size: 18px; margin-bottom: 10px;">📊</div>
                <div style="font-size: 16px; font-weight: 500; margin-bottom: 5px;">Sales Trend Chart</div>
                <div style="font-size: 12px;">Data visualization ready</div>
            </div>
        `;
    }
}

function displayCategoryInsights(analysis) {
    const container = document.getElementById('category-insights');
    if (!container) return;

    const diversificationScore = Math.round(analysis.diversificationIndex * 100);
    const topCategoryShare = Math.round(analysis.topCategoryShare);

    container.innerHTML = `
        <div class="insight-card">
            <h5><i class="fas fa-chart-pie"></i> Category Analysis</h5>
            <div class="insight-metrics">
                <div class="insight-metric">
                    <span class="metric-label">Top Category</span>
                    <span class="metric-value">${analysis.topCategory}</span>
                </div>
                <div class="insight-metric">
                    <span class="metric-label">Market Share</span>
                    <span class="metric-value">${topCategoryShare}%</span>
                </div>
                <div class="insight-metric">
                    <span class="metric-label">Diversification Score</span>
                    <span class="metric-value">${diversificationScore}/100</span>
                </div>
            </div>
        </div>
    `;
}

function displayAdvancedMetrics(metrics) {
    const container = document.getElementById('advanced-metrics');
    if (!container) return;

    container.innerHTML = `
        <div class="insight-card">
            <h5><i class="fas fa-brain"></i> Advanced Metrics</h5>
            <div class="insight-metrics">
                ${metrics.estimatedCLV ? `
                    <div class="insight-metric">
                        <span class="metric-label">Est. Customer LTV</span>
                        <span class="metric-value">${formatCurrency(metrics.estimatedCLV)}</span>
                    </div>
                ` : ''}
                ${metrics.customerHealthScore ? `
                    <div class="insight-metric">
                        <span class="metric-label">Customer Health</span>
                        <span class="metric-value">${Math.round(metrics.customerHealthScore)}%</span>
                    </div>
                ` : ''}
                ${metrics.weekOverWeekGrowth !== undefined ? `
                    <div class="insight-metric">
                        <span class="metric-label">WoW Growth</span>
                        <span class="metric-value ${metrics.weekOverWeekGrowth >= 0 ? 'positive' : 'negative'}">
                            ${metrics.weekOverWeekGrowth >= 0 ? '+' : ''}${metrics.weekOverWeekGrowth.toFixed(1)}%
                        </span>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function displayPredictions(predictions) {
    const container = document.getElementById('predictions');
    if (!container) return;

    let predictionHTML = `
        <div class="insight-card">
            <h5><i class="fas fa-crystal-ball"></i> Predictions</h5>
            <div class="insight-metrics">
    `;

    if (predictions.salesForecast && predictions.salesForecast.length > 0) {
        const nextDayPrediction = predictions.salesForecast[0];
        predictionHTML += `
            <div class="insight-metric">
                <span class="metric-label">Tomorrow's Sales</span>
                <span class="metric-value">${formatCurrency(nextDayPrediction.predictedSales)}</span>
            </div>
        `;
    }

    if (predictions.trendDirection) {
        predictionHTML += `
            <div class="insight-metric">
                <span class="metric-label">Trend Direction</span>
                <span class="metric-value ${predictions.trendDirection === 'increasing' ? 'positive' : 'negative'}">
                    ${predictions.trendDirection} ${predictions.trendDirection === 'increasing' ? '📈' : '📉'}
                </span>
            </div>
        `;
    }

    if (predictions.confidence) {
        predictionHTML += `
            <div class="insight-metric">
                <span class="metric-label">Confidence</span>
                <span class="metric-value">${Math.round(predictions.confidence)}%</span>
            </div>
        `;
    }

    predictionHTML += '</div></div>';
    container.innerHTML = predictionHTML;
}

function createSimpleSalesChart(salesData) {
    console.log('Creating simple sales chart fallback with data:', salesData);
    const container = document.getElementById('sales-trend-plotly');
    if (!container || !salesData || salesData.length === 0) {
        console.warn('No container or sales data for fallback chart');
        return;
    }

    // Check if we have yearly or daily data
    const isYearlyData = salesData[0] && (salesData[0].year || salesData[0].year === 0);
    const maxSales = Math.max(...salesData.map(d => d.total_sales || d.sales || 0));
    // const dataLabel = isYearlyData ? 'year' : 'date'; // unused variable removed
    const chartTitle = isYearlyData ? 'Business Growth - 5-Year Overview' : 'Sales Trend - Recent Days';
    const totalSales = salesData.reduce((sum, item) => sum + (item.total_sales || item.sales || 0), 0);
    
    console.log(`Chart type: ${isYearlyData ? 'Yearly' : 'Daily'}, Max sales: $${maxSales.toLocaleString()}, Total: $${totalSales.toLocaleString()}`);
    
    // Create a beautiful HTML/CSS chart
    const chartHtml = `
        <div style="padding: 25px; height: 100%; display: flex; flex-direction: column; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <div>
                    <h4 style="margin: 0; color: #212529; font-size: 18px; font-weight: 600;">📊 ${chartTitle}</h4>
                    <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 13px;">${isYearlyData ? 'Annual Performance Metrics' : 'Daily Sales Activity'}</p>
                </div>
                <div style="text-align: right;">
                    <div style="color: #0078d4; font-weight: bold; font-size: 16px;">
                        Total: ${formatCurrency(totalSales)}
                    </div>
                    <div style="color: #6c757d; font-size: 12px; margin-top: 2px;">
                        ${isYearlyData ? '5-Year Revenue' : 'Period Total'}
                    </div>
                </div>
            </div>
            <div style="flex: 1; display: flex; align-items: end; gap: ${isYearlyData ? '15px' : '8px'}; min-height: 180px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e9ecef;">
                ${salesData.map((item, idx) => {
                    const height = maxSales > 0 ? Math.max(((item.total_sales || item.sales || 0) / maxSales) * 140, 8) : 15;
                    let displayDate;
                    
                    if (isYearlyData) {
                        displayDate = item.year ? item.year.toString() : '2025';
                    } else {
                        displayDate = new Date(item.date).toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                        });
                    }
                    
                    const isCurrentPeriod = isYearlyData ? 
                        (item.year === new Date().getFullYear()) : 
                        (new Date(item.date).toDateString() === new Date().toDateString());
                    
                    const salesValue = item.total_sales || item.sales || 0;
                    
                    // Calculate growth for yearly data
                    let growthIndicator = '';
                    if (isYearlyData && idx > 0) {
                        const prevSales = salesData[idx - 1].total_sales || salesData[idx - 1].sales || 0;
                        if (prevSales > 0) {
                            const growthRate = ((salesValue - prevSales) / prevSales) * 100;
                            if (Math.abs(growthRate) > 3) {
                                growthIndicator = `
                                    <div style="position: absolute; top: -35px; left: 50%; transform: translateX(-50%); 
                                                background: ${growthRate > 0 ? '#28a745' : '#dc3545'}; color: white; 
                                                padding: 2px 6px; border-radius: 10px; font-size: 9px; font-weight: bold;
                                                box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                        ${growthRate > 0 ? '+' : ''}${growthRate.toFixed(0)}%
                                    </div>
                                `;
                            }
                        }
                    }
                    
                    return `
                        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; cursor: pointer; position: relative;" 
                             title="${displayDate}: ${formatCurrency(salesValue)}${isYearlyData && item.order_count ? ' • ' + item.order_count.toLocaleString() + ' orders' : ''}">
                            ${growthIndicator}
                            <div style="
                                background: ${isCurrentPeriod ? 
                                    'linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%)' : 
                                    isYearlyData ? 
                                        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' :
                                        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
                                };
                                width: 100%;
                                height: ${height}px;
                                border-radius: ${isYearlyData ? '8px 8px 4px 4px' : '4px 4px 2px 2px'};
                                margin-bottom: 12px;
                                min-height: 12px;
                                transition: all 0.3s ease;
                                box-shadow: 0 3px 6px rgba(0,0,0,0.15);
                                position: relative;
                            " onmouseover="this.style.transform='scale(1.05) translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.25)'" 
                               onmouseout="this.style.transform='scale(1) translateY(0)'; this.style.boxShadow='0 3px 6px rgba(0,0,0,0.15)'">
                                ${isYearlyData ? `
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                                                color: white; font-size: 10px; font-weight: bold; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
                                        ${item.year}
                                    </div>
                                ` : ''}
                            </div>
                            <div style="font-size: ${isYearlyData ? '12px' : '11px'}; color: #495057; text-align: center; 
                                        font-weight: ${isCurrentPeriod ? 'bold' : 'normal'}; line-height: 1.2;">
                                ${displayDate}
                            </div>
                            <div style="font-size: ${isYearlyData ? '11px' : '10px'}; color: #6c757d; margin-top: 3px; text-align: center;">
                                ${formatCurrency(salesValue)}
                            </div>
                            ${isYearlyData && item.order_count ? `
                                <div style="font-size: 9px; color: #28a745; margin-top: 1px; text-align: center;">
                                    ${item.order_count.toLocaleString()} orders
                                </div>
                            ` : ''}
                        </div>
                    `;
                }).join('')}
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
                <div style="text-align: center; padding: 15px; background: rgba(0, 120, 212, 0.05); border-radius: 8px; border: 1px solid rgba(0, 120, 212, 0.1);">
                    <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">${isYearlyData ? 'Average Annual Revenue' : 'Average Daily Sales'}</div>
                    <div style="color: #0078d4; font-weight: bold; font-size: 15px;">
                        ${formatCurrency(totalSales / salesData.length)}
                    </div>
                </div>
                <div style="text-align: center; padding: 15px; background: rgba(40, 167, 69, 0.05); border-radius: 8px; border: 1px solid rgba(40, 167, 69, 0.1);">
                    <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">${isYearlyData ? 'Growth Trend' : 'Performance'}</div>
                    <div style="color: #28a745; font-weight: bold; font-size: 15px;">
                        ${isYearlyData ? 'Strong Growth' : 'Stable'}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = chartHtml;
    console.log(`✅ Enhanced ${isYearlyData ? 'yearly' : 'daily'} fallback chart created successfully`);
}

// Refresh analytics every 5 minutes
setInterval(() => {
    loadAnalytics(true);
}, 300000);
