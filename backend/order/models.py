from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Order(models.Model):
    """
    Order model for loan and insurance requests
    """
    ORDER_TYPE_CHOICES = [
        ('loan', _('Loan')),
        ('insurance', _('Insurance')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('on_hold', _('On Hold')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(_('order type'), max_length=20, choices=ORDER_TYPE_CHOICES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(_('priority'), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    conversation = models.OneToOneField('Conversation', on_delete=models.CASCADE, null=True, blank=True, related_name='order')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'orders_order'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_type.title()} - {self.user.email} - {self.status}"
    
    @property
    def duration(self):
        """Calculate order duration"""
        if self.completed_at:
            return self.completed_at - self.created_at
        return None

class Conversation(models.Model):
    """
    Conversation model for chat and voice interactions
    """
    CONVERSATION_TYPE_CHOICES = [
        ('chat', _('Text Chat')),
        ('voice', _('Voice Chat')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('ended', _('Ended')),
        ('transferred', _('Transferred')),
        ('waiting', _('Waiting')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    conversation_type = models.CharField(_('conversation type'), max_length=10, choices=CONVERSATION_TYPE_CHOICES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    ended_at = models.DateTimeField(_('ended at'), null=True, blank=True)
    duration = models.IntegerField(_('duration (seconds)'), null=True, blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'orders_conversation'
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.conversation_type.title()} - {self.user.email} - {self.status}"
    
    def end_conversation(self):
        """End the conversation and calculate duration"""
        from django.utils import timezone
        
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.duration = int((self.ended_at - self.started_at).total_seconds())
            self.status = 'ended'
            self.save()

class Message(models.Model):
    """
    Message model for conversation messages
    """
    SENDER_TYPE_CHOICES = [
        ('user', _('User')),
        ('ai', _('AI Assistant')),
        ('agent', _('Human Agent')),
        ('system', _('System')),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('text', _('Text')),
        ('image', _('Image')),
        ('audio', _('Audio')),
        ('file', _('File')),
        ('video', _('Video')),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(_('sender type'), max_length=10, choices=SENDER_TYPE_CHOICES)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message_type = models.CharField(_('message type'), max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(_('content'))
    file_url = models.URLField(_('file URL'), blank=True)
    file_size = models.IntegerField(_('file size'), null=True, blank=True)
    file_type = models.CharField(_('file type'), max_length=50, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'orders_message'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender_type.title()} - {self.conversation.id} - {self.created_at}"
    
    @property
    def is_from_user(self):
        return self.sender_type == 'user'
    
    @property
    def is_from_ai(self):
        return self.sender_type == 'ai'

class VoiceRecording(models.Model):
    """
    Voice recording model for voice conversations
    """
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='voice_recording')
    audio_file = models.FileField(_('audio file'), upload_to='voice_recordings/%Y/%m/%d/')
    duration = models.IntegerField(_('duration (seconds)'))
    transcript = models.TextField(_('transcript'), blank=True)
    language = models.CharField(_('language'), max_length=10, default='en')
    confidence_score = models.FloatField(_('confidence score'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'orders_voicerecording'
        verbose_name = _('Voice Recording')
        verbose_name_plural = _('Voice Recordings')
    
    def __str__(self):
        return f"Voice Recording - {self.message.id} - {self.duration}s"

class OrderDocument(models.Model):
    """
    Documents attached to orders
    """
    DOCUMENT_TYPE_CHOICES = [
        ('identity', _('Identity Proof')),
        ('income', _('Income Proof')),
        ('address', _('Address Proof')),
        ('other', _('Other')),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(_('document type'), max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(_('file'), upload_to='order_documents/%Y/%m/%d/')
    original_name = models.CharField(_('original name'), max_length=255)
    file_size = models.IntegerField(_('file size'))
    mime_type = models.CharField(_('MIME type'), max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    is_verified = models.BooleanField(_('is verified'), default=False)
    verification_notes = models.TextField(_('verification notes'), blank=True)
    
    class Meta:
        db_table = 'orders_orderdocument'
        verbose_name = _('Order Document')
        verbose_name_plural = _('Order Documents')
    
    def __str__(self):
        return f"{self.document_type.title()} - {self.order.id}"

class OrderStatusHistory(models.Model):
    """
    History of order status changes
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(_('old status'), max_length=20)
    new_status = models.CharField(_('new status'), max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('changed at'), auto_now_add=True)
    
    class Meta:
        db_table = 'orders_orderstatushistory'
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.id} - {self.old_status} → {self.new_status}"