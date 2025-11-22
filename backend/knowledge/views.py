from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import (
    KnowledgeEntry, KnowledgeVersion, Prompt, PromptVersion,
    TrainingData, AIModelPerformance, FAQ
)
from .serializers import (
    KnowledgeEntrySerializer, KnowledgeVersionSerializer,
    PromptSerializer, PromptVersionSerializer,
    TrainingDataSerializer, AIModelPerformanceSerializer,
    FAQSerializer
)


# Knowledge Entry Views
class KnowledgeEntryListView(generics.ListCreateAPIView):
    """
    List and create knowledge entries
    """
    serializer_class = KnowledgeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return KnowledgeEntry.objects.all()
        return KnowledgeEntry.objects.filter(group=user.group)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, group=self.request.user.group)


class KnowledgeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete knowledge entry
    """
    serializer_class = KnowledgeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return KnowledgeEntry.objects.all()
        return KnowledgeEntry.objects.filter(group=user.group)


class KnowledgeEntrySearchView(generics.ListAPIView):
    """
    Search knowledge entries
    """
    serializer_class = KnowledgeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = KnowledgeEntry.objects.all()
        
        if user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(group=user.group)
        
        # Search parameters
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.filter(is_active=True)


class KnowledgeEntryByCategoryView(generics.ListAPIView):
    """
    List knowledge entries by category
    """
    serializer_class = KnowledgeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        category = self.kwargs.get('category')
        
        queryset = KnowledgeEntry.objects.filter(category=category, is_active=True)
        
        if user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(group=user.group)
        
        return queryset


# Knowledge Version Views
class KnowledgeVersionListView(generics.ListAPIView):
    """
    List versions for a knowledge entry
    """
    serializer_class = KnowledgeVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        entry_id = self.kwargs.get('entry_id')
        return KnowledgeVersion.objects.filter(knowledge_entry_id=entry_id)


# Prompt Views
class PromptListView(generics.ListCreateAPIView):
    """
    List and create prompts
    """
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Prompt.objects.all()
        return Prompt.objects.filter(group=user.group)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, group=self.request.user.group)


class PromptDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete prompt
    """
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Prompt.objects.all()
        return Prompt.objects.filter(group=user.group)


class PromptTestView(APIView):
    """
    Test prompt with variables
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        prompt_id = request.data.get('prompt_id')
        variables = request.data.get('variables', {})
        
        prompt = get_object_or_404(Prompt, id=prompt_id)
        rendered = prompt.render(**variables)
        
        return Response({
            'prompt_id': prompt.id,
            'rendered_content': rendered,
            'variables_used': variables
        })


class PromptByCategoryView(generics.ListAPIView):
    """
    List prompts by category
    """
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        category = self.kwargs.get('category')
        
        queryset = Prompt.objects.filter(category=category, is_active=True)
        
        if user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(group=user.group)
        
        return queryset


class PromptSearchView(generics.ListAPIView):
    """
    Search prompts
    """
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Prompt.objects.all()
        
        if user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(group=user.group)
        
        # Search parameters
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(content__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.filter(is_active=True)


# Prompt Version Views
class PromptVersionListView(generics.ListAPIView):
    """
    List versions for a prompt
    """
    serializer_class = PromptVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        prompt_id = self.kwargs.get('prompt_id')
        return PromptVersion.objects.filter(prompt_id=prompt_id)


# Training Data Views
class TrainingDataListView(generics.ListCreateAPIView):
    """
    List and create training data
    """
    serializer_class = TrainingDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return TrainingData.objects.all()
        return TrainingData.objects.filter(group=user.group)
    
    def perform_create(self, serializer):
        serializer.save(group=self.request.user.group)


class TrainingDataDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete training data
    """
    serializer_class = TrainingDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return TrainingData.objects.all()
        return TrainingData.objects.filter(group=user.group)


# AI Performance Views
class AIModelPerformanceListView(generics.ListCreateAPIView):
    """
    List and create AI performance metrics
    """
    serializer_class = AIModelPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return AIModelPerformance.objects.all()
        return AIModelPerformance.objects.filter(group=user.group)
    
    def perform_create(self, serializer):
        serializer.save(group=self.request.user.group)


class AIModelPerformanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete AI performance metric
    """
    serializer_class = AIModelPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return AIModelPerformance.objects.all()
        return AIModelPerformance.objects.filter(group=user.group)


# FAQ Views
class FAQListView(generics.ListCreateAPIView):
    """
    List and create FAQs
    """
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return FAQ.objects.all()
        return FAQ.objects.filter(group=user.group)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, group=self.request.user.group)


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete FAQ
    """
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return FAQ.objects.all()
        return FAQ.objects.filter(group=user.group)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FAQSearchView(generics.ListAPIView):
    """
    Search FAQs
    """
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = FAQ.objects.all()
        
        if user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(group=user.group)
        
        # Search parameters
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        
        if query:
            queryset = queryset.filter(
                Q(question__icontains=query) | Q(answer__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.filter(is_active=True)


# AI Processing Views
class AISearchView(APIView):
    """
    AI-powered search across knowledge base
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        query = request.data.get('query', '')
        
        # Basic search implementation
        # In production, this would use vector search or other AI techniques
        knowledge_results = KnowledgeEntry.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_active=True
        )[:5]
        
        faq_results = FAQ.objects.filter(
            Q(question__icontains=query) | Q(answer__icontains=query),
            is_active=True
        )[:5]
        
        return Response({
            'query': query,
            'knowledge_entries': KnowledgeEntrySerializer(knowledge_results, many=True).data,
            'faqs': FAQSerializer(faq_results, many=True).data
        })


class AIQueryView(APIView):
    """
    AI-powered query processing
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        query = request.data.get('query', '')
        context = request.data.get('context', {})
        
        # Placeholder for AI query processing
        # In production, this would integrate with LLM API
        return Response({
            'query': query,
            'response': 'AI query processing not yet implemented',
            'confidence': 0.0,
            'sources': []
        })


class AITrainView(APIView):
    """
    Trigger AI model training
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Placeholder for training trigger
        # In production, this would trigger a background job
        return Response({
            'message': 'Training job initiated',
            'status': 'pending',
            'job_id': None
        })
