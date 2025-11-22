import os
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import FileUpload

logger = logging.getLogger(__name__)

class FileProcessingService:
    """
    Service for handling file uploads and processing
    """
    
    def process_upload(self, file_obj, user):
        """Process uploaded file and return file data"""
        try:
            # Determine file type
            file_type = self._determine_file_type(file_obj.content_type)
            
            # Generate unique filename
            filename = self._generate_filename(file_obj.name)
            
            # Save file
            file_path = default_storage.save(
                f'uploads/{user.id}/{filename}',
                ContentFile(file_obj.read())
            )
            
            return {
                'file': file_path,
                'file_type': file_type,
                'mime_type': file_obj.content_type,
                'group': user.group
            }
        except Exception as e:
            logger.error(f"Error processing file upload: {str(e)}")
            raise e
    
    def _determine_file_type(self, content_type):
        """Determine file type based on content type"""
        if content_type.startswith('image/'):
            return 'image'
        elif content_type == 'application/pdf':
            return 'document'
        elif content_type.startswith('audio/'):
            return 'audio'
        elif content_type.startswith('video/'):
            return 'video'
        else:
            return 'other'
    
    def _generate_filename(self, original_name):
        """Generate unique filename"""
        import uuid
        name, ext = os.path.splitext(original_name)
        return f"{uuid.uuid4().hex}{ext}"

class NotificationService:
    """
    Service for managing notifications
    """
    
    def create_notification(self, title, message, user=None, group=None, notification_type='info'):
        """Create a new notification"""
        from .models import Notification
        
        notification = Notification.objects.create(
            title=title,
            message=message,
            user=user,
            group=group,
            notification_type=notification_type
        )
        
        return notification
    
    def create_user_welcome_notification(self, user):
        """Create welcome notification for new user"""
        return self.create_notification(
            title="Welcome to Omnifin!",
            message=f"Welcome {user.full_name}! Your account has been created successfully. Start by exploring our AI-powered services.",
            user=user,
            notification_type='success'
        )
    
    def create_order_status_notification(self, order, old_status, new_status):
        """Create order status change notification"""
        return self.create_notification(
            title=f"Order #{order.id} Status Updated",
            message=f"Your {order.order_type} order status has been changed from {old_status} to {new_status}.",
            user=order.user,
            notification_type='info'
        )
    
    def mark_all_as_read(self, user):
        """Mark all notifications as read for user"""
        from .models import Notification
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    
    def get_unread_count(self, user):
        """Get count of unread notifications for user"""
        from .models import Notification
        return Notification.objects.filter(user=user, is_read=False).count()