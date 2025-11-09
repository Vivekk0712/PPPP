import React, { useState } from 'react';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from 'firebase/auth';
import { auth } from '../firebaseClient';
import { sessionLogin } from '../services/api';
import { Form, Button, Alert } from 'react-bootstrap';
import { motion } from 'framer-motion';

const EmailAuth = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSignUp, setIsSignUp] = useState(true);

  const handleAuth = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      let userCredential;
      if (isSignUp) {
        userCredential = await createUserWithEmailAndPassword(auth, email, password);
      } else {
        userCredential = await signInWithEmailAndPassword(auth, email, password);
      }
      const idToken = await userCredential.user.getIdToken();
      await sessionLogin(idToken);
      window.location.reload(); // Reload to fetch user session
    } catch (error) {
      setError(error.message);
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };

  return (
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
      <motion.h5 variants={itemVariants} className="text-center mb-3">{isSignUp ? 'Sign Up' : 'Sign In'} with Email</motion.h5>
      <Form onSubmit={handleAuth}>
        <motion.div variants={itemVariants}>
          <Form.Group className="mb-3" controlId="formBasicEmail">
            <Form.Control
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter email"
              required
            />
          </Form.Group>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Form.Group className="mb-3" controlId="formBasicPassword">
            <Form.Control
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
          </Form.Group>
        </motion.div>

        {error && <motion.div variants={itemVariants}><Alert variant="danger">{error}</Alert></motion.div>}

        <motion.div variants={itemVariants} className="d-grid">
          <Button as={motion.button} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="btn-primary-custom" type="submit">
            {isSignUp ? 'Sign Up' : 'Sign In'}
          </Button>
        </motion.div>
      </Form>
      <motion.div variants={itemVariants} className="text-center mt-3">
        <Button as={motion.button} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} variant="link" className="btn-link-custom" onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
        </Button>
      </motion.div>
    </motion.div>
  );
};

export default EmailAuth;
