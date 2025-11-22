from rest_framework import serializers
from .models import (
    KnowledgeEntry, KnowledgeVersion, Prompt, PromptVersion,
    TrainingData, AIModelPerformance, FAQ
)


class KnowledgeEntrySerializer(serializers.ModelSerializer):
    """
    Knowledge Entry serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = KnowledgeEntry
        fields = [
            'id', 'title', 'content', 'category', 'subcategory', 'tags',
            'group', 'created_by', 'created_by_email', 'is_active', 'version',
            'created_at', 'updated_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_email', 'version']


class KnowledgeVersionSerializer(serializers.ModelSerializer):
    """
    Knowledge Version serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = KnowledgeVersion
        fields = [
            'id', 'knowledge_entry', 'version', 'title', 'content',
            'change_summary', 'created_by', 'created_by_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_email']


class PromptSerializer(serializers.ModelSerializer):
    """
    Prompt serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Prompt
        fields = [
            'id', 'name', 'category', 'prompt_type', 'content', 'variables',
            'group', 'created_by', 'created_by_email', 'is_active', 'version',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_email', 'version']


class PromptVersionSerializer(serializers.ModelSerializer):
    """
    Prompt Version serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = PromptVersion
        fields = [
            'id', 'prompt', 'version', 'content', 'change_summary',
            'created_by', 'created_by_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_email']


class TrainingDataSerializer(serializers.ModelSerializer):
    """
    Training Data serializer
    """
    validated_by_email = serializers.ReadOnlyField(source='validated_by.email')
    
    class Meta:
        model = TrainingData
        fields = [
            'id', 'data_type', 'input_text', 'expected_output', 'intent',
            'entities', 'confidence_score', 'group', 'is_used_for_training',
            'created_at', 'validated_at', 'validated_by', 'validated_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'validated_by_email']


class AIModelPerformanceSerializer(serializers.ModelSerializer):
    """
    AI Model Performance serializer
    """
    class Meta:
        model = AIModelPerformance
        fields = [
            'id', 'model_name', 'metric_type', 'metric_value', 'test_data_size',
            'group', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class FAQSerializer(serializers.ModelSerializer):
    """
    FAQ serializer
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category', 'tags', 'group',
            'is_active', 'view_count', 'created_by', 'created_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_email', 'view_count']
