from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Group(models.Model):
    """
    User group model for organization and permissions
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_groups')
    is_active = models.BooleanField(_('is active'), default=True)
    settings = models.JSONField(_('settings'), default=dict, blank=True)
    
    class Meta:
        db_table = 'groups_group'
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
    
    def __str__(self):
        return self.name

class APIConfiguration(models.Model):
    """
    API configuration for external services
    """
    API_TYPE_CHOICES = [
        ('llm_text', _('LLM Text API')),
        ('llm_voice', _('LLM Voice API')),
        ('crm', _('CRM System')),
        ('erp', _('ERP System')),
    ]
    
    PROVIDER_CHOICES = [
        ('openai', _('OpenAI')),
        ('anthropic', _('Anthropic')),
        ('elevenlabs', _('ElevenLabs')),
        ('custom', _('Custom Provider')),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    api_type = models.CharField(_('API type'), max_length=20, choices=API_TYPE_CHOICES)
    provider = models.CharField(_('provider'), max_length=50, choices=PROVIDER_CHOICES)
    endpoint_url = models.URLField(_('endpoint URL'), blank=True)
    api_key_encrypted = models.TextField(_('API key (encrypted)'))
    configuration = models.JSONField(_('configuration'), default=dict, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'core_apiconfiguration'
        verbose_name = _('API Configuration')
        verbose_name_plural = _('API Configurations')
        unique_together = ['name', 'group']
    
    def __str__(self):
        return f"{self.name} ({self.provider})"

class SystemSetting(models.Model):
    """
    System-wide settings
    """
    key = models.CharField(_('key'), max_length=100, unique=True)
    value = models.TextField(_('value'))
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'core_systemsetting'
        verbose_name = _('System Setting')
        verbose_name_plural = _('System Settings')
    
    def __str__(self):
        return self.key

class FileUpload(models.Model):
    """
    File upload model for images and documents
    """
    FILE_TYPE_CHOICES = [
        ('image', _('Image')),
        ('document', _('Document')),
        ('audio', _('Audio')),
        ('video', _('Video')),
    ]
    
    file = models.FileField(_('file'), upload_to='uploads/%Y/%m/%d/')
    original_name = models.CharField(_('original name'), max_length=255)
    file_type = models.CharField(_('file type'), max_length=20, choices=FILE_TYPE_CHOICES)
    file_size = models.IntegerField(_('file size'))
    mime_type = models.CharField(_('MIME type'), max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'core_fileupload'
        verbose_name = _('File Upload')
        verbose_name_plural = _('File Uploads')
    
    def __str__(self):
        return self.original_name
    
    @property
    def file_url(self):
        return self.file.url if self.file else None

class Notification(models.Model):
    """
    System notifications
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('info', _('Information')),
        ('warning', _('Warning')),
        ('error', _('Error')),
        ('success', _('Success')),
    ]
    
    title = models.CharField(_('title'), max_length=200)
    message = models.TextField(_('message'))
    notification_type = models.CharField(_('type'), max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(_('is read'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'core_notification'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class AuditLog(models.Model):
    """
    Audit log for tracking important actions
    """
    ACTION_CHOICES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('permission_grant', _('Permission Grant')),
        ('permission_revoke', _('Permission Revoke')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(_('action'), max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(_('resource type'), max_length=50, blank=True)
    resource_id = models.IntegerField(_('resource ID'), null=True, blank=True)
    details = models.JSONField(_('details'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'core_auditlog'
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.action} at {self.created_at}"