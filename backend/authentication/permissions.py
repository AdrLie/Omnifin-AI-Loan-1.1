from rest_framework import permissions

class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin or superadmin users
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'superadmin']

class CanManageUser(permissions.BasePermission):
    """
    Custom permission to check if user can manage another user
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'superadmin':
            return True
        if user.role == 'admin' and obj.group == user.group:
            return obj.role in ['simple', 'super']
        return False

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to access objects
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'superadmin']:
            return True
        return obj.user == request.user

class IsGroupMember(permissions.BasePermission):
    """
    Custom permission to only allow group members to access group resources
    """
    
    def has_permission(self, request, view):
        if request.user.role == 'superadmin':
            return True
        group_id = view.kwargs.get('group_id')
        if group_id:
            return request.user.group_id == int(group_id)
        return True