from rest_framework import permissions

class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin or superadmin users
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'superadmin']

class CanManageGroup(permissions.BasePermission):
    """
    Custom permission to check if user can manage group resources
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'superadmin':
            return True
        if hasattr(obj, 'group'):
            return obj.group == request.user.group
        return False