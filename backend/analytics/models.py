from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserActivity(models.Model):
    """
    User activity tracking
    """
    ACTION_CHOICES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('view', _('View')),
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('chat_start', _('Chat Started')),
        ('chat_message', _('Chat Message')),
        ('voice_start', _('Voice Chat Started')),
        ('file_upload', _('File Upload')),
        ('order_created', _('Order Created')),
        ('order_updated', _('Order Updated')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(_('action'), max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(_('resource type'), max_length=50, blank=True)
    resource_id = models.IntegerField(_('resource ID'), null=True, blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    session_id = models.CharField(_('session ID'), max_length=100, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'analytics_useractivity'
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"

class Metric(models.Model):
    """
    System metrics for analytics
    """
    PERIOD_CHOICES = [
        ('hourly', _('Hourly')),
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
    ]
    
    name = models.CharField(_('metric name'), max_length=100)
    category = models.CharField(_('category'), max_length=50)
    value = models.DecimalField(_('value'), max_digits=15, decimal_places=2)
    recorded_at = models.DateTimeField(_('recorded at'), auto_now_add=True)
    period = models.CharField(_('period'), max_length=20, choices=PERIOD_CHOICES, default='daily')
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'analytics_metric'
        verbose_name = _('Metric')
        verbose_name_plural = _('Metrics')
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['name', 'recorded_at']),
            models.Index(fields=['category', 'recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value} ({self.recorded_at})"

class UserEngagement(models.Model):
    """
    User engagement metrics
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField(_('date'))
    session_duration = models.IntegerField(_('session duration (seconds)'), null=True, blank=True)
    page_views = models.IntegerField(_('page views'), default=0)
    conversations_count = models.IntegerField(_('conversations count'), default=0)
    messages_sent = models.IntegerField(_('messages sent'), default=0)
    orders_created = models.IntegerField(_('orders created'), default=0)
    files_uploaded = models.IntegerField(_('files uploaded'), default=0)
    unique_sessions = models.IntegerField(_('unique sessions'), default=1)
    bounce_rate = models.FloatField(_('bounce rate'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_userengagement'
        verbose_name = _('User Engagement')
        verbose_name_plural = _('User Engagements')
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"

class ConversationAnalytics(models.Model):
    """
    Conversation analytics
    """
    conversation = models.OneToOneField('order.Conversation', on_delete=models.CASCADE, related_name='analytics')
    message_count = models.IntegerField(_('message count'), default=0)
    user_message_count = models.IntegerField(_('user message count'), default=0)
    ai_message_count = models.IntegerField(_('AI message count'), default=0)
    avg_response_time = models.FloatField(_('average response time (seconds)'), null=True, blank=True)
    total_duration = models.IntegerField(_('total duration (seconds)'), null=True, blank=True)
    satisfaction_score = models.FloatField(_('satisfaction score'), null=True, blank=True)
    intent_accuracy = models.FloatField(_('intent accuracy'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'analytics_conversationanalytics'
        verbose_name = _('Conversation Analytics')
        verbose_name_plural = _('Conversation Analytics')
    
    def __str__(self):
        return f"Analytics - Conversation {self.conversation.id}"

class OrderAnalytics(models.Model):
    """
    Order analytics
    """
    order = models.OneToOneField('order.Order', on_delete=models.CASCADE, related_name='analytics')
    processing_time = models.IntegerField(_('processing time (seconds)'), null=True, blank=True)
    completion_time = models.IntegerField(_('completion time (seconds)'), null=True, blank=True)
    documents_count = models.IntegerField(_('documents count'), default=0)
    conversation_turns = models.IntegerField(_('conversation turns'), default=0)
    automation_level = models.FloatField(_('automation level'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'analytics_orderanalytics'
        verbose_name = _('Order Analytics')
        verbose_name_plural = _('Order Analytics')
    
    def __str__(self):
        return f"Analytics - Order {self.order.id}"

class SystemPerformance(models.Model):
    """
    System performance metrics
    """
    metric_name = models.CharField(_('metric name'), max_length=100)
    metric_value = models.FloatField(_('metric value'))
    metric_unit = models.CharField(_('metric unit'), max_length=20, blank=True)
    category = models.CharField(_('category'), max_length=50)
    recorded_at = models.DateTimeField(_('recorded at'), auto_now_add=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'analytics_systemperformance'
        verbose_name = _('System Performance')
        verbose_name_plural = _('System Performances')
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.metric_unit}"

class Report(models.Model):
    """
    Generated reports
    """
    REPORT_TYPE_CHOICES = [
        ('user_activity', _('User Activity Report')),
        ('conversation', _('Conversation Report')),
        ('order', _('Order Report')),
        ('performance', _('Performance Report')),
        ('custom', _('Custom Report')),
    ]
    
    name = models.CharField(_('report name'), max_length=200)
    report_type = models.CharField(_('report type'), max_length=50, choices=REPORT_TYPE_CHOICES)
    parameters = models.JSONField(_('parameters'), default=dict, blank=True)
    data = models.JSONField(_('report data'), default=dict, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(_('file path'), max_length=500, blank=True)
    file_size = models.IntegerField(_('file size'), null=True, blank=True)
    is_ready = models.BooleanField(_('is ready'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'analytics_report'
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.report_type}"

class DashboardWidget(models.Model):
    """
    Dashboard widget configurations
    """
    WIDGET_TYPE_CHOICES = [
        ('chart', _('Chart')),
        ('metric', _('Metric Card')),
        ('table', _('Table')),
        ('graph', _('Graph')),
        ('progress', _('Progress Bar')),
    ]
    
    name = models.CharField(_('widget name'), max_length=100)
    widget_type = models.CharField(_('widget type'), max_length=20, choices=WIDGET_TYPE_CHOICES)
    configuration = models.JSONField(_('configuration'), default=dict, blank=True)
    data_source = models.CharField(_('data source'), max_length=100)
    refresh_interval = models.IntegerField(_('refresh interval (seconds)'), default=300)
    is_active = models.BooleanField(_('is active'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'analytics_dashboardwidget'
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgets')
    
    def __str__(self):
        return f"{self.name} ({self.widget_type})"