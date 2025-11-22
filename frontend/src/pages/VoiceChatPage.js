import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Avatar,
  CircularProgress,
  Chip,
  Fade,
  Fab,
} from '@mui/material';
import {
  Mic,
  Stop,
  SmartToy,
  Person,
  VolumeUp,
} from '@mui/icons-material';
import { useNotification } from '../contexts/NotificationContext';
import { chatService } from '../services/chatService';

const SUPPORTED_AUDIO_TYPES = [
  'audio/webm;codecs=opus',
  'audio/ogg;codecs=opus',
  'audio/webm',
];

const getSupportedMimeType = () => {
  if (typeof window === 'undefined' || !window.MediaRecorder) {
    return 'audio/webm';
  }
  return SUPPORTED_AUDIO_TYPES.find((type) => MediaRecorder.isTypeSupported(type)) || 'audio/webm';
};

const getAudioDuration = (blob) => new Promise((resolve, reject) => {
  const tempUrl = URL.createObjectURL(blob);
  const audio = new Audio(tempUrl);
  audio.addEventListener('loadedmetadata', () => {
    const duration = audio.duration || 0;
    URL.revokeObjectURL(tempUrl);
    resolve(duration);
  });
  audio.addEventListener('error', (event) => {
    URL.revokeObjectURL(tempUrl);
    reject(event);
  });
});

const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return '0:00';
  const rounded = Math.max(0, Math.round(seconds));
  const mins = Math.floor(rounded / 60);
  const secs = rounded % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const VoiceChatPage = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const objectUrlsRef = useRef([]);
  const mimeTypeRef = useRef(getSupportedMimeType());
  const { showNotification } = useNotification();

  useEffect(() => {
    return () => {
      objectUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
    };
  }, []);

  const startRecording = async () => {
    if (isProcessing || isUploading) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const constraints = mimeTypeRef.current ? { mimeType: mimeTypeRef.current } : undefined;
      mediaRecorderRef.current = new MediaRecorder(stream, constraints);
      mimeTypeRef.current = mediaRecorderRef.current.mimeType || mimeTypeRef.current;
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const blobType = mimeTypeRef.current || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: blobType });
        const durationSeconds = await getAudioDuration(audioBlob).catch(() => 0);
        await processVoiceRecording(audioBlob, durationSeconds, blobType);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      showNotification('Failed to access microphone', 'error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const processVoiceRecording = async (audioBlob, durationSeconds, blobType) => {
    setIsProcessing(true);
    setIsUploading(true);
    
    const audioUrl = URL.createObjectURL(audioBlob);
    objectUrlsRef.current.push(audioUrl);
    const fileExtension = blobType && blobType.includes('ogg') ? 'ogg' : 'webm';
    const fileName = `voice-${Date.now()}.${fileExtension}`;
    const audioFile = new File([audioBlob], fileName, { type: blobType });

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: 'Voice message recorded',
      timestamp: new Date(),
      audioUrl,
      status: 'uploading',
      metadata: {
        duration: durationSeconds,
      },
    };
    
    setConversation(prev => [...prev, userMessage]);

    try {
      const apiResponse = await chatService.uploadVoiceRecording(audioFile, durationSeconds);

      setConversation(prev => prev.map(message => 
        message.id === userMessage.id 
          ? { ...message, status: 'uploaded' }
          : message
      ));

      const resultMessage = {
        id: `${userMessage.id}-result`,
        type: 'ai',
        content: apiResponse?.ai_response || apiResponse?.transcript || 'Voice recording processed.',
        timestamp: new Date(),
        audioUrl: apiResponse?.audio_file,
        metadata: apiResponse,
      };

      setConversation(prev => [...prev, resultMessage]);
      showNotification('Voice message processed successfully', 'success');
    } catch (error) {
      console.error('Voice upload failed:', error);
      setConversation(prev => prev.map(message => 
        message.id === userMessage.id 
          ? { ...message, status: 'error' }
          : message
      ));
      showNotification('Failed to process voice recording', 'error');
    } finally {
      setIsProcessing(false);
      setIsUploading(false);
    }
  };

  const MessageBubble = ({ message }) => {
    const isUser = message.type === 'user';
    
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
            {message.content && (
              <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
                {message.content}
              </Typography>
            )}
            {message.audioUrl && (
              <Box sx={{ mt: 1 }}>
                <audio
                  controls
                  src={message.audioUrl}
                  style={{ width: '100%' }}
                />
              </Box>
            )}
            {message.metadata?.transcript && (
              <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                Transcript: {message.metadata.transcript}
              </Typography>
            )}
            {(message.metadata?.duration || message.metadata?.confidence_score) && (
              <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                {message.metadata?.duration !== undefined && `Duration: ${formatDuration(message.metadata.duration)}`}
                {message.metadata?.confidence_score !== undefined && (
                  <> • Confidence: {Math.round(message.metadata.confidence_score * 100)}%</>
                )}
              </Typography>
            )}
            {message.status === 'uploading' && (
              <Typography variant="caption" sx={{ display: 'block', mt: 0.5, opacity: 0.8 }}>
                Uploading...
              </Typography>
            )}
            {message.status === 'error' && (
              <Typography variant="caption" color="error" sx={{ display: 'block', mt: 0.5 }}>
                Upload failed. Please try again.
              </Typography>
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
      {/* Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 2, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
              <SmartToy />
            </Avatar>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Voice AI Assistant
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Click the microphone to start speaking
              </Typography>
            </Box>
          </Box>
          <Box>
            <Chip
              label={
                isRecording
                  ? 'Recording...'
                  : (isProcessing || isUploading)
                    ? 'Processing...'
                    : 'Ready'
              }
              color={isRecording ? 'error' : (isProcessing || isUploading) ? 'warning' : 'success'}
              size="small"
            />
          </Box>
        </Box>
      </Paper>

      {/* Voice Control */}
      <Paper elevation={1} sx={{ p: 4, mb: 2, borderRadius: 3, textAlign: 'center' }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Voice Controls
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Hold the microphone button to record your message
          </Typography>
        </Box>

        <Box sx={{ position: 'relative', display: 'inline-block' }}>
          <Fade in={!isRecording} timeout={300}>
            <Fab
              color="primary"
              size="large"
              onMouseDown={startRecording}
              onTouchStart={startRecording}
              disabled={isProcessing || isUploading}
              sx={{
                width: 80,
                height: 80,
                '&:hover': { transform: 'scale(1.1)' },
                transition: 'transform 0.2s',
              }}
            >
              <Mic sx={{ fontSize: 40 }} />
            </Fab>
          </Fade>

          <Fade in={isRecording} timeout={300}>
            <Fab
              color="error"
              size="large"
              onClick={stopRecording}
              onMouseUp={stopRecording}
              onTouchEnd={stopRecording}
              sx={{
                width: 80,
                height: 80,
                position: 'absolute',
                top: 0,
                left: 0,
                animation: 'pulse 1.5s infinite',
              }}
            >
              <Stop sx={{ fontSize: 40 }} />
            </Fab>
          </Fade>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          {isRecording 
            ? 'Release to send message' 
            : isProcessing 
              ? 'Processing your message...' 
              : 'Hold to record'}
        </Typography>
      </Paper>

      {/* Conversation */}
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
          {conversation.length === 0 ? (
            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <VolumeUp sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Start a voice conversation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Use the microphone above to record your first message
              </Typography>
            </Box>
          ) : (
            conversation.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))
          )}
        </Box>

        {/* Status Bar */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Voice Chat Status:
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {isRecording && (
                <CircularProgress size={16} color="error" />
              )}
              <Chip
                size="small"
                label={
                  isRecording 
                    ? 'Recording' 
                    : (isProcessing || isUploading)
                      ? 'Processing' 
                      : 'Ready'
                }
                color={
                  isRecording 
                    ? 'error' 
                    : (isProcessing || isUploading)
                      ? 'warning' 
                      : 'success'
                }
              />
            </Box>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default VoiceChatPage;