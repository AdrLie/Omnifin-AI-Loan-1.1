"""
URL configuration for Omnifin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as auth_views
from order.views import (
    ChatMessageWorkflowView, ChatHistoryWorkflowView,
    ChatVoiceWorkflowView, ChatStatusWorkflowView
)
from authentication.views import (
    AdminUserListCreateView, AdminUserDetailView
)
from analytics.views import AnalyticsSummaryView
from knowledge.views import PromptListView, PromptDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', auth_views.obtain_auth_token, name='api_token_auth'),
    path('api/auth/', include('authentication.urls')),
    path('api/core/', include('core.urls')),
    path('api/knowledge/', include('knowledge.urls')),
    path('api/order/', include('order.urls')),
    path('api/analytics/', include('analytics.urls')),
    
    # Workflow chat endpoints
    path('api/chat/message/', ChatMessageWorkflowView.as_view(), name='workflow-chat-message'),
    path('api/chat/history/', ChatHistoryWorkflowView.as_view(), name='workflow-chat-history'),
    path('api/chat/voice/', ChatVoiceWorkflowView.as_view(), name='workflow-chat-voice'),
    path('api/chat/status/', ChatStatusWorkflowView.as_view(), name='workflow-chat-status'),
    
    # Admin workflow endpoints
    path('api/admin/users/', AdminUserListCreateView.as_view(), name='workflow-admin-users'),
    path('api/admin/users/<int:user_id>/', AdminUserDetailView.as_view(), name='workflow-admin-user-detail'),
    path('api/admin/analytics/', AnalyticsSummaryView.as_view(), name='workflow-admin-analytics'),
    path('api/admin/prompts/', PromptListView.as_view(), name='workflow-admin-prompts'),
    path('api/admin/prompts/<int:pk>/', PromptDetailView.as_view(), name='workflow-admin-prompt-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)