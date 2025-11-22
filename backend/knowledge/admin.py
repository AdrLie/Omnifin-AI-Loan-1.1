from django.contrib import admin
from .models import (
    KnowledgeEntry, KnowledgeVersion, Prompt, PromptVersion,
    TrainingData, AIModelPerformance, FAQ
)

@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'version', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['version', 'created_at', 'updated_at']

@admin.register(KnowledgeVersion)
class KnowledgeVersionAdmin(admin.ModelAdmin):
    list_display = ['knowledge_entry', 'version', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['knowledge_entry__title', 'change_summary']
    readonly_fields = ['created_at']

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'prompt_type', 'is_active', 'version', 'created_at']
    list_filter = ['category', 'prompt_type', 'is_active', 'created_at']
    search_fields = ['name', 'content']
    readonly_fields = ['version', 'created_at', 'updated_at']

@admin.register(PromptVersion)
class PromptVersionAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'version', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['prompt__name', 'change_summary']
    readonly_fields = ['created_at']

@admin.register(TrainingData)
class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ['data_type', 'intent', 'is_used_for_training', 'created_at']
    list_filter = ['data_type', 'is_used_for_training', 'created_at']
    search_fields = ['input_text', 'expected_output', 'intent']
    readonly_fields = ['created_at', 'validated_at']

@admin.register(AIModelPerformance)
class AIModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'metric_type', 'metric_value', 'created_at']
    list_filter = ['model_name', 'metric_type', 'created_at']
    search_fields = ['model_name', 'metric_type']
    readonly_fields = ['created_at']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active', 'view_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    readonly_fields = ['created_at', 'updated_at']