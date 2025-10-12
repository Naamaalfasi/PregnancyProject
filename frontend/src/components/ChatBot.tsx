import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  Avatar,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Checkbox
} from '@mui/material';
import {
  Send,
  SmartToy,
  Add,
  Chat,
  History,
  PregnantWoman,
  Delete
} from '@mui/icons-material';
import { chatService, type ChatMessage } from '../services/chatService';

interface Conversation {
  id?: string;
  conversation_id?: string;
  title?: string;
  subject?: string;
  messages: ChatMessage[];
  created_at: string;
}
import { authService } from '../services/authService';

// Custom styled markdown component
const StyledMarkdown = ({ children }: { children: string }) => {
  return (
    <ReactMarkdown
      components={{
        // Style paragraphs
        p: ({ children }) => (
          <Typography component="span" variant="body1" sx={{ display: 'block', mb: 1, lineHeight: 1.6 }}>
            {children}
          </Typography>
        ),
        // Style strong/bold text
        strong: ({ children }) => (
          <strong style={{ fontWeight: 600 }}>{children}</strong>
        ),
        // Style emphasis/italic text
        em: ({ children }) => (
          <em style={{ fontStyle: 'italic' }}>{children}</em>
        ),
        // Style lists
        ul: ({ children }) => (
          <ul style={{ marginLeft: '20px', marginBottom: '8px' }}>
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol style={{ marginLeft: '20px', marginBottom: '8px' }}>
            {children}
          </ol>
        ),
        li: ({ children }) => (
          <li style={{ marginBottom: '4px' }}>{children}</li>
        ),
        // Style code
        code: ({ children }) => (
          <code style={{ 
            backgroundColor: 'rgba(255,255,255,0.2)', 
            padding: '2px 6px', 
            borderRadius: '4px',
            fontFamily: 'monospace'
          }}>
            {children}
          </code>
        ),
      }}
    >
      {children}
    </ReactMarkdown>
  );
};

interface ChatBotProps {}

const ChatBot: React.FC<ChatBotProps> = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [showConversations, setShowConversations] = useState(false);
  const [userId, setUserId] = useState<string>('');
  const [selectedConversations, setSelectedConversations] = useState<Set<string>>(new Set());
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Get current user ID
    const getCurrentUser = async () => {
      try {
        const user = await authService.getCurrentUser();
        if (user) {
          // The getCurrentUser() returns the user object directly, not wrapped in user_id
          const userId = user.user_id || user;
          setUserId(userId);
          await loadConversations(userId);
        } else {
          setError('Please log in to use the chatbot. Click the login button in the header.');
        }
      } catch (error) {
        console.error('Error getting current user:', error);
        setError('Failed to get user information');
      }
    };

    getCurrentUser();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async (userId: string) => {
    try {
      const convos = await chatService.getAllConversations(userId);
      setConversations(convos || []);
    } catch (error) {
      console.error('Error loading conversations:', error);
      setConversations([]);
    }
  };

  const createNewConversation = async () => {
    if (!userId) return;
    
    try {
      const result = await chatService.createNewConversation(userId);
      setCurrentConversationId(result.conversation_id);
      setMessages([]);
      await loadConversations(userId);
      setShowConversations(false);
    } catch (error) {
      console.error('Error creating conversation:', error);
      setError('Failed to create new conversation');
    }
  };

  const switchConversation = async (conversationId: string) => {
    if (!userId) return;
    
    try {
      await chatService.switchToConversation(userId, conversationId);
      const conversation = await chatService.getConversationById(userId, conversationId);
      setCurrentConversationId(conversationId);
      
      // Convert API messages to ChatMessage format
      const apiMessages = conversation.messages || [];
      const chatMessages: ChatMessage[] = apiMessages
        .filter((msg: any) => msg.role !== 'system') // Filter out system messages
        .map((msg: any) => ({
          id: msg.message_id || Date.now().toString(),
          message: msg.content || '',
          timestamp: msg.timestamp || new Date().toISOString(),
          isUser: msg.role === 'user'
        }));
      
      setMessages(chatMessages);
      setShowConversations(false);
    } catch (error) {
      console.error('Error switching conversation:', error);
      setError('Failed to load conversation');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) {
      setError('Please enter a message');
      return;
    }
    
    if (!userId) {
      setError('Please log in to send messages');
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message: inputMessage,
      timestamp: new Date().toISOString(),
      isUser: true
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatService.processChatMessage(userId, messageToSend);
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: response.response,
        timestamp: new Date().toISOString(),
        isUser: false
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const handleConversationSelect = (conversationId: string) => {
    const newSelected = new Set(selectedConversations);
    if (newSelected.has(conversationId)) {
      newSelected.delete(conversationId);
    } else {
      newSelected.add(conversationId);
    }
    setSelectedConversations(newSelected);
  };

  const handleDeleteSelected = async () => {
    if (!userId || selectedConversations.size === 0) return;
    
    try {
      const deletePromises = Array.from(selectedConversations).map(conversationId =>
        chatService.deleteConversation(userId, conversationId)
      );
      
      await Promise.all(deletePromises);
      
      // Reload conversations
      await loadConversations(userId);
      setSelectedConversations(new Set());
      
      // If current conversation was deleted, clear messages
      if (currentConversationId && selectedConversations.has(currentConversationId)) {
        setMessages([]);
        setCurrentConversationId(null);
      }
    } catch (error) {
      console.error('Error deleting conversations:', error);
      setError('Failed to delete conversations');
    }
  };

  return (
    <Box sx={{ 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column', 
      p: 2,
      maxWidth: '1200px',
      margin: '0 auto',
      width: '100%'
    }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 2, mb: 2, background: 'linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <SmartToy sx={{ color: '#e91e63', mr: 1 }} />
            <Typography variant="h5" sx={{ fontWeight: 600, color: '#333' }}>
              AI Pregnancy Assistant
            </Typography>
          </Box>
          <Box>
            <IconButton onClick={() => setShowConversations(true)} sx={{ mr: 1 }}>
              <History />
            </IconButton>
            <IconButton onClick={createNewConversation} color="primary">
              <Add />
            </IconButton>
          </Box>
        </Box>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Messages Area */}
      <Paper 
        elevation={1} 
        sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2, 
          mb: 2,
          background: '#fafafa'
        }}
      >
        {!userId ? (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <SmartToy sx={{ fontSize: 64, color: '#e91e63', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Please log in to use the chatbot
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Click the login button in the header to access the AI Pregnancy Assistant
            </Typography>
          </Box>
        ) : messages.length === 0 ? (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <SmartToy sx={{ fontSize: 64, color: '#e91e63', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Welcome to your AI Pregnancy Assistant
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Ask me anything about your pregnancy journey!
            </Typography>
          </Box>
        ) : (
          <List>
            {messages.map((message) => (
              <React.Fragment key={message.id}>
                <ListItem sx={{ justifyContent: message.isUser ? 'flex-end' : 'flex-start' }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', maxWidth: '70%' }}>
                    <Avatar sx={{ 
                      bgcolor: message.isUser ? '#e91e63' : '#9c27b0',
                      mr: message.isUser ? 0 : 1,
                      ml: message.isUser ? 1 : 0,
                      order: message.isUser ? 2 : 0
                    }}>
                      {message.isUser ? <PregnantWoman /> : <SmartToy />}
                    </Avatar>
                    <Paper 
                      elevation={1}
                      sx={{ 
                        p: 2, 
                        bgcolor: message.isUser ? '#e91e63' : '#9c27b0',
                        color: 'white',
                        borderRadius: message.isUser ? '20px 20px 5px 20px' : '20px 20px 20px 5px'
                      }}
                    >
                      <Box sx={{ color: 'white' }}>
                        <StyledMarkdown>{message.message}</StyledMarkdown>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', display: 'block', mt: 1 }}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                </ListItem>
                <Divider sx={{ my: 1 }} />
              </React.Fragment>
            ))}
            {isLoading && (
              <ListItem sx={{ justifyContent: 'flex-start' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#9c27b0', mr: 1 }}>
                    <SmartToy />
                  </Avatar>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: '#9c27b0', color: 'white' }}>
                    <CircularProgress size={16} sx={{ color: 'white' }} />
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      AI is thinking...
                    </Typography>
                  </Paper>
                </Box>
              </ListItem>
            )}
          </List>
        )}
        <div ref={messagesEndRef} />
      </Paper>

      {/* Input Area */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder={!userId ? "Please log in to use the chatbot" : "Ask me anything about your pregnancy..."}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading || !userId}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '25px',
                backgroundColor: '#f8f9ff'
              }
            }}
          />
          <Button
            variant="contained"
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading || !userId}
            sx={{
              borderRadius: '50%',
              minWidth: '56px',
              height: '56px',
              background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
              '&:hover': {
                background: 'linear-gradient(45deg, #c2185b, #7b1fa2)'
              }
            }}
          >
            <Send />
          </Button>
        </Box>
      </Paper>

      {/* Conversations Dialog */}
      <Dialog open={showConversations} onClose={() => setShowConversations(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">Conversation History</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {selectedConversations.size > 0 && (
                <Button
                  startIcon={<Delete />}
                  onClick={handleDeleteSelected}
                  variant="outlined"
                  color="error"
                  size="small"
                >
                  Delete ({selectedConversations.size})
                </Button>
              )}
              <Button
                startIcon={<Add />}
                onClick={createNewConversation}
                variant="contained"
                size="small"
              >
                New Chat
              </Button>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {!conversations || conversations.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Chat sx={{ fontSize: 48, color: '#e91e63', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                No conversations yet. Start a new chat!
              </Typography>
            </Box>
          ) : (
            <List>
              {conversations.map((conversation) => {
                const conversationId = conversation.id || conversation.conversation_id;
                const isSelected = selectedConversations.has(conversationId || '');
                return (
                  <ListItem key={conversationId} disablePadding>
                    <ListItemButton
                      onClick={() => conversationId && switchConversation(conversationId)}
                      selected={currentConversationId === conversationId}
                    >
                      <Checkbox
                        checked={isSelected}
                        onChange={() => conversationId && handleConversationSelect(conversationId)}
                        onClick={(e) => e.stopPropagation()}
                      />
                      <ListItemIcon>
                        <Chat color={currentConversationId === conversationId ? 'primary' : 'inherit'} />
                      </ListItemIcon>
                      <ListItemText
                        primary={conversation.title || conversation.subject || `Conversation ${conversationId ? conversationId.slice(-6) : 'Unknown'}`}
                        secondary={conversation.created_at ? new Date(conversation.created_at).toLocaleDateString() : 'Unknown date'}
                      />
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConversations(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatBot;
