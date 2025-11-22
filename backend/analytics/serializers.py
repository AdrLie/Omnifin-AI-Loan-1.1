from rest_framework import serializers
from .models import (
    UserActivity, Metric, UserEngagement, ConversationAnalytics,
    OrderAnalytics, SystemPerformance, Report, DashboardWidget
)


class UserActivitySerializer(serializers.ModelSerializer):
    """
    User Activity serializer
    """
    user_email = serializers.SerializerMethodField()
    ip_address = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_email', 'action', 'resource_type', 'resource_id',
            'ip_address', 'user_agent', 'session_id', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'user_email']
    
    def get_user_email(self, obj):
        try:
            return obj.user.email if obj.user else None
        except Exception:
            return None


class MetricSerializer(serializers.ModelSerializer):
    """
    Metric serializer
    """
    class Meta:
        model = Metric
        fields = [
            'id', 'name', 'category', 'value', 'recorded_at', 'period', 'metadata'
        ]
        read_only_fields = ['id', 'recorded_at']


class UserEngagementSerializer(serializers.ModelSerializer):
    """
    User Engagement serializer
    """
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = UserEngagement
        fields = [
            'id', 'user', 'user_email', 'date', 'session_duration', 'page_views',
            'conversations_count', 'messages_sent', 'orders_created', 'files_uploaded',
            'unique_sessions', 'bounce_rate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user_email']


class ConversationAnalyticsSerializer(serializers.ModelSerializer):
    """
    Conversation Analytics serializer
    """
    class Meta:
        model = ConversationAnalytics
        fields = [
            'id', 'conversation', 'message_count', 'user_message_count',
            'ai_message_count', 'avg_response_time', 'total_duration',
            'satisfaction_score', 'intent_accuracy', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderAnalyticsSerializer(serializers.ModelSerializer):
    """
    Order Analytics serializer
    """
    class Meta:
        model = OrderAnalytics
        fields = [
            'id', 'order', 'processing_time', 'completion_time',
            'documents_count', 'conversation_turns', 'automation_level',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemPerformanceSerializer(serializers.ModelSerializer):
    """
    System Performance serializer
    """
    class Meta:
        model = SystemPerformance
        fields = [
            'id', 'metric_name', 'metric_value', 'metric_unit', 'category',
            'recorded_at', 'metadata'
        ]
        read_only_fields = ['id', 'recorded_at']


class ReportSerializer(serializers.ModelSerializer):
    """
    Report serializer
    """
    generated_by_email = serializers.ReadOnlyField(source='generated_by.email')
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'parameters', 'data',
            'generated_by', 'generated_by_email', 'file_path', 'file_size',
            'is_ready', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'generated_by_email', 'is_ready', 'completed_at']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """
    Dashboard Widget serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'configuration', 'data_source',
            'refresh_interval', 'is_active', 'created_by', 'created_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_email']
