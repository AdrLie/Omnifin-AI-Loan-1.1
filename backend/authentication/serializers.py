from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserPermission

class UserSerializer(serializers.ModelSerializer):
    """
    User model serializer
    """
    full_name = serializers.ReadOnlyField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'phone', 'role', 'group', 'profile_image',
            'is_active', 'is_verified', 'date_joined', 'permissions',
            'metadata'
        ]
        read_only_fields = ['id', 'date_joined', 'permissions']
    
    def get_permissions(self, obj):
        """Get user permissions"""
        return obj.custom_permissions.values_list('permission', flat=True)

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    User login serializer
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        
        return attrs

class PasswordChangeSerializer(serializers.Serializer):
    """
    Password change serializer
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

class UserPermissionSerializer(serializers.ModelSerializer):
    """
    User permission serializer
    """
    granted_by_email = serializers.ReadOnlyField(source='granted_by.email')
    
    class Meta:
        model = UserPermission
        fields = ['id', 'permission', 'granted_at', 'granted_by_email']
        read_only_fields = ['id', 'granted_at', 'granted_by_email']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    User profile update serializer
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'profile_image', 'metadata']
    
    def validate_profile_image(self, value):
        """Validate profile image"""
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError("Image size must be less than 5MB.")
            
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Invalid image format. Allowed: JPEG, PNG, GIF, WebP.")
        
        return value