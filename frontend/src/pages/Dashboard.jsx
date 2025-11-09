import React, { useState } from 'react';
import { sessionLogout } from '../services/api';
import { Card, Button, Form, Tabs, Tab, Container, Row, Col } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { 
  Person, 
  ChatDots, 
  House,
  Cpu,
  Image as ImageIcon,
  BoxArrowRight
} from 'react-bootstrap-icons';
import ChatBot from '../components/ChatBot';
import MLProjectsPage from './MLProjectsPage';
import ModelTester from '../components/ModelTester';

const Dashboard = ({ user }) => {
  const [showProfile, setShowProfile] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [isChatFullscreen, setIsChatFullscreen] = useState(false);
  const [activeTab, setActiveTab] = useState('home');
  
  // Load profile from localStorage or use Firebase user data as fallback
  const [profileData, setProfileData] = useState(() => {
    // Use user.uid to make localStorage user-specific
    const savedProfile = localStorage.getItem(`userProfile_${user.uid}`);
    if (savedProfile) {
      return JSON.parse(savedProfile);
    }
    return {
      displayName: user.displayName || '',
      phoneNumber: user.phoneNumber || ''
    };
  });

  const handleLogout = async () => {
    await sessionLogout();
    window.location.reload();
  };

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    // Save to localStorage with user-specific key
    localStorage.setItem(`userProfile_${user.uid}`, JSON.stringify(profileData));
    alert('Profile updated successfully!');
    setShowProfile(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleToggleChatFullscreen = () => {
    setIsChatFullscreen(!isChatFullscreen);
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb', width: '100%' }}>
      {/* Top Navigation Bar */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{
          background: 'white',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          position: 'sticky',
          top: 0,
          zIndex: 100
        }}
      >
        <Container fluid style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div className="d-flex justify-content-between align-items-center py-3">
            <div className="d-flex align-items-center gap-3">
              <h4 className="mb-0 fw-bold" style={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                ____VibeML___________________________________________________________________________________________
              </h4>
            </div>
            
            <div className="d-flex align-items-center gap-3">
              <Button
                variant="link"
                onClick={() => setShowProfile(!showProfile)}
                style={{ 
                  color: '#4b5563',
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <Person size={20} />
                <span className="d-none d-md-inline">Profile</span>
              </Button>
              
              {activeTab === 'home' && (
                <Button
                  variant="link"
                  onClick={() => setShowChat(!showChat)}
                  style={{ 
                    color: '#4b5563',
                    textDecoration: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <ChatDots size={20} />
                  <span className="d-none d-md-inline">Chat</span>
                </Button>
              )}
              
              <Button
                variant="outline-danger"
                size="sm"
                onClick={handleLogout}
                style={{ 
                  borderRadius: '8px',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <BoxArrowRight size={16} />
                <span className="d-none d-md-inline">Logout</span>
              </Button>
            </div>
          </div>
        </Container>
      </motion.div>

      {/* Profile Modal Overlay */}
      {showProfile && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px'
          }}
          onClick={() => setShowProfile(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
            style={{ maxWidth: '500px', width: '100%' }}
          >
            <Card className="border-0 shadow-lg" style={{ borderRadius: '20px' }}>
              <Card.Header 
                className="border-0 text-white"
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: '20px 20px 0 0',
                  padding: '24px'
                }}
              >
                <h5 className="mb-0 fw-bold">👤 Profile Settings</h5>
              </Card.Header>
              <Card.Body className="p-4">
                <Form onSubmit={handleProfileSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label className="fw-semibold">Name</Form.Label>
                    <Form.Control 
                      type="text" 
                      name="displayName"
                      placeholder="Enter your name" 
                      value={profileData.displayName}
                      onChange={handleInputChange}
                      style={{
                        borderRadius: '10px',
                        border: '2px solid #e5e7eb',
                        padding: '12px'
                      }}
                    />
                  </Form.Group>

                  <Form.Group className="mb-4">
                    <Form.Label className="fw-semibold">Phone Number</Form.Label>
                    <Form.Control 
                      type="text" 
                      name="phoneNumber"
                      placeholder="Enter phone number" 
                      value={profileData.phoneNumber}
                      onChange={handleInputChange}
                      style={{
                        borderRadius: '10px',
                        border: '2px solid #e5e7eb',
                        padding: '12px'
                      }}
                    />
                  </Form.Group>
                  
                  <div className="d-flex gap-2">
                    <Button 
                      variant="primary" 
                      type="submit"
                      className="flex-grow-1"
                      style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        border: 'none',
                        borderRadius: '10px',
                        padding: '12px',
                        fontWeight: '600'
                      }}
                    >
                      Save Changes
                    </Button>
                    <Button 
                      variant="outline-secondary"
                      onClick={() => setShowProfile(false)}
                      style={{
                        borderRadius: '10px',
                        padding: '12px 24px',
                        fontWeight: '600'
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </Form>
              </Card.Body>
            </Card>
          </motion.div>
        </motion.div>
      )}

      {/* Main Content with Tabs */}
      <Container fluid className="py-4" style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-4 custom-tabs"
            style={{
              borderBottom: '2px solid #e5e7eb'
            }}
          >
            <Tab 
              eventKey="home" 
              title={
                <span className="d-flex align-items-center gap-2">
                  <House size={18} />
                  <span>Home</span>
                </span>
              }
            >
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="border-0 shadow-sm" style={{ borderRadius: '20px' }}>
                  <Card.Body className="p-5">
                    <motion.div
                      initial="hidden"
                      animate="visible"
                      variants={{
                        visible: {
                          transition: {
                            staggerChildren: 0.1
                          }
                        }
                      }}
                    >
                      <motion.div variants={itemVariants}>
                        <h2 className="mb-3 fw-bold" style={{ color: '#1f2937' }}>
                          Welcome back, {profileData.displayName || user.displayName || user.email || user.phoneNumber}! 👋
                        </h2>
                        <p style={{ color: '#6b7280', fontSize: '1.1em', marginBottom: '30px' }}>
                          Your AI-powered machine learning workspace
                        </p>
                      </motion.div>

                      <motion.div variants={itemVariants}>
                        <Row className="g-4 justify-content-center">
                          <Col xs={12} sm={6} lg={4}>
                            <Card 
                              className="border-0 h-100"
                              style={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                borderRadius: '16px',
                                cursor: 'pointer'
                              }}
                              onClick={() => setActiveTab('ml-projects')}
                            >
                              <Card.Body className="p-4 text-white">
                                <Cpu size={40} className="mb-3" />
                                <h5 className="fw-bold mb-2">ML Projects</h5>
                                <p style={{ opacity: 0.9, fontSize: '0.9em' }}>
                                  Create and manage your machine learning models
                                </p>
                              </Card.Body>
                            </Card>
                          </Col>

                          <Col xs={12} sm={6} lg={4}>
                            <Card 
                              className="border-0 h-100"
                              style={{
                                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                                borderRadius: '16px',
                                cursor: 'pointer'
                              }}
                              onClick={() => setActiveTab('test-model')}
                            >
                              <Card.Body className="p-4 text-white">
                                <ImageIcon size={40} className="mb-3" />
                                <h5 className="fw-bold mb-2">Test Models</h5>
                                <p style={{ opacity: 0.9, fontSize: '0.9em' }}>
                                  Upload images to test your trained models
                                </p>
                              </Card.Body>
                            </Card>
                          </Col>

                          <Col xs={12} sm={6} lg={4}>
                            <Card 
                              className="border-0 h-100"
                              style={{
                                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                borderRadius: '16px',
                                cursor: 'pointer'
                              }}
                              onClick={() => setShowChat(true)}
                            >
                              <Card.Body className="p-4 text-white">
                                <ChatDots size={40} className="mb-3" />
                                <h5 className="fw-bold mb-2">AI Assistant</h5>
                                <p style={{ opacity: 0.9, fontSize: '0.9em' }}>
                                  Chat with your personal AI assistant
                                </p>
                              </Card.Body>
                            </Card>
                          </Col>
                        </Row>
                      </motion.div>
                    </motion.div>
                  </Card.Body>
                </Card>
              </motion.div>
            </Tab>

            <Tab 
              eventKey="ml-projects" 
              title={
                <span className="d-flex align-items-center gap-2">
                  <Cpu size={18} />
                  <span>ML Projects</span>
                </span>
              }
            >
              <MLProjectsPage user={user} />
            </Tab>

            <Tab 
              eventKey="test-model" 
              title={
                <span className="d-flex align-items-center gap-2">
                  <ImageIcon size={18} />
                  <span>Test Model</span>
                </span>
              }
            >
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <ModelTester />
              </motion.div>
            </Tab>
          </Tabs>
        </motion.div>
      </Container>

      {/* Chat Widget (only on home tab) */}
      {showChat && activeTab === 'home' && (
        <div className="chat-widget">
          <ChatBot 
            user={user}
            onToggleFullscreen={handleToggleChatFullscreen}
            isFullscreen={isChatFullscreen}
            onClose={() => setShowChat(false)}
          />
        </div>
      )}

      <style>{`
        .custom-tabs .nav-link {
          color: #6b7280;
          border: none;
          padding: 12px 24px;
          font-weight: 600;
          border-bottom: 3px solid transparent;
          transition: all 0.3s;
        }
        
        .custom-tabs .nav-link:hover {
          color: #667eea;
          border-bottom-color: #667eea;
        }
        
        .custom-tabs .nav-link.active {
          color: #667eea;
          background: transparent;
          border-bottom-color: #667eea;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
