from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import (
    Group, APIConfiguration, SystemSetting, FileUpload,
    Notification, AuditLog
)
from .serializers import (
    GroupSerializer, APIConfigurationSerializer, SystemSettingSerializer,
    FileUploadSerializer, NotificationSerializer, AuditLogSerializer
)
from .permissions import IsAdminOrSuperAdmin
from .services import FileProcessingService, NotificationService
import logging

logger = logging.getLogger(__name__)

# API Configuration Views
class APIConfigurationListView(generics.ListCreateAPIView):
    """
    List and create API configurations
    """
    serializer_class = APIConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return APIConfiguration.objects.all()
        return APIConfiguration.objects.filter(group=user.group)
    
    def perform_create(self, serializer):
        if self.request.user.role != 'superadmin':
            serializer.save(created_by=self.request.user, group=self.request.user.group)
        else:
            serializer.save(created_by=self.request.user)

class APIConfigurationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete API configuration
    """
    serializer_class = APIConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return APIConfiguration.objects.all()
        return APIConfiguration.objects.filter(group=user.group)

# System Setting Views
class SystemSettingListView(generics.ListCreateAPIView):
    """
    List and create system settings
    """
    serializer_class = SystemSettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    queryset = SystemSetting.objects.all()

class SystemSettingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete system setting
    """
    serializer_class = SystemSettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_object(self):
        key = self.kwargs.get('key')
        return get_object_or_404(SystemSetting, key=key)

# File Upload Views
class FileUploadView(generics.ListCreateAPIView):
    """
    Upload and list files
    """
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return FileUpload.objects.all()
        return FileUpload.objects.filter(uploaded_by=user)
    
    def perform_create(self, serializer):
        file_service = FileProcessingService()
        
        # Process file
        file_obj = self.request.FILES.get('file')
        if file_obj:
            processed_file = file_service.process_upload(file_obj, self.request.user)
            serializer.save(
                uploaded_by=self.request.user,
                original_name=file_obj.name,
                file_size=file_obj.size,
                mime_type=file_obj.content_type,
                **processed_file
            )

class FileUploadDetailView(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete uploaded file
    """
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return FileUpload.objects.all()
        return FileUpload.objects.filter(uploaded_by=user)

# Notification Views
class NotificationListView(generics.ListAPIView):
    """
    List notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Notification.objects.all()
        return Notification.objects.filter(
            models.Q(user=user) | 
            models.Q(group=user.group) | 
            models.Q(user__isnull=True, group__isnull=True)
        )

class NotificationDetailView(generics.RetrieveAPIView):
    """
    Retrieve notification details
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Notification.objects.all()
        return Notification.objects.filter(
            models.Q(user=user) | 
            models.Q(group=user.group) | 
            models.Q(user__isnull=True, group__isnull=True)
        )

class NotificationMarkReadView(generics.GenericAPIView):
    """
    Mark notification as read
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})

# Audit Log Views
class AuditLogListView(generics.ListAPIView):
    """
    List audit logs
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    queryset = AuditLog.objects.all()

# Dashboard Views
class DashboardStatsView(generics.GenericAPIView):
    """
    Get dashboard statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from datetime import datetime, timedelta
        from django.db.models import Count, Avg, Sum
        from order.models import Order, Conversation
        from authentication.models import User
        
        # Time ranges
        now = timezone.now()
        today = now.date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        
        # User stats
        total_users = User.objects.count()
        active_users_today = User.objects.filter(last_login__date=today).count()
        new_users_7_days = User.objects.filter(date_joined__date__gte=last_7_days).count()
        
        # Order stats
        total_orders = Order.objects.count()
        orders_today = Order.objects.filter(created_at__date=today).count()
        orders_7_days = Order.objects.filter(created_at__date__gte=last_7_days).count()
        
        # Conversation stats
        total_conversations = Conversation.objects.count()
        active_conversations = Conversation.objects.filter(status='active').count()
        conversations_today = Conversation.objects.filter(started_at__date=today).count()
        
        # Status distribution
        order_status_distribution = dict(
            Order.objects.values_list('status').annotate(count=Count('status'))
        )
        
        conversation_status_distribution = dict(
            Conversation.objects.values_list('status').annotate(count=Count('status'))
        )
        
        stats = {
            'users': {
                'total': total_users,
                'active_today': active_users_today,
                'new_7_days': new_users_7_days,
            },
            'orders': {
                'total': total_orders,
                'today': orders_today,
                'last_7_days': orders_7_days,
                'status_distribution': order_status_distribution,
            },
            'conversations': {
                'total': total_conversations,
                'active': active_conversations,
                'today': conversations_today,
                'status_distribution': conversation_status_distribution,
            },
            'timestamp': now.isoformat()
        }
        
        return Response(stats)

class SystemHealthView(generics.GenericAPIView):
    """
    Get system health status
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get(self, request):
        import os
        import psutil
        from django.db import connection
        
        # Database health
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_health = cursor.fetchone()[0] == 1
        except Exception:
            db_health = False
        
        # System resources
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            
            system_health = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_info.percent,
                'memory_available_gb': memory_info.available / (1024**3),
                'disk_percent': disk_usage.percent,
                'disk_free_gb': disk_usage.free / (1024**3),
            }
        except Exception:
            system_health = None
        
        # Cache health (Redis)
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            cache_health = cache.get('health_check') == 'ok'
        except Exception:
            cache_health = False
        
        health_status = {
            'database': db_health,
            'cache': cache_health,
            'system': system_health is not None,
            'system_resources': system_health,
            'overall': db_health and cache_health and system_health is not None,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(health_status)