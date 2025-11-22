from django.urls import path
from .views import (
    # User Activity
    UserActivityListView, UserActivityDetailView,
    # Metrics
    MetricListView, MetricDetailView,
    # User Engagement
    UserEngagementListView, UserEngagementDetailView,
    # Conversation Analytics
    ConversationAnalyticsListView, ConversationAnalyticsDetailView,
    # Order Analytics
    OrderAnalyticsListView, OrderAnalyticsDetailView,
    # System Performance
    SystemPerformanceListView, SystemPerformanceDetailView,
    # Reports
    ReportListView, ReportDetailView,
    # Dashboard Widgets
    DashboardWidgetListView, DashboardWidgetDetailView,
    # Summary Views
    AnalyticsSummaryView, ActivityTrendsView,
)

app_name = 'analytics'

urlpatterns = [
    # User Activity endpoints
    path('activities/', UserActivityListView.as_view(), name='user-activity-list'),
    path('activities/<int:pk>/', UserActivityDetailView.as_view(), name='user-activity-detail'),
    
    # Metric endpoints
    path('metrics/', MetricListView.as_view(), name='metric-list'),
    path('metrics/<int:pk>/', MetricDetailView.as_view(), name='metric-detail'),
    
    # User Engagement endpoints
    path('engagement/', UserEngagementListView.as_view(), name='user-engagement-list'),
    path('engagement/<int:pk>/', UserEngagementDetailView.as_view(), name='user-engagement-detail'),
    
    # Conversation Analytics endpoints
    path('conversations/', ConversationAnalyticsListView.as_view(), name='conversation-analytics-list'),
    path('conversations/<int:pk>/', ConversationAnalyticsDetailView.as_view(), name='conversation-analytics-detail'),
    
    # Order Analytics endpoints
    path('orders/', OrderAnalyticsListView.as_view(), name='order-analytics-list'),
    path('orders/<int:pk>/', OrderAnalyticsDetailView.as_view(), name='order-analytics-detail'),
    
    # System Performance endpoints
    path('performance/', SystemPerformanceListView.as_view(), name='system-performance-list'),
    path('performance/<int:pk>/', SystemPerformanceDetailView.as_view(), name='system-performance-detail'),
    
    # Report endpoints
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    
    # Dashboard Widget endpoints
    path('widgets/', DashboardWidgetListView.as_view(), name='dashboard-widget-list'),
    path('widgets/<int:pk>/', DashboardWidgetDetailView.as_view(), name='dashboard-widget-detail'),
    
    # Summary endpoints
    path('summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    path('trends/', ActivityTrendsView.as_view(), name='activity-trends'),
]
