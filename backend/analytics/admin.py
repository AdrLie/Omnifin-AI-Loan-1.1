from django.contrib import admin
from .models import (
    UserActivity, Metric, UserEngagement,
    ConversationAnalytics, OrderAnalytics, SystemPerformance,
    Report, DashboardWidget
)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'ip_address', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'action']
    readonly_fields = ['created_at']

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'value', 'period', 'recorded_at']
    list_filter = ['category', 'period', 'recorded_at']
    search_fields = ['name', 'category']
    readonly_fields = ['recorded_at']

@admin.register(UserEngagement)
class UserEngagementAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'session_duration', 'page_views', 'conversations_count']
    list_filter = ['date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']

@admin.register(ConversationAnalytics)
class ConversationAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'message_count', 'avg_response_time', 'satisfaction_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['conversation__id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OrderAnalytics)
class OrderAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['order', 'processing_time', 'completion_time', 'documents_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SystemPerformance)
class SystemPerformanceAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'metric_value', 'metric_unit', 'category', 'recorded_at']
    list_filter = ['category', 'recorded_at']
    search_fields = ['metric_name', 'category']
    readonly_fields = ['recorded_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'generated_by', 'is_ready', 'created_at']
    list_filter = ['report_type', 'is_ready', 'created_at']
    search_fields = ['name', 'report_type']
    readonly_fields = ['created_at', 'completed_at']

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'data_source', 'is_active', 'created_at']
    list_filter = ['widget_type', 'is_active', 'created_at']
    search_fields = ['name', 'data_source']
    readonly_fields = ['created_at', 'updated_at']