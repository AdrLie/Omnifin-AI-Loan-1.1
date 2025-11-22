from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class KnowledgeEntry(models.Model):
    """
    Knowledge base entries for AI training and responses
    """
    CATEGORY_CHOICES = [
        ('loan', _('Loan Information')),
        ('insurance', _('Insurance Information')),
        ('general', _('General Information')),
        ('procedure', _('Procedures')),
        ('faq', _('Frequently Asked Questions')),
        ('policy', _('Policies')),
        ('compliance', _('Compliance')),
    ]
    
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    category = models.CharField(_('category'), max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(_('subcategory'), max_length=50, blank=True)
    tags = models.JSONField(_('tags'), default=list, blank=True)
    group = models.ForeignKey('core.Group', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    version = models.IntegerField(_('version'), default=1)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'knowledge_knowledgeentry'
        verbose_name = _('Knowledge Entry')
        verbose_name_plural = _('Knowledge Entries')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def save(self, *args, **kwargs):
        if self.pk:
            # Create version history before updating
            try:
                old_instance = KnowledgeEntry.objects.get(pk=self.pk)
                KnowledgeVersion.objects.create(
                    knowledge_entry=self,
                    version=old_instance.version,
                    title=old_instance.title,
                    content=old_instance.content,
                    change_summary="Automatic version on update",
                    created_by=old_instance.created_by
                )
            except KnowledgeEntry.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class KnowledgeVersion(models.Model):
    """
    Version history for knowledge entries
    """
    knowledge_entry = models.ForeignKey(KnowledgeEntry, on_delete=models.CASCADE, related_name='versions')
    version = models.IntegerField(_('version'))
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    change_summary = models.TextField(_('change summary'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'knowledge_knowledgeversion'
        verbose_name = _('Knowledge Version')
        verbose_name_plural = _('Knowledge Versions')
        ordering = ['-version']
        unique_together = ['knowledge_entry', 'version']
    
    def __str__(self):
        return f"{self.knowledge_entry.title} - Version {self.version}"

class Prompt(models.Model):
    """
    LLM prompts for different functions
    """
    PROMPT_TYPE_CHOICES = [
        ('system', _('System Prompt')),
        ('user', _('User Prompt')),
        ('assistant', _('Assistant Prompt')),
        ('instruction', _('Instruction Prompt')),
    ]
    
    CATEGORY_CHOICES = [
        ('loan', _('Loan Processing')),
        ('insurance', _('Insurance Processing')),
        ('general', _('General Chat')),
        ('greeting', _('Greeting')),
        ('closing', _('Closing')),
        ('error', _('Error Handling')),
        ('validation', _('Input Validation')),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    category = models.CharField(_('category'), max_length=50, choices=CATEGORY_CHOICES)
    prompt_type = models.CharField(_('prompt type'), max_length=20, choices=PROMPT_TYPE_CHOICES)
    content = models.TextField(_('content'))
    variables = models.JSONField(_('variables'), default=list, blank=True)
    group = models.ForeignKey('core.Group', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    version = models.IntegerField(_('version'), default=1)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'prompts_prompt'
        verbose_name = _('Prompt')
        verbose_name_plural = _('Prompts')
        ordering = ['-created_at']
        unique_together = ['name', 'group']
    
    def __str__(self):
        return f"{self.name} ({self.category}) - v{self.version}"
    
    def render(self, **kwargs):
        """Render prompt with variables"""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            return f"Error rendering prompt: Missing variable {e}"

class PromptVersion(models.Model):
    """
    Version history for prompts
    """
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='versions')
    version = models.IntegerField(_('version'))
    content = models.TextField(_('content'))
    change_summary = models.TextField(_('change summary'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'prompts_promptversion'
        verbose_name = _('Prompt Version')
        verbose_name_plural = _('Prompt Versions')
        ordering = ['-version']
        unique_together = ['prompt', 'version']
    
    def __str__(self):
        return f"{self.prompt.name} - Version {self.version}"

class TrainingData(models.Model):
    """
    Training data for AI model improvement
    """
    DATA_TYPE_CHOICES = [
        ('conversation', _('Conversation')),
        ('faq', _('FAQ')),
        ('document', _('Document')),
        ('intent', _('Intent Example')),
        ('entity', _('Entity Example')),
    ]
    
    data_type = models.CharField(_('data type'), max_length=20, choices=DATA_TYPE_CHOICES)
    input_text = models.TextField(_('input text'))
    expected_output = models.TextField(_('expected output'), blank=True)
    intent = models.CharField(_('intent'), max_length=100, blank=True)
    entities = models.JSONField(_('entities'), default=dict, blank=True)
    confidence_score = models.FloatField(_('confidence score'), null=True, blank=True)
    group = models.ForeignKey('core.Group', on_delete=models.CASCADE, null=True, blank=True)
    is_used_for_training = models.BooleanField(_('used for training'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    validated_at = models.DateTimeField(_('validated at'), null=True, blank=True)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'knowledge_trainingdata'
        verbose_name = _('Training Data')
        verbose_name_plural = _('Training Data')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.data_type.title()} - {self.intent or 'No Intent'}"

class AIModelPerformance(models.Model):
    """
    Track AI model performance metrics
    """
    model_name = models.CharField(_('model name'), max_length=100)
    metric_type = models.CharField(_('metric type'), max_length=50)
    metric_value = models.FloatField(_('metric value'))
    test_data_size = models.IntegerField(_('test data size'), null=True, blank=True)
    group = models.ForeignKey('core.Group', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        db_table = 'knowledge_aimodelperformance'
        verbose_name = _('AI Model Performance')
        verbose_name_plural = _('AI Model Performances')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.model_name} - {self.metric_type}: {self.metric_value}"

class FAQ(models.Model):
    """
    Frequently Asked Questions
    """
    question = models.TextField(_('question'))
    answer = models.TextField(_('answer'))
    category = models.CharField(_('category'), max_length=50, blank=True)
    tags = models.JSONField(_('tags'), default=list, blank=True)
    group = models.ForeignKey('core.Group', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    view_count = models.IntegerField(_('view count'), default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'knowledge_faq'
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['-view_count', '-created_at']
    
    def __str__(self):
        return f"FAQ: {self.question[:50]}..."
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])