import logging
import openai
from django.conf import settings
from django.db import models, OperationalError, ProgrammingError
from knowledge.models import Prompt, KnowledgeEntry
from .models import Message, Conversation

logger = logging.getLogger(__name__)

class AIProcessingService:
    """
    Service for processing messages with AI and generating responses
    """
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def get_welcome_message(self, order_type='general'):
        """Get welcome message based on order type"""
        try:
            prompt = Prompt.objects.get(
                name='welcome_message',
                category=order_type,
                is_active=True
            )
            return prompt.render(order_type=order_type)
        except Prompt.DoesNotExist:
            return f"Welcome to Omnifin! I'm here to help you with {order_type}. How can I assist you today?"
        except (OperationalError, ProgrammingError) as db_error:
            logger.warning(
                "Prompt table unavailable while fetching welcome message: %s",
                db_error
            )
            return f"Welcome to Omnifin! I'm here to help you with {order_type}. How can I assist you today?"
    
    def process_chat_message(self, conversation, message, user):
        """Process a chat message and generate AI response"""
        try:
            # Get context from conversation history
            context = self._get_conversation_context(conversation)
            
            # Get relevant knowledge
            knowledge = self._get_relevant_knowledge(message, user.group)
            
            # Generate AI response
            response = self._generate_ai_response(message, context, knowledge)
            
            # Extract intent and entities
            intent, entities = self._extract_intent_and_entities(message)
            
            return {
                'response': response,
                'intent': intent,
                'entities': entities,
                'metadata': {
                    'knowledge_used': knowledge,
                    'confidence': 0.8,
                    'processing_time': 1.2
                }
            }
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return {
                'response': "I apologize, but I'm having trouble processing your request. Please try again.",
                'intent': 'error',
                'entities': {},
                'metadata': {'error': str(e)}
            }
    
    def _get_conversation_context(self, conversation, limit=5):
        """Get recent conversation context"""
        recent_messages = conversation.messages.filter(
            sender_type__in=['user', 'ai']
        ).order_by('-created_at')[:limit]
        
        context = []
        for msg in reversed(recent_messages):
            context.append({
                'role': 'user' if msg.sender_type == 'user' else 'assistant',
                'content': msg.content
            })
        
        return context
    
    def _get_relevant_knowledge(self, message, group):
        """Get relevant knowledge entries for the message"""
        # Simple keyword matching for now
        keywords = message.lower().split()
        
        try:
            knowledge_entries = KnowledgeEntry.objects.filter(
                is_active=True
            ).filter(
                models.Q(group=group) | models.Q(group__isnull=True)
            )
        except (OperationalError, ProgrammingError) as db_error:
            logger.warning(
                "Knowledge tables unavailable while fetching relevant knowledge: %s",
                db_error
            )
            return []
        
        relevant_knowledge = []
        for entry in knowledge_entries:
            entry_text = (entry.title + ' ' + entry.content).lower()
            if any(keyword in entry_text for keyword in keywords):
                relevant_knowledge.append({
                    'title': entry.title,
                    'content': entry.content,
                    'category': entry.category
                })
        
        return relevant_knowledge[:3]  # Limit to top 3 relevant entries
    
    def _generate_ai_response(self, message, context, knowledge):
        """Generate AI response using OpenAI API or fallback"""
        if not settings.OPENAI_API_KEY:
            return self._fallback_ai_response(message, knowledge)
        
        try:
            # Prepare system prompt
            system_prompt = """You are an AI assistant for Omnifin, a financial services platform. 
            You help users with loans and insurance inquiries. Be helpful, professional, and accurate."""
            
            # Add knowledge context
            if knowledge:
                knowledge_text = "\n".join([k['content'] for k in knowledge])
                system_prompt += f"\n\nRelevant information:\n{knowledge_text}"
            
            # Prepare messages
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(context)
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._fallback_ai_response(message, knowledge)
    
    def _extract_intent_and_entities(self, message):
        """Extract intent and entities from message"""
        # Simple intent classification
        message_lower = message.lower()
        
        intents = {
            'loan_inquiry': ['loan', 'borrow', 'lend', 'credit'],
            'insurance_inquiry': ['insurance', 'policy', 'coverage', 'claim'],
            'general_info': ['information', 'help', 'what', 'how'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
            'goodbye': ['bye', 'goodbye', 'see you', 'thanks']
        }
        
        detected_intent = 'general_info'
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intent = intent
                break
        
        # Simple entity extraction
        entities = {
            'amount': self._extract_amount(message),
            'timeframe': self._extract_timeframe(message),
            'contact_info': self._extract_contact_info(message)
        }
        
        return detected_intent, entities
    
    def _extract_amount(self, message):
        """Extract monetary amounts from message"""
        import re
        amounts = re.findall(r'\$?\d+(?:,\d{3})*(?:\.\d{2})?', message)
        return amounts[0] if amounts else None
    
    def _extract_timeframe(self, message):
        """Extract timeframes from message"""
        import re
        time_patterns = r'\b(\d+)\s*(days?|weeks?|months?|years?)\b'
        matches = re.findall(time_patterns, message, re.IGNORECASE)
        return matches[0] if matches else None
    
    def _extract_contact_info(self, message):
        """Extract contact information from message"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        emails = re.findall(email_pattern, message)
        phones = re.findall(phone_pattern, message)
        
        return {
            'emails': emails,
            'phones': phones
        }

    def _fallback_ai_response(self, message, knowledge):
        """Generate a simple deterministic response when LLM is unavailable"""
        knowledge_snippet = ""
        if knowledge:
            primary = knowledge[0]
            knowledge_snippet = f"\n\nHere's something related that may help: {primary['title']} - {primary['content']}"
        
        return (
            "Thanks for reaching out to Omnifin. I'm currently running in offline mode, "
            "so this is a simplified response. "
            f"You said: \"{message}\".{knowledge_snippet}\n\n"
            "If you need more detailed assistance, please provide a bit more context and I'll do my best to help."
        )

class VoiceProcessingService:
    """
    Service for processing voice recordings and speech-to-text
    """
    
    def process_voice_message(self, audio_file, conversation, user):
        """Process voice message and return response"""
        try:
            # Simulate voice processing
            import time
            time.sleep(2)  # Simulate processing time
            
            # Mock transcript
            transcript = "This is a demo transcript of your voice message."
            
            # Mock AI response
            ai_response = f"I heard you say: '{transcript}'. How can I help you with that?"
            
            return {
                'success': True,
                'transcript': transcript,
                'ai_response': ai_response,
                'confidence': 0.85,
                'processing_time': 2.1
            }
        except Exception as e:
            logger.error(f"Error processing voice message: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_recording(self, audio_file, user, duration=None):
        """Process voice recording and extract transcript"""
        try:
            # Simulate speech-to-text processing
            transcript = "Demo transcript from voice recording"
            
            if duration is None:
                duration = 5
            else:
                try:
                    duration = round(float(duration), 2)
                except (TypeError, ValueError):
                    duration = 5
            
            return {
                'transcript': transcript,
                'duration': duration,
                'language': 'en',
                'confidence_score': 0.9,
                'ai_response': f"I processed your {duration}-second voice note. Here's what I heard: \"{transcript}\""
            }
        except Exception as e:
            logger.error(f"Error processing recording: {str(e)}")
            raise e