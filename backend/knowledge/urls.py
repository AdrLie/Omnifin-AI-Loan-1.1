from django.urls import path
from knowledge.views import (
    # Knowledge Entry
    KnowledgeEntryListView, KnowledgeEntryDetailView,
    KnowledgeEntrySearchView, KnowledgeEntryByCategoryView,
    # Knowledge Version
    KnowledgeVersionListView,
    # Prompts
    PromptListView, PromptDetailView, PromptTestView,
    PromptByCategoryView, PromptSearchView,
    # Prompt Versions
    PromptVersionListView,
    # Training Data
    TrainingDataListView, TrainingDataDetailView,
    # AI Performance
    AIModelPerformanceListView, AIModelPerformanceDetailView,
    # FAQ
    FAQListView, FAQDetailView, FAQSearchView,
    # AI Processing
    AISearchView, AIQueryView, AITrainView,
)

app_name = 'knowledge'

urlpatterns = [
    # Root knowledge endpoints for workflow compatibility
    path('', KnowledgeEntryListView.as_view(), name='knowledge-root'),
    path('<int:pk>/', KnowledgeEntryDetailView.as_view(), name='knowledge-root-detail'),
    
    # Knowledge Entry endpoints
    path('entries/', KnowledgeEntryListView.as_view(), name='knowledge-entry-list'),
    path('entries/<int:pk>/', KnowledgeEntryDetailView.as_view(), name='knowledge-entry-detail'),
    path('entries/search/', KnowledgeEntrySearchView.as_view(), name='knowledge-entry-search'),
    path('entries/category/<str:category>/', KnowledgeEntryByCategoryView.as_view(), name='knowledge-entry-by-category'),
    
    # Knowledge Version endpoints
    path('entries/<int:entry_id>/versions/', KnowledgeVersionListView.as_view(), name='knowledge-version-list'),
    
    # Prompt endpoints
    path('prompts/', PromptListView.as_view(), name='prompt-list'),
    path('prompts/<int:pk>/', PromptDetailView.as_view(), name='prompt-detail'),
    path('prompts/test/', PromptTestView.as_view(), name='prompt-test'),
    path('prompts/category/<str:category>/', PromptByCategoryView.as_view(), name='prompt-by-category'),
    path('prompts/search/', PromptSearchView.as_view(), name='prompt-search'),
    
    # Prompt Version endpoints
    path('prompts/<int:prompt_id>/versions/', PromptVersionListView.as_view(), name='prompt-version-list'),
    
    # Training Data endpoints
    path('training-data/', TrainingDataListView.as_view(), name='training-data-list'),
    path('training-data/<int:pk>/', TrainingDataDetailView.as_view(), name='training-data-detail'),
    
    # AI Performance endpoints
    path('ai-performance/', AIModelPerformanceListView.as_view(), name='ai-performance-list'),
    path('ai-performance/<int:pk>/', AIModelPerformanceDetailView.as_view(), name='ai-performance-detail'),
    
    # FAQ endpoints
    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('faq/<int:pk>/', FAQDetailView.as_view(), name='faq-detail'),
    path('faq/search/', FAQSearchView.as_view(), name='faq-search'),
    
    # AI Processing endpoints
    path('ai/search/', AISearchView.as_view(), name='ai-search'),
    path('ai/query/', AIQueryView.as_view(), name='ai-query'),
    path('ai/train/', AITrainView.as_view(), name='ai-train'),
]