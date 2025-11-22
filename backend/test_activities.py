"""
Script to create test activities for dashboard testing
Run this with: python manage.py shell < test_activities.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omnifin.settings')
django.setup()

from analytics.models import UserActivity
from authentication.models import User
from django.utils import timezone
from datetime import timedelta

# Get or create a test user
user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'customer'
    }
)

if created:
    user.set_password('testpassword123')
    user.save()
    print(f"Created test user: {user.email}")
else:
    print(f"Using existing user: {user.email}")

# Create sample activities
activities = [
    {
        'action': 'login',
        'resource_type': 'auth',
        'created_at': timezone.now() - timedelta(minutes=2)
    },
    {
        'action': 'chat_start',
        'resource_type': 'conversation',
        'resource_id': 1,
        'created_at': timezone.now() - timedelta(minutes=5)
    },
    {
        'action': 'chat_message',
        'resource_type': 'message',
        'resource_id': 1,
        'created_at': timezone.now() - timedelta(minutes=10)
    },
    {
        'action': 'order_created',
        'resource_type': 'order',
        'resource_id': 1,
        'created_at': timezone.now() - timedelta(hours=1)
    },
    {
        'action': 'voice_start',
        'resource_type': 'voice_session',
        'created_at': timezone.now() - timedelta(hours=2)
    },
    {
        'action': 'view',
        'resource_type': 'dashboard',
        'created_at': timezone.now() - timedelta(hours=3)
    },
]

# Delete old test activities for this user
UserActivity.objects.filter(user=user).delete()

# Create new activities
for activity_data in activities:
    UserActivity.objects.create(
        user=user,
        **activity_data
    )
    print(f"Created activity: {activity_data['action']}")

print(f"\n✅ Successfully created {len(activities)} test activities!")
print(f"Total activities in database: {UserActivity.objects.count()}")
