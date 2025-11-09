import React, { useState, useEffect, useRef } from 'react';
import { Form, Button, Card, Spinner, InputGroup, Badge } from 'react-bootstrap';
import { Send, Lightbulb } from 'react-bootstrap-icons';
import { createMLProject } from '../services/mlApi';
import { motion, AnimatePresence } from 'framer-motion';

const MLChatBot = ({ user, onProjectCreated }) => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef(null);

  const examplePrompts = [
    "Train a model to classify plant diseases",
    "Create an image classifier for skin cancer detection",
    "Build a model to identify different types of flowers"
  ];

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory, loading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = { 
      role: 'user', 
      content: message, 
      timestamp: new Date().toISOString() 
    };
    
    setChatHistory(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      const response = await createMLProject(message);
      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.reply || 'Project created successfully! Check the projects list below.',
        timestamp: new Date().toISOString(),
        projectId: response.data.projectId
      };
      
      setChatHistory(prev => [...prev, assistantMessage]);
      
      if (onProjectCreated) {
        onProjectCreated();
      }
    } catch (error) {
      console.error('Error creating ML project:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, there was an error creating your project. Please try again.',
        timestamp: new Date().toISOString()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (prompt) => {
    setMessage(prompt);
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
    <Card className="shadow-sm border-0" style={{ 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '20px',
      overflow: 'hidden'
    }}>
      <Card.Header className="border-0 text-white" style={{ 
        background: 'rgba(255,255,255,0.1)',
        backdropFilter: 'blur(10px)'
      }}>
        <div className="d-flex align-items-center justify-content-between">
          <div>
            <h5 className="mb-1 fw-bold">🤖 ML Project Assistant</h5>
            <small style={{ opacity: 0.9 }}>Describe your machine learning project</small>
          </div>
          <Badge bg="light" text="dark" className="px-3 py-2">
            AI Powered
          </Badge>
        </div>
      </Card.Header>
      
      <Card.Body style={{ padding: '0' }}>
        <div 
          ref={chatContainerRef}
          style={{
            height: '400px',
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
              style={{ textAlign: 'center', padding: '40px 20px' }}
            >
              <Lightbulb size={48} style={{ color: '#667eea', marginBottom: '20px' }} />
              <h6 className="mb-3" style={{ color: '#333' }}>Start Your ML Journey</h6>
              <p style={{ color: '#666', fontSize: '0.9em', marginBottom: '20px' }}>
                Tell me what kind of model you want to create, and I'll help you build it!
              </p>
              
              <div className="d-flex flex-column gap-2">
                <small className="text-muted mb-2">Try these examples:</small>
                {examplePrompts.map((prompt, idx) => (
                  <motion.button
                    key={idx}
                    whileHover={{ scale: 1.02, boxShadow: '0 4px 12px rgba(102,126,234,0.2)' }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleExampleClick(prompt)}
                    style={{
                      padding: '12px 16px',
                      border: '2px solid #e9ecef',
                      borderRadius: '12px',
                      background: 'white',
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontSize: '0.9em',
                      color: '#495057',
                      transition: 'all 0.2s'
                    }}
                  >
                    💡 {prompt}
                  </motion.button>
                ))}
              </div>
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
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : '#f8f9fa',
                  color: chat.role === 'user' ? 'white' : '#333',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  wordWrap: 'break-word'
                }}>
                  <div style={{ fontSize: '0.75em', opacity: 0.8, marginBottom: '6px' }}>
                    {chat.role === 'user' ? '👤 You' : '🤖 Assistant'}
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
              <Spinner animation="border" size="sm" style={{ color: '#667eea' }} />
              <span style={{ color: '#666', fontSize: '0.9em' }}>
                Creating your project...
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
                placeholder="Describe your ML project..."
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
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
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

export default MLChatBot;
