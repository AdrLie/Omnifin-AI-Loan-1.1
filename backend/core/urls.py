from django.urls import path
from .views import (
    # API Configuration
    APIConfigurationListView, APIConfigurationDetailView,
    # System Settings
    SystemSettingListView, SystemSettingDetailView,
    # File Upload
    FileUploadView, FileUploadDetailView,
    # Notifications
    NotificationListView, NotificationDetailView, NotificationMarkReadView,
    # Audit Log
    AuditLogListView,
    # Dashboard
    DashboardStatsView, SystemHealthView,
)

app_name = 'core'

urlpatterns = [
    # API Configuration
    path('api-config/', APIConfigurationListView.as_view(), name='api-config-list'),
    path('api-config/<int:pk>/', APIConfigurationDetailView.as_view(), name='api-config-detail'),
    
    # System Settings
    path('settings/', SystemSettingListView.as_view(), name='setting-list'),
    path('settings/<str:key>/', SystemSettingDetailView.as_view(), name='setting-detail'),
    
    # File Upload
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('upload/<int:pk>/', FileUploadDetailView.as_view(), name='file-detail'),
    
    # Notifications
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    
    # Audit Log
    path('audit-log/', AuditLogListView.as_view(), name='audit-log-list'),
    
    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('system/health/', SystemHealthView.as_view(), name='system-health'),
]