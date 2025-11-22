from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import User, UserPermission, UserSession
from django.shortcuts import get_object_or_404
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    PasswordChangeSerializer, UserPermissionSerializer, UserProfileUpdateSerializer
)
from .permissions import IsAdminOrSuperAdmin, CanManageUser
from analytics.models import UserActivity
import logging

logger = logging.getLogger(__name__)

class UserRegistrationView(generics.CreateAPIView):
    """
    User registration view
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        # Track user registration activity
        UserActivity.objects.create(
            user=user,
            action='create',
            resource_type='user',
            resource_id=user.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={'registration_method': 'api'}
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully.'
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    """
    User login view
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        
        # Update last login
        user.last_login = user.__class__.objects.get(id=user.id).last_login
        
        # Create session record
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'user': user,
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
        
        # Log the login
        logger.info(f"User {user.email} logged in from {request.META.get('REMOTE_ADDR')}")
        
        # Track login activity
        UserActivity.objects.create(
            user=user,
            action='login',
            resource_type='auth',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=session_key or ''
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful.'
        }, status=status.HTTP_200_OK)

class UserLogoutView(generics.GenericAPIView):
    """
    User logout view
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            # Delete token
            request.user.auth_token.delete()
            
            # Update session
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(session_key=session_key).update(is_active=False)
            
            # Log the logout
            logger.info(f"User {request.user.email} logged out")
            
            # Track logout activity
            UserActivity.objects.create(
                user=request.user,
                action='logout',
                resource_type='auth',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({'message': 'Logout failed.'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.UpdateAPIView):
    """
    User profile update view
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'user': UserSerializer(instance).data,
            'message': 'Profile updated successfully.'
        })

class PasswordChangeView(generics.GenericAPIView):
    """
    Password change view
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Update token
        Token.objects.filter(user=user).delete()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Password changed successfully.',
            'token': token.key
        }, status=status.HTTP_200_OK)

class UserListView(generics.ListAPIView):
    """
    List all users (Admin/SuperAdmin only)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return User.objects.all()
        elif user.role == 'admin':
            return User.objects.filter(group=user.group)
        return User.objects.none()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'users': serializer.data,
            'total': queryset.count()
        })

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    User detail view (Admin/SuperAdmin only)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSuperAdmin, CanManageUser]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return User.objects.all()
        elif user.role == 'admin':
            return User.objects.filter(group=user.group)
        return User.objects.none()
    
    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(f"User {self.request.user.email} updated user {instance.email}")
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        logger.info(f"User {self.request.user.email} deactivated user {instance.email}")

class UserPermissionListView(generics.ListCreateAPIView):
    """
    User permission management
    """
    serializer_class = UserPermissionSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return UserPermission.objects.filter(user_id=user_id)
    
    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        serializer.save(
            user_id=user_id,
            granted_by=self.request.user
        )
        logger.info(f"Permission {serializer.instance.permission} granted to user {user_id}")

class UserPermissionDetailView(generics.DestroyAPIView):
    """
    User permission detail view
    """
    serializer_class = UserPermissionSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return UserPermission.objects.filter(user_id=user_id)
    
    def perform_destroy(self, instance):
        permission = instance.permission
        user_id = instance.user_id
        instance.delete()
        logger.info(f"Permission {permission} revoked from user {user_id}")

class AdminUserListCreateView(generics.GenericAPIView):
    """
    Workflow endpoint: /api/admin/users
    """
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get_queryset(self, request):
        if request.user.role == 'superadmin':
            return User.objects.all()
        return User.objects.filter(group=request.user.group)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        serializer = UserSerializer(queryset, many=True)
        return Response({
            'users': serializer.data,
            'total': queryset.count()
        })
    
    def post(self, request, *args, **kwargs):
        registration_serializer = UserRegistrationSerializer(data=request.data)
        registration_serializer.is_valid(raise_exception=True)
        user = registration_serializer.save()
        
        # Optional admin-specific fields
        role = request.data.get('role')
        if role:
            user.role = role
        group_id = request.data.get('group')
        if group_id:
            user.group_id = group_id
        if 'is_staff' in request.data:
            user.is_staff = request.data.get('is_staff') in [True, 'true', 'True', '1']
        if 'is_superuser' in request.data:
            user.is_superuser = request.data.get('is_superuser') in [True, 'true', 'True', '1']
        user.save()
        
        logger.info(f"Admin {request.user.email} created user {user.email}")
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User created successfully.'
        }, status=status.HTTP_201_CREATED)

class AdminUserDetailView(generics.GenericAPIView):
    """
    Workflow endpoint: /api/admin/users/{id}
    """
    permission_classes = [IsAdminOrSuperAdmin, CanManageUser]
    
    def get_object(self, user_id):
        return get_object_or_404(User, id=user_id)
    
    def put(self, request, user_id):
        user = self.get_object(user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Admin {request.user.email} updated user {user.email}")
        return Response({
            'user': serializer.data,
            'message': 'User updated successfully.'
        })
    
    def delete(self, request, user_id):
        user = self.get_object(user_id)
        user.is_active = False
        user.save()
        logger.info(f"Admin {request.user.email} deactivated user {user.email}")
        return Response({'message': 'User deactivated successfully.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_permission(request):
    """
    Check if user has specific permission
    """
    permission = request.data.get('permission')
    if not permission:
        return Response({'error': 'Permission required'}, status=status.HTTP_400_BAD_REQUEST)
    
    has_permission = request.user.has_permission(permission)
    return Response({
        'permission': permission,
        'has_permission': has_permission
    })