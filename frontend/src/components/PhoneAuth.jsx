import React, { useState } from 'react';
import { RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';
import { auth } from '../firebaseClient';
import OTPModal from './OTPModal';
import { Form, Button, Alert } from 'react-bootstrap';
import { motion } from 'framer-motion';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';

const PhoneAuth = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState(null);
  const [confirmationResult, setConfirmationResult] = useState(null);
  const [showOtpModal, setShowOtpModal] = useState(false);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
        'size': 'invisible',
      });
      const result = await signInWithPhoneNumber(auth, `+${phoneNumber}`, recaptchaVerifier);
      setConfirmationResult(result);
      setShowOtpModal(true);
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
      <motion.h5 variants={itemVariants} className="text-center mb-3">Sign In with Phone</motion.h5>
      <Form onSubmit={handleSignIn}>
        <motion.div variants={itemVariants}>
          <Form.Group className="mb-3" controlId="formBasicPhoneNumber">
            <PhoneInput
              country={'in'}
              value={phoneNumber}
              onChange={setPhoneNumber}
            />
          </Form.Group>
        </motion.div>

        {error && <motion.div variants={itemVariants}><Alert variant="danger">{error}</Alert></motion.div>}

        <motion.div variants={itemVariants} className="d-grid">
          <Button as={motion.button} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="btn-primary-custom" type="submit">
            Send OTP
          </Button>
        </motion.div>
      </Form>
      <div id="recaptcha-container"></div>
      <OTPModal
        show={showOtpModal}
        onHide={() => setShowOtpModal(false)}
        confirmationResult={confirmationResult}
      />
    </motion.div>
  );
};

export default PhoneAuth;
