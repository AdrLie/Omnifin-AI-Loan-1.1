from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model with role-based permissions
    """
    
    ROLE_CHOICES = [
        ('simple', _('Simple User')),
        ('super', _('Super User')),
        ('admin', _('Admin User')),
        ('superadmin', _('Super Admin User')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='simple')
    group = models.ForeignKey('core.Group', on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    profile_image = models.ImageField(_('profile image'), upload_to='profiles/', null=True, blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        if self.role == 'superadmin':
            return True
        if self.role == 'admin':
            return permission in ['view_users', 'create_users', 'edit_users', 'manage_group']
        if self.role == 'super':
            return permission in ['view_users', 'edit_own_profile']
        return permission == 'view_own_profile'
    
    def can_manage_user(self, target_user):
        """Check if user can manage another user"""
        if self.role == 'superadmin':
            return True
        if self.role == 'admin' and target_user.group == self.group:
            return target_user.role in ['simple', 'super']
        return False

class UserPermission(models.Model):
    """
    Custom permissions for users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    permission = models.CharField(_('permission'), max_length=100)
    granted_at = models.DateTimeField(_('granted at'), auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    
    class Meta:
        db_table = 'auth_userpermissions'
        unique_together = ['user', 'permission']
        verbose_name = _('User Permission')
        verbose_name_plural = _('User Permissions')
    
    def __str__(self):
        return f"{self.user.email} - {self.permission}"

class UserSession(models.Model):
    """
    User session tracking
    """
    session_key = models.CharField(_('session key'), max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    last_activity = models.DateTimeField(_('last activity'), auto_now=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        db_table = 'analytics_session'
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
    
    def __str__(self):
        return f"{self.session_key} - {self.user.email if self.user else 'Anonymous'}"