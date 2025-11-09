import React, { useState, useEffect, useRef } from 'react';
import { Form, Button, Card, Spinner, InputGroup, Badge } from 'react-bootstrap';
import { X, Fullscreen, FullscreenExit, Trash, Send, ChatDots } from 'react-bootstrap-icons';
import { getHistory, sendMessage, clearChat } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';

const ChatBot = ({ user, onToggleFullscreen, isFullscreen = false, onClose }) => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef(null);

  // Load chat history from localStorage (user-specific)
  useEffect(() => {
    if (user?.uid) {
      const savedHistory = localStorage.getItem(`chatHistory_${user.uid}`);
      console.log('DEBUG: Loading from localStorage:', savedHistory);
      if (savedHistory) {
        try {
          const parsedHistory = JSON.parse(savedHistory);
          console.log('DEBUG: Parsed localStorage history:', parsedHistory);
          setChatHistory(parsedHistory);
        } catch (error) {
          console.error('Error parsing saved chat history:', error);
        }
      }
    }
  }, [user?.uid]);

  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    if (user?.uid && chatHistory.length > 0) {
      localStorage.setItem(`chatHistory_${user.uid}`, JSON.stringify(chatHistory));
      console.log('DEBUG: Saved to localStorage:', chatHistory);
    }
  }, [chatHistory, user?.uid]);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory, loading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = { role: 'user', content: message, timestamp: new Date().toISOString() };
    const newChatHistory = [...chatHistory, userMessage];
    console.log('DEBUG: Adding user message:', userMessage);
    console.log('DEBUG: New chat history after user message:', newChatHistory);
    
    setChatHistory(newChatHistory);
    setMessage('');
    setLoading(true);

    try {
      const response = await sendMessage(message);
      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.reply,
        timestamp: new Date().toISOString()
      };
      const finalChatHistory = [...newChatHistory, assistantMessage];
      console.log('DEBUG: Adding assistant message:', assistantMessage);
      console.log('DEBUG: Final chat history:', finalChatHistory);
      
      setChatHistory(finalChatHistory);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, something went wrong.',
        timestamp: new Date().toISOString()
      };
      setChatHistory([...newChatHistory, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (window.confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
      try {
        setLoading(true);
        await clearChat();
        setChatHistory([]);
        // Also clear localStorage
        if (user?.uid) {
          localStorage.removeItem(`chatHistory_${user.uid}`);
        }
        console.log('Chat history cleared successfully');
      } catch (error) {
        console.error('Error clearing chat history:', error);
        alert('Failed to clear chat history. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const messageVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { duration: 0.3 }
    }
  };

  return (
    <Card 
      className={`shadow-sm border-0 ${isFullscreen ? 'fullscreen-chat' : ''}`}
      style={isFullscreen ? {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1000,
        borderRadius: 0,
        margin: 0
      } : { 
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        borderRadius: '20px',
        overflow: 'hidden'
      }}
    >
      <Card.Header 
        className="border-0 text-white" 
        style={{ 
          background: isFullscreen ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)'
        }}
      >
        <div className="d-flex align-items-center justify-content-between">
          <div className="d-flex align-items-center gap-2">
            <ChatDots size={24} />
            <div>
              <h5 className="mb-0 fw-bold">💬 AI Assistant</h5>
              <small style={{ opacity: 0.9 }}>Your personal chat companion</small>
            </div>
          </div>
          <div className="d-flex gap-2">
            {chatHistory.length > 0 && !isFullscreen && (
              <Button 
                variant="light"
                size="sm" 
                onClick={handleClearChat}
                disabled={loading}
                title="Clear chat history"
                style={{ 
                  borderRadius: '8px',
                  padding: '6px 12px'
                }}
              >
                <Trash size={14} />
              </Button>
            )}
            {!isFullscreen && (
              <>
                <Button 
                  variant="light"
                  size="sm" 
                  onClick={onToggleFullscreen}
                  title="Fullscreen"
                  style={{ 
                    borderRadius: '8px',
                    padding: '6px 12px'
                  }}
                >
                  <Fullscreen size={14} />
                </Button>
                {onClose && (
                  <Button 
                    variant="light"
                    size="sm" 
                    onClick={onClose}
                    title="Close chat"
                    style={{ 
                      borderRadius: '8px',
                      padding: '6px 12px'
                    }}
                  >
                    <X size={14} />
                  </Button>
                )}
              </>
            )}
            {isFullscreen && (
              <>
                {chatHistory.length > 0 && (
                  <Button 
                    variant="light"
                    size="sm" 
                    onClick={handleClearChat}
                    disabled={loading}
                    title="Clear chat history"
                    style={{ 
                      borderRadius: '8px',
                      padding: '6px 12px'
                    }}
                  >
                    <Trash size={14} />
                  </Button>
                )}
                <Button 
                  variant="light"
                  size="sm" 
                  onClick={onToggleFullscreen}
                  title="Exit fullscreen"
                  style={{ 
                    borderRadius: '8px',
                    padding: '6px 12px'
                  }}
                >
                  <FullscreenExit size={14} />
                </Button>
              </>
            )}
          </div>
        </div>
      </Card.Header>
      
      <Card.Body style={{ padding: '0' }}>
        <div 
          ref={chatContainerRef}
          style={{
            height: isFullscreen ? 'calc(100vh - 200px)' : '450px',
            overflowY: 'auto',
            padding: '20px',
            background: 'white',
            scrollBehavior: 'smooth'
          }}
        >
          {chatHistory.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              style={{ textAlign: 'center', padding: '60px 20px' }}
            >
              <ChatDots size={48} style={{ color: '#10b981', marginBottom: '20px' }} />
              <h6 className="mb-3" style={{ color: '#333' }}>Start a Conversation</h6>
              <p style={{ color: '#666', fontSize: '0.9em' }}>
                Ask me anything! I'm here to help you with your questions.
              </p>
            </motion.div>
          )}
          
          <AnimatePresence>
            {chatHistory.map((chat, index) => (
              <motion.div
                key={`${chat.timestamp}-${index}`}
                variants={messageVariants}
                initial="hidden"
                animate="visible"
                style={{
                  margin: '12px 0',
                  display: 'flex',
                  justifyContent: chat.role === 'user' ? 'flex-end' : 'flex-start'
                }}
              >
                <div style={{
                  maxWidth: '75%',
                  padding: '14px 18px',
                  borderRadius: chat.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                  background: chat.role === 'user' 
                    ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                    : '#f8f9fa',
                  color: chat.role === 'user' ? 'white' : '#333',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  wordWrap: 'break-word'
                }}>
                  <div style={{ fontSize: '0.75em', opacity: 0.8, marginBottom: '6px' }}>
                    {chat.role === 'user' ? '👤 You' : '🤖 Assistant'}
                    {chat.timestamp && (
                      <span style={{ marginLeft: '8px' }}>
                        {formatTime(chat.timestamp)}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.95em', lineHeight: '1.5' }}>
                    {chat.content}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ 
                textAlign: 'center', 
                padding: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px'
              }}
            >
              <Spinner animation="border" size="sm" style={{ color: '#10b981' }} />
              <span style={{ color: '#666', fontSize: '0.9em' }}>
                Assistant is thinking...
              </span>
            </motion.div>
          )}
        </div>
        
        <div style={{ 
          padding: '20px', 
          background: 'white',
          borderTop: '1px solid #e9ecef'
        }}>
          <Form onSubmit={handleSendMessage}>
            <InputGroup>
              <Form.Control
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                disabled={loading}
                style={{
                  borderRadius: '25px 0 0 25px',
                  border: '2px solid #e9ecef',
                  padding: '12px 20px',
                  fontSize: '0.95em'
                }}
              />
              <Button 
                type="submit" 
                disabled={loading || !message.trim()}
                style={{
                  borderRadius: '0 25px 25px 0',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  border: 'none',
                  padding: '0 24px',
                  fontWeight: '600'
                }}
              >
                <Send size={18} />
              </Button>
            </InputGroup>
          </Form>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ChatBot;