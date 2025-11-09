import React from 'react';
import EmailAuth from '../components/EmailAuth';
import GoogleSignIn from '../components/GoogleSignIn';
import PhoneAuth from '../components/PhoneAuth';
import { Card, Tab, Nav } from 'react-bootstrap';
import { motion, AnimatePresence } from 'framer-motion';

const tabContentVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  transition: { duration: 0.2 }
};

const LoginPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="auth-card">
        <Card.Header
          as="h4"
          className="text-center bg-transparent border-0 pt-4 pb-3"
          style={{ color: '#1565C0', fontWeight: '700' }} // dark blue
        >
          Sign up / Login 
        </Card.Header>

        <Card.Body>
          <Tab.Container defaultActiveKey="email">
            <Nav variant="pills" className="justify-content-center mb-4">
              <Nav.Item>
                <Nav.Link eventKey="email" as={motion.a} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>Email</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="phone" as={motion.a} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>Phone</Nav.Link>
              </Nav.Item>
            </Nav>
            <AnimatePresence mode="wait">
              <Tab.Content>
                <Tab.Pane eventKey="email">
                  <motion.div {...tabContentVariants}>
                    <EmailAuth />
                  </motion.div>
                </Tab.Pane>
                <Tab.Pane eventKey="phone">
                  <motion.div {...tabContentVariants}>
                    <PhoneAuth />
                  </motion.div>
                </Tab.Pane>
              </Tab.Content>
            </AnimatePresence>
          </Tab.Container>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.3 }}
            className="d-flex align-items-center my-3"
          >
            <hr className="flex-grow-1" />
            <span className="px-2 text-muted small">OR</span>
            <hr className="flex-grow-1" />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.3 }}
          >
            <GoogleSignIn />
          </motion.div>
        </Card.Body>
      </Card>
    </motion.div>
  );
};

export default LoginPage;
