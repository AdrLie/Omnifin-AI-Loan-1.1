from rest_framework import serializers
from .models import (
    Order, Conversation, Message, VoiceRecording, 
    OrderDocument, OrderStatusHistory
)

class OrderSerializer(serializers.ModelSerializer):
    """
    Order serializer
    """
    user_email = serializers.ReadOnlyField(source='user.email')
    assigned_to_email = serializers.ReadOnlyField(source='assigned_to.email')
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'order_type', 'status', 'priority',
            'conversation', 'assigned_to', 'assigned_to_email', 'created_at',
            'updated_at', 'completed_at', 'metadata', 'duration'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'duration']

class ConversationSerializer(serializers.ModelSerializer):
    """
    Conversation serializer
    """
    user_email = serializers.ReadOnlyField(source='user.email')
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'user_email', 'conversation_type', 'status',
            'started_at', 'ended_at', 'duration', 'metadata', 'message_count'
        ]
        read_only_fields = ['id', 'started_at', 'ended_at', 'duration']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class MessageSerializer(serializers.ModelSerializer):
    """
    Message serializer
    """
    sender_email = serializers.ReadOnlyField(source='sender.email')
    is_from_user = serializers.ReadOnlyField()
    is_from_ai = serializers.ReadOnlyField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender_type', 'sender', 'sender_email',
            'message_type', 'content', 'file_url', 'file_size', 'file_type',
            'created_at', 'processed_at', 'metadata', 'is_from_user', 'is_from_ai'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']

class VoiceRecordingSerializer(serializers.ModelSerializer):
    """
    Voice recording serializer
    """
    message_content = serializers.ReadOnlyField(source='message.content')
    
    class Meta:
        model = VoiceRecording
        fields = [
            'id', 'message', 'message_content', 'audio_file', 'duration',
            'transcript', 'language', 'confidence_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class VoiceRecordingUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading raw voice recordings
    """
    audio_file = serializers.FileField()
    duration = serializers.FloatField(required=False)
    
    def validate_audio_file(self, value):
        allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/webm']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(f"Invalid audio format. Allowed: {', '.join(allowed_types)}")
        
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Audio file size must be less than 5MB")
        
        return value

class OrderDocumentSerializer(serializers.ModelSerializer):
    """
    Order document serializer
    """
    uploaded_by_email = serializers.ReadOnlyField(source='uploaded_by.email')
    file_url = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderDocument
        fields = [
            'id', 'order', 'document_type', 'file', 'original_name',
            'file_size', 'mime_type', 'uploaded_by', 'uploaded_by_email',
            'created_at', 'is_verified', 'verification_notes', 'file_url'
        ]
        read_only_fields = ['id', 'created_at', 'file_url']

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """
    Order status history serializer
    """
    changed_by_email = serializers.ReadOnlyField(source='changed_by.email')
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'order', 'old_status', 'new_status',
            'changed_by', 'changed_by_email', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

# Chat specific serializers
class ChatMessageSerializer(serializers.Serializer):
    """
    Chat message serializer
    """
    message = serializers.CharField()
    context = serializers.JSONField(required=False, default=dict)
    
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()

class WorkflowChatMessageSerializer(serializers.Serializer):
    """
    Chat message serializer for workflow endpoints
    """
    conversation_id = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False, allow_blank=True)
    order_type = serializers.CharField(required=False, default='general')
    
    def validate_message(self, value):
        return value.strip()

class VoiceMessageSerializer(serializers.Serializer):
    """
    Voice message serializer
    """
    audio_file = serializers.FileField()
    
    def validate_audio_file(self, value):
        # Validate file type
        allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/webm']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(f"Invalid audio format. Allowed: {', '.join(allowed_types)}")
        
        # Validate file size (5MB limit)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Audio file size must be less than 5MB")
        
        return value

class WorkflowVoiceMessageSerializer(VoiceMessageSerializer):
    """
    Voice message serializer for workflow endpoints
    """
    conversation_id = serializers.IntegerField(required=False)
    order_type = serializers.CharField(required=False, default='general')

# Analytics serializers
class ConversationAnalyticsSerializer(serializers.ModelSerializer):
    """
    Conversation analytics serializer
    """
    class Meta:
        model = Conversation
        fields = ['id', 'user', 'conversation_type', 'status', 'started_at', 'ended_at', 'duration']

class OrderAnalyticsSerializer(serializers.ModelSerializer):
    """
    Order analytics serializer
    """
    class Meta:
        model = Order
        fields = ['id', 'user', 'order_type', 'status', 'priority', 'created_at', 'completed_at']