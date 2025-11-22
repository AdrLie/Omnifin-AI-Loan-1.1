from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import (
    Order, Conversation, Message, VoiceRecording, 
    OrderDocument, OrderStatusHistory
)
from .serializers import (
    OrderSerializer, ConversationSerializer, MessageSerializer,
    VoiceRecordingSerializer, OrderDocumentSerializer,
    ChatMessageSerializer, VoiceMessageSerializer,
    VoiceRecordingUploadSerializer, WorkflowChatMessageSerializer,
    WorkflowVoiceMessageSerializer
)
from .permissions import IsOrderOwner, IsConversationParticipant
from .services import AIProcessingService, VoiceProcessingService
from analytics.models import UserActivity
import logging

logger = logging.getLogger(__name__)

# Order Views
class OrderListView(generics.ListCreateAPIView):
    """
    List and create orders
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        
        # Track order creation activity
        UserActivity.objects.create(
            user=self.request.user,
            action='order_created',
            resource_type='order',
            resource_id=order.id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'order_type': order.order_type,
                'product_type': order.product_type,
                'status': order.status
            }
        )

class OrderDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update order details
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Order.objects.all()
        return Order.objects.filter(user=user)

class OrderStatusUpdateView(generics.GenericAPIView):
    """
    Update order status
    """
    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status not in [choice[0] for choice in Order.STATUS_CHOICES]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = order.status
        order.status = new_status
        if new_status == 'completed':
            order.completed_at = timezone.now()
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            notes=notes
        )
        
        # Track order update activity
        UserActivity.objects.create(
            user=request.user,
            action='order_updated',
            resource_type='order',
            resource_id=order.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'old_status': old_status,
                'new_status': new_status,
                'order_type': order.order_type
            }
        )
        
        return Response({'message': 'Status updated successfully'})

# Conversation Views
class ConversationListView(generics.ListCreateAPIView):
    """
    List and create conversations
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Conversation.objects.all()
        return Conversation.objects.filter(user=user)
    
    def perform_create(self, serializer):
        conversation = serializer.save(user=self.request.user)
        
        # Track conversation start activity
        UserActivity.objects.create(
            user=self.request.user,
            action='chat_start',
            resource_type='conversation',
            resource_id=conversation.id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            metadata={'conversation_type': conversation.type}
        )

class ConversationDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update conversation details
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return Conversation.objects.all()
        return Conversation.objects.filter(user=user)

class ConversationEndView(generics.GenericAPIView):
    """
    End a conversation
    """
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        conversation.end_conversation()
        return Response({'message': 'Conversation ended successfully'})

# Message Views
class MessageListView(generics.ListAPIView):
    """
    List messages in a conversation
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id=conversation_id)

class MessageCreateView(generics.CreateAPIView):
    """
    Create a new message
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        message = serializer.save(
            conversation_id=conversation_id,
            sender=self.request.user,
            sender_type='user'
        )
        
        # Track message activity
        UserActivity.objects.create(
            user=self.request.user,
            action='chat_message',
            resource_type='message',
            resource_id=message.id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            metadata={'conversation_id': conversation_id}
        )

class MessageDetailView(generics.RetrieveAPIView):
    """
    Retrieve a message
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def get_queryset(self):
        return Message.objects.all()

# Voice Recording Views
class VoiceRecordingUploadView(generics.GenericAPIView):
    """
    Upload voice recording and return processing result
    """
    serializer_class = VoiceRecordingUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        voice_service = VoiceProcessingService()
        result = voice_service.process_recording(
            serializer.validated_data['audio_file'],
            request.user,
            serializer.validated_data.get('duration')
        )
        
        return Response(result)

class VoiceRecordingDetailView(generics.RetrieveAPIView):
    """
    Retrieve voice recording details
    """
    serializer_class = VoiceRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return VoiceRecording.objects.all()
        return VoiceRecording.objects.filter(message__sender=user)

# Document Views
class OrderDocumentListView(generics.ListCreateAPIView):
    """
    List and upload documents for an order
    """
    serializer_class = OrderDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]
    
    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderDocument.objects.filter(order_id=order_id)
    
    def perform_create(self, serializer):
        order_id = self.kwargs['order_id']
        serializer.save(
            order_id=order_id,
            uploaded_by=self.request.user
        )

class OrderDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a document
    """
    serializer_class = OrderDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]
    
    def get_queryset(self):
        return OrderDocument.objects.all()

# Chat Specific Views
class ChatStartView(generics.GenericAPIView):
    """
    Start a new chat conversation
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        order_type = request.data.get('order_type', 'general')
        
        # Create conversation
        conversation = Conversation.objects.create(
            user=request.user,
            conversation_type='chat',
            metadata={'order_type': order_type}
        )
        
        # Create welcome message
        ai_service = AIProcessingService()
        welcome_message = ai_service.get_welcome_message(order_type)
        
        Message.objects.create(
            conversation=conversation,
            sender_type='ai',
            content=welcome_message
        )
        
        return Response({
            'conversation_id': conversation.id,
            'welcome_message': welcome_message
        })

class ChatMessageView(generics.GenericAPIView):
    """
    Send a message in chat and get AI response
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def post(self, request, conversation_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        message_content = serializer.validated_data['message']
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            sender_type='user',
            content=message_content
        )
        
        # Process with AI
        ai_service = AIProcessingService()
        ai_response = ai_service.process_chat_message(
            conversation=conversation,
            message=message_content,
            user=request.user
        )
        
        # Save AI response
        ai_message = Message.objects.create(
            conversation=conversation,
            sender_type='ai',
            content=ai_response['response'],
            metadata=ai_response['metadata']
        )
        
        return Response({
            'user_message': MessageSerializer(user_message).data,
            'ai_response': MessageSerializer(ai_message).data,
            'intent': ai_response.get('intent'),
            'entities': ai_response.get('entities')
        })

class ChatHistoryView(generics.ListAPIView):
    """
    Get chat history
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id=conversation_id).order_by('created_at')

class ChatMessageWorkflowView(generics.GenericAPIView):
    """
    Workflow endpoint: POST /api/chat/message
    """
    serializer_class = WorkflowChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_type = serializer.validated_data.get('order_type', 'general')
        conversation_id = serializer.validated_data.get('conversation_id')
        message_text = serializer.validated_data.get('message', '')
        
        ai_service = AIProcessingService()
        welcome_message = None
        welcome_obj = None
        
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            if conversation.user != request.user:
                return Response({'detail': 'You do not have access to this conversation.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                conversation_type='chat',
                metadata={'order_type': order_type}
            )
            welcome_message = ai_service.get_welcome_message(order_type)
            welcome_obj = Message.objects.create(
                conversation=conversation,
                sender_type='ai',
                content=welcome_message,
                metadata={'type': 'welcome'}
            )
        
        if not message_text:
            return Response({
                'conversation_id': conversation.id,
                'welcome_message': welcome_message,
                'ai_response': MessageSerializer(welcome_obj).data if welcome_obj else None
            }, status=status.HTTP_201_CREATED if welcome_message else status.HTTP_200_OK)
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            sender_type='user',
            content=message_text
        )
        
        ai_response = ai_service.process_chat_message(
            conversation=conversation,
            message=message_text,
            user=request.user
        )
        
        ai_message = Message.objects.create(
            conversation=conversation,
            sender_type='ai',
            content=ai_response['response'],
            metadata=ai_response.get('metadata', {})
        )
        
        return Response({
            'conversation_id': conversation.id,
            'user_message': MessageSerializer(user_message).data,
            'ai_response': MessageSerializer(ai_message).data,
            'intent': ai_response.get('intent'),
            'entities': ai_response.get('entities')
        })

class ChatHistoryWorkflowView(generics.ListAPIView):
    """
    Workflow endpoint: GET /api/chat/history
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        if not conversation_id:
            return Message.objects.none()
        conversation = get_object_or_404(Conversation, id=conversation_id, user=self.request.user)
        return conversation.messages.order_by('created_at')
    
    def list(self, request, *args, **kwargs):
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response({'detail': 'conversation_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

# Voice Chat Views
class VoiceChatStartView(generics.GenericAPIView):
    """
    Start a voice chat conversation
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        order_type = request.data.get('order_type', 'general')
        
        conversation = Conversation.objects.create(
            user=request.user,
            conversation_type='voice',
            metadata={'order_type': order_type}
        )
        
        # Track voice chat start activity
        UserActivity.objects.create(
            user=request.user,
            action='voice_start',
            resource_type='conversation',
            resource_id=conversation.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={'order_type': order_type}
        )
        
        return Response({
            'conversation_id': conversation.id,
            'message': 'Voice chat started. Ready to receive audio.'
        })

class VoiceMessageView(generics.GenericAPIView):
    """
    Process voice message and return response
    """
    serializer_class = VoiceMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, conversation_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        audio_file = serializer.validated_data['audio_file']
        
        # Process voice
        voice_service = VoiceProcessingService()
        result = voice_service.process_voice_message(
            audio_file=audio_file,
            conversation=conversation,
            user=request.user
        )
        
        return Response(result)

class ChatVoiceWorkflowView(generics.GenericAPIView):
    """
    Workflow endpoint: POST /api/chat/voice
    """
    serializer_class = WorkflowVoiceMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = serializer.validated_data.get('conversation_id')
        order_type = serializer.validated_data.get('order_type', 'general')
        audio_file = serializer.validated_data['audio_file']
        
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            if conversation.user != request.user:
                return Response({'detail': 'You do not have access to this conversation.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                conversation_type='voice',
                metadata={'order_type': order_type}
            )
        
        voice_service = VoiceProcessingService()
        result = voice_service.process_voice_message(
            audio_file=audio_file,
            conversation=conversation,
            user=request.user
        )
        result['conversation_id'] = conversation.id
        return Response(result)

class ChatStatusWorkflowView(generics.GenericAPIView):
    """
    Workflow endpoint: GET /api/chat/status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        conversation_id = request.query_params.get('conversation_id')
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            conversation = Conversation.objects.filter(user=request.user).order_by('-started_at').first()
            if not conversation:
                return Response({'active': False})
        
        data = ConversationSerializer(conversation).data
        data['message_count'] = conversation.messages.count()
        return Response({
            'active': True,
            'conversation': data
        })

# AI Processing Views
class ProcessMessageView(generics.GenericAPIView):
    """
    Process a message with AI (for testing/debugging)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        message = request.data.get('message')
        context = request.data.get('context', {})
        
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = AIProcessingService()
        result = ai_service.process_message(message, context, request.user)
        
        return Response(result)

class GenerateAIResponseView(generics.GenericAPIView):
    """
    Generate AI response for a given prompt
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        prompt = request.data.get('prompt')
        model = request.data.get('model', 'gpt-3.5-turbo')
        
        if not prompt:
            return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = AIProcessingService()
        response = ai_service.generate_response(prompt, model)
        
        return Response({'response': response})