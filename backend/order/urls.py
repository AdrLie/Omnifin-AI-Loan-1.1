from django.urls import path
from .views import (
    # Order views
    OrderListView, OrderDetailView, OrderStatusUpdateView,
    # Conversation views
    ConversationListView, ConversationDetailView, ConversationEndView,
    # Message views
    MessageListView, MessageCreateView, MessageDetailView,
    # Voice views
    VoiceRecordingUploadView, VoiceRecordingDetailView,
    # Document views
    OrderDocumentListView, OrderDocumentDetailView,
    # Chat specific
    ChatStartView, ChatMessageView, ChatHistoryView,
    # Voice chat specific
    VoiceChatStartView, VoiceMessageView,
    # AI processing
    ProcessMessageView, GenerateAIResponseView,
)

app_name = 'order'

urlpatterns = [
    # Order endpoints
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    
    # Conversation endpoints
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:pk>/end/', ConversationEndView.as_view(), name='conversation-end'),
    
    # Message endpoints
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('conversations/<int:conversation_id>/messages/send/', MessageCreateView.as_view(), name='message-create'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    
    # Voice recording endpoints
    path('voice-recordings/upload/', VoiceRecordingUploadView.as_view(), name='voice-upload'),
    path('voice-recordings/<int:pk>/', VoiceRecordingDetailView.as_view(), name='voice-detail'),
    
    # Document endpoints
    path('orders/<int:order_id>/documents/', OrderDocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', OrderDocumentDetailView.as_view(), name='document-detail'),
    
    # Chat specific endpoints
    path('chat/start/', ChatStartView.as_view(), name='chat-start'),
    path('chat/<int:conversation_id>/message/', ChatMessageView.as_view(), name='chat-message'),
    path('chat/<int:conversation_id>/history/', ChatHistoryView.as_view(), name='chat-history'),
    
    # Voice chat specific endpoints
    path('voice-chat/start/', VoiceChatStartView.as_view(), name='voice-chat-start'),
    path('voice-chat/<int:conversation_id>/message/', VoiceMessageView.as_view(), name='voice-message'),
    
    # AI processing endpoints
    path('ai/process-message/', ProcessMessageView.as_view(), name='process-message'),
    path('ai/generate-response/', GenerateAIResponseView.as_view(), name='generate-response'),
]