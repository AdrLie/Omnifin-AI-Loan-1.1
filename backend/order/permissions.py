from rest_framework import permissions

class IsOrderOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to access orders
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'superadmin']:
            return True
        return obj.user == request.user

class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow conversation participants or admins
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'superadmin']:
            return True
        return obj.user == request.user

class CanManageOrder(permissions.BasePermission):
    """
    Custom permission to check if user can manage orders
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'superadmin':
            return True
        if request.user.role == 'admin':
            return obj.user.group == request.user.group
        return obj.user == request.user