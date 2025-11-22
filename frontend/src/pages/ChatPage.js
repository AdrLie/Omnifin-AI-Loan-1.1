import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Chip,
  CircularProgress,
  Fab,
  Fade,
  Button,
} from '@mui/material';
import {
  Send,
  Person,
  SmartToy,
  AttachFile,
  Mic,
  Stop,
} from '@mui/icons-material';
import { useNotification } from '../contexts/NotificationContext';
import { chatService } from '../services/chatService';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { showNotification } = useNotification();

  useEffect(() => {
    startConversation();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startConversation = async () => {
    try {
      setLoading(true);
      const response = await chatService.startConversation('loan');
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      
      const welcomeContent = response.welcome_message || response.ai_response?.content;
      if (welcomeContent) {
        setMessages([
          {
            id: Date.now(),
            content: welcomeContent,
            sender: 'ai',
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error) {
      showNotification('Failed to start conversation', 'error');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !conversationId || loading) return;

    const userMessage = {
      id: Date.now(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await chatService.sendMessage(conversationId, inputMessage);
      
      if (response.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id);
      }
      
      const aiMessage = {
        id: Date.now() + 1,
        content: response.ai_response?.content || 'I have received your message.',
        sender: 'ai',
        timestamp: new Date(),
        metadata: response.ai_response?.metadata || response.metadata,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      showNotification('Failed to send message', 'error');
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const MessageBubble = ({ message }) => {
    const isUser = message.sender === 'user';
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'flex-start',
            maxWidth: '70%',
          }}
        >
          {!isUser && (
            <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
              <SmartToy />
            </Avatar>
          )}
          <Paper
            elevation={1}
            sx={{
              p: 2,
              backgroundColor: isUser ? 'primary.main' : 'background.paper',
              color: isUser ? 'white' : 'text.primary',
              borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
            }}
          >
            <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
              {message.content}
            </Typography>
            {message.metadata?.intent && (
              <Chip
                label={message.metadata.intent}
                size="small"
                sx={{ mt: 1 }}
                color="info"
              />
            )}
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 0.5,
                opacity: 0.7,
                color: isUser ? 'rgba(255,255,255,0.8)' : 'text.secondary',
              }}
            >
              {new Date(message.timestamp).toLocaleTimeString()}
            </Typography>
          </Paper>
          {isUser && (
            <Avatar sx={{ ml: 1, bgcolor: 'secondary.main' }}>
              <Person />
            </Avatar>
          )}
        </Box>
      </Box>
    );
  };

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Header */}
      <Paper elevation={2} sx={{ p: 2, mb: 2, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
            <SmartToy />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              AI Assistant
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ready to help with loans and insurance
            </Typography>
          </Box>
          <Box sx={{ ml: 'auto' }}>
            <Chip
              label={isTyping ? 'Typing...' : 'Online'}
              color={isTyping ? 'warning' : 'success'}
              size="small"
            />
          </Box>
        </Box>
      </Paper>

      {/* Messages Container */}
      <Paper
        elevation={1}
        sx={{
          flexGrow: 1,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          borderRadius: 3,
        }}
      >
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isTyping && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
              <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                <SmartToy />
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  borderRadius: '18px 18px 18px 4px',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  AI is typing...
                </Typography>
              </Paper>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              variant="outlined"
              placeholder="Type your message..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: 'background.paper',
                },
              }}
            />
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <IconButton
                color="primary"
                onClick={sendMessage}
                disabled={!inputMessage.trim() || loading}
                sx={{
                  bgcolor: 'primary.main',
                  color: 'white',
                  '&:hover': { bgcolor: 'primary.dark' },
                  '&:disabled': { bgcolor: 'grey.300' },
                }}
              >
                <Send />
              </IconButton>
            </Box>
          </Box>
          
          <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
            <Button
              startIcon={<AttachFile />}
              size="small"
              variant="outlined"
              disabled
              sx={{ textTransform: 'none' }}
            >
              Attach File
            </Button>
            <Button
              startIcon={<Mic />}
              size="small"
              variant="outlined"
              disabled
              sx={{ textTransform: 'none' }}
            >
              Voice Message
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatPage;