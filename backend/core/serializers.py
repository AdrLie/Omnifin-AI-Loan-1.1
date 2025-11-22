from rest_framework import serializers
from .models import (
    Group, APIConfiguration, SystemSetting, FileUpload,
    Notification, AuditLog
)

class GroupSerializer(serializers.ModelSerializer):
    """
    Group serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'created_at', 'created_by',
            'created_by_email', 'is_active', 'settings', 'user_count'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_email', 'user_count']
    
    def get_user_count(self, obj):
        return obj.users.count()

class APIConfigurationSerializer(serializers.ModelSerializer):
    """
    API Configuration serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = APIConfiguration
        fields = [
            'id', 'name', 'api_type', 'provider', 'endpoint_url',
            'configuration', 'is_active', 'group', 'created_by',
            'created_by_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by_email', 'created_at', 'updated_at']
    
    def validate_api_key_encrypted(self, value):
        """Validate API key encryption"""
        if value and len(value) < 10:
            raise serializers.ValidationError("API key seems too short")
        return value
    
    def to_representation(self, instance):
        """Hide sensitive data in response"""
        ret = super().to_representation(instance)
        # Remove sensitive fields from response
        ret.pop('api_key_encrypted', None)
        return ret

class SystemSettingSerializer(serializers.ModelSerializer):
    """
    System setting serializer
    """
    class Meta:
        model = SystemSetting
        fields = [
            'id', 'key', 'value', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_key(self, value):
        """Validate key format"""
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Key must contain only alphanumeric characters, underscores, and hyphens")
        return value

class FileUploadSerializer(serializers.ModelSerializer):
    """
    File upload serializer
    """
    uploaded_by_email = serializers.ReadOnlyField(source='uploaded_by.email')
    file_url = serializers.ReadOnlyField()
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'file', 'original_name', 'file_type', 'file_size',
            'mime_type', 'uploaded_by', 'uploaded_by_email', 'group',
            'created_at', 'metadata', 'file_url'
        ]
        read_only_fields = ['id', 'created_at', 'file_url']
    
    def validate_file(self, value):
        """Validate uploaded file"""
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("File size must be less than 5MB")
        
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'text/plain', 'application/json'
        ]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Invalid file type")
        
        return value

class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification serializer
    """
    user_email = serializers.ReadOnlyField(source='user.email')
    group_name = serializers.ReadOnlyField(source='group.name')
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'user',
            'user_email', 'group', 'group_name', 'is_read', 'created_at',
            'expires_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']

class AuditLogSerializer(serializers.ModelSerializer):
    """
    Audit log serializer
    """
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action', 'resource_type',
            'resource_id', 'details', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']