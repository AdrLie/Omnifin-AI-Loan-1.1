from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserProfileView, UserProfileUpdateView, PasswordChangeView,
    UserListView, UserDetailView, UserPermissionListView,
    UserPermissionDetailView, get_current_user, check_permission
)

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    
    # User Management (Admin only)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/permissions/', UserPermissionListView.as_view(), name='user-permissions'),
    path('users/<int:user_id>/permissions/<int:pk>/', UserPermissionDetailView.as_view(), name='user-permission-detail'),
    
    # Utility
    path('me/', get_current_user, name='current-user'),
    path('check-permission/', check_permission, name='check-permission'),
]