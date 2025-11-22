from django.contrib import admin
from .models import (
    Order, Conversation, Message, VoiceRecording,
    OrderDocument, OrderStatusHistory
)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_type', 'status', 'priority', 'created_at']
    list_filter = ['order_type', 'status', 'priority', 'created_at']
    search_fields = ['user__username', 'user__email', 'id']
    readonly_fields = ['created_at', 'updated_at', 'duration']
    raw_id_fields = ['user', 'assigned_to']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'conversation_type', 'status', 'started_at', 'duration']
    list_filter = ['conversation_type', 'status', 'started_at']
    search_fields = ['user__username', 'user__email', 'id']
    readonly_fields = ['started_at', 'ended_at', 'duration']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender_type', 'message_type', 'created_at']
    list_filter = ['sender_type', 'message_type', 'created_at']
    search_fields = ['content', 'conversation__id']
    readonly_fields = ['created_at', 'processed_at']

@admin.register(VoiceRecording)
class VoiceRecordingAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'duration', 'language', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['transcript', 'message__id']
    readonly_fields = ['created_at']

@admin.register(OrderDocument)
class OrderDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'document_type', 'original_name', 'is_verified', 'created_at']
    list_filter = ['document_type', 'is_verified', 'created_at']
    search_fields = ['original_name', 'order__id']
    readonly_fields = ['created_at']

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['order__id', 'notes']
    readonly_fields = ['created_at']