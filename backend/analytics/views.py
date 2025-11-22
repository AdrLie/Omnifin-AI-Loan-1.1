from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserActivity, Metric, UserEngagement, ConversationAnalytics,
    OrderAnalytics, SystemPerformance, Report, DashboardWidget
)
from .serializers import (
    UserActivitySerializer, MetricSerializer, UserEngagementSerializer,
    ConversationAnalyticsSerializer, OrderAnalyticsSerializer,
    SystemPerformanceSerializer, ReportSerializer, DashboardWidgetSerializer
)
import logging

logger = logging.getLogger(__name__)


# User Activity Views
class UserActivityListView(generics.ListCreateAPIView):
    """
    List and create user activities
    Supports pagination and limit parameter for recent activities
    """
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = UserActivity.objects.all().select_related('user').order_by('-created_at')
        
        # Filter by user role
        if user and hasattr(user, 'role') and user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(user=user)
        
        return queryset
    
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Support limit parameter for dashboard
            limit = request.query_params.get('limit')
            if limit:
                try:
                    queryset = queryset[:int(limit)]
                except (ValueError, TypeError):
                    pass
            
            # Check if queryset is empty
            if not queryset.exists():
                return Response([])
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error in UserActivityListView: {str(e)}\n{error_traceback}")
            print(f"Full traceback:\n{error_traceback}")  # Print to console
            return Response({
                'error': str(e),
                'traceback': error_traceback
            }, status=500)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserActivityDetailView(generics.RetrieveAPIView):
    """
    Retrieve user activity
    """
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=user)


# Metric Views
class MetricListView(generics.ListCreateAPIView):
    """
    List and create metrics
    """
    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Metric.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()


class MetricDetailView(generics.RetrieveAPIView):
    """
    Retrieve metric
    """
    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Metric.objects.all()


# User Engagement Views
class UserEngagementListView(generics.ListCreateAPIView):
    """
    List and create user engagement metrics
    """
    serializer_class = UserEngagementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return UserEngagement.objects.all()
        return UserEngagement.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save()


class UserEngagementDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user engagement
    """
    serializer_class = UserEngagementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return UserEngagement.objects.all()
        return UserEngagement.objects.filter(user=user)


# Conversation Analytics Views
class ConversationAnalyticsListView(generics.ListCreateAPIView):
    """
    List and create conversation analytics
    """
    serializer_class = ConversationAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ConversationAnalytics.objects.all()


class ConversationAnalyticsDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update conversation analytics
    """
    serializer_class = ConversationAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ConversationAnalytics.objects.all()


# Order Analytics Views
class OrderAnalyticsListView(generics.ListCreateAPIView):
    """
    List and create order analytics
    """
    serializer_class = OrderAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrderAnalytics.objects.all()


class OrderAnalyticsDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update order analytics
    """
    serializer_class = OrderAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrderAnalytics.objects.all()


# System Performance Views
class SystemPerformanceListView(generics.ListCreateAPIView):
    """
    List and create system performance metrics
    """
    serializer_class = SystemPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SystemPerformance.objects.all()


class SystemPerformanceDetailView(generics.RetrieveAPIView):
    """
    Retrieve system performance metric
    """
    serializer_class = SystemPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SystemPerformance.objects.all()


# Report Views
class ReportListView(generics.ListCreateAPIView):
    """
    List and create reports
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Report.objects.all()
        return Report.objects.filter(generated_by=user)
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


class ReportDetailView(generics.RetrieveAPIView):
    """
    Retrieve report
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Report.objects.all()
        return Report.objects.filter(generated_by=user)


# Dashboard Widget Views
class DashboardWidgetListView(generics.ListCreateAPIView):
    """
    List and create dashboard widgets
    """
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return DashboardWidget.objects.filter(is_active=True)
        return DashboardWidget.objects.filter(created_by=user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DashboardWidgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete dashboard widget
    """
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return DashboardWidget.objects.all()
        return DashboardWidget.objects.filter(created_by=user)


# Analytics Summary Views
class AnalyticsSummaryView(APIView):
    """
    Get analytics summary
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        
        # User activity stats
        if user.role in ['admin', 'superadmin']:
            total_activities = UserActivity.objects.count()
            activities_today = UserActivity.objects.filter(created_at__date=today).count()
            activities_7_days = UserActivity.objects.filter(created_at__date__gte=last_7_days).count()
        else:
            total_activities = UserActivity.objects.filter(user=user).count()
            activities_today = UserActivity.objects.filter(user=user, created_at__date=today).count()
            activities_7_days = UserActivity.objects.filter(user=user, created_at__date__gte=last_7_days).count()
        
        # Engagement stats
        if user.role in ['admin', 'superadmin']:
            engagement_data = UserEngagement.objects.filter(date__gte=last_7_days).aggregate(
                total_page_views=Sum('page_views'),
                total_conversations=Sum('conversations_count'),
                total_messages=Sum('messages_sent'),
                avg_session_duration=Avg('session_duration')
            )
        else:
            engagement_data = UserEngagement.objects.filter(user=user, date__gte=last_7_days).aggregate(
                total_page_views=Sum('page_views'),
                total_conversations=Sum('conversations_count'),
                total_messages=Sum('messages_sent'),
                avg_session_duration=Avg('session_duration')
            )
        
        return Response({
            'user_activity': {
                'total': total_activities,
                'today': activities_today,
                'last_7_days': activities_7_days,
            },
            'engagement': {
                'page_views': engagement_data.get('total_page_views', 0) or 0,
                'conversations': engagement_data.get('total_conversations', 0) or 0,
                'messages': engagement_data.get('total_messages', 0) or 0,
                'avg_session_duration': engagement_data.get('avg_session_duration', 0) or 0,
            },
            'timestamp': now.isoformat()
        })


class ActivityTrendsView(APIView):
    """
    Get activity trends over time
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get activity trends
        if user.role in ['admin', 'superadmin']:
            activities = UserActivity.objects.filter(
                created_at__date__gte=start_date
            ).values('created_at__date', 'action').annotate(count=Count('id'))
        else:
            activities = UserActivity.objects.filter(
                user=user,
                created_at__date__gte=start_date
            ).values('created_at__date', 'action').annotate(count=Count('id'))
        
        return Response({
            'period': f'{days} days',
            'start_date': start_date.isoformat(),
            'trends': list(activities)
        })
