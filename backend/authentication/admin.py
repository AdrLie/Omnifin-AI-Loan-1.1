from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserPermission

class UserPermissionInline(admin.TabularInline):
    model = UserPermission
    fk_name = 'user'
    extra = 0
    readonly_fields = ['granted_at']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'is_verified')}),
        (_('Group info'), {'fields': ('group', 'created_by')}),
        (_('Profile'), {'fields': ('profile_image', 'metadata')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'group', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'group']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login', 'created_by']
    inlines = [UserPermissionInline]

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'granted_by', 'granted_at']
    list_filter = ['permission', 'granted_at']
    search_fields = ['user__username', 'user__email', 'permission']
    readonly_fields = ['granted_at']