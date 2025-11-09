import React, { useState, useEffect } from 'react';
import { getMe } from './services/api';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import './App.css';
import pic2 from './assets/pic2.jpeg'; // Import the image

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await getMe();
        setUser(response.data);
      } catch (error) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) {
    return (
      <div className="app-container">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`app-container ${!user ? 'login-bg-image' : ''}`}>
      {user ? (
        <Dashboard user={user} />
      ) : (
        <div className="app-content">
          <LoginPage />
        </div>
      )}
    </div>
  );
}

export default App;
