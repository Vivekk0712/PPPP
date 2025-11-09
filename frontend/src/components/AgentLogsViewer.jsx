import React, { useState, useEffect } from 'react';
import { Card, Badge, Spinner, Alert } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { 
  Terminal, 
  InfoCircle, 
  ExclamationTriangle, 
  XCircle,
  CheckCircle
} from 'react-bootstrap-icons';
import { getProjectLogs } from '../services/mlApi';

const AgentLogsViewer = ({ projectId }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (projectId) {
      fetchLogs();
    }
  }, [projectId]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getProjectLogs(projectId);
      setLogs(response.data.logs || []);
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to load logs');
    } finally {
      setLoading(false);
    }
  };

  const getLogIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return <XCircle size={16} style={{ color: '#ef4444' }} />;
      case 'warning':
        return <ExclamationTriangle size={16} style={{ color: '#f59e0b' }} />;
      case 'success':
        return <CheckCircle size={16} style={{ color: '#10b981' }} />;
      default:
        return <InfoCircle size={16} style={{ color: '#3b82f6' }} />;
    }
  };

  const getLogColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return { bg: '#fef2f2', border: '#fecaca', text: '#991b1b' };
      case 'warning':
        return { bg: '#fffbeb', border: '#fde68a', text: '#92400e' };
      case 'success':
        return { bg: '#f0fdf4', border: '#bbf7d0', text: '#166534' };
      default:
        return { bg: '#eff6ff', border: '#bfdbfe', text: '#1e40af' };
    }
  };

  const getAgentBadgeColor = (agentName) => {
    const colors = {
      'planner': 'primary',
      'dataset': 'info',
      'training': 'warning',
      'evaluation': 'success'
    };
    return colors[agentName?.toLowerCase()] || 'secondary';
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="text-center py-4">
        <Spinner animation="border" size="sm" style={{ color: '#667eea' }} />
        <p className="mt-2 text-muted" style={{ fontSize: '0.9em' }}>Loading logs...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger" className="border-0" style={{ borderRadius: '12px' }}>
        {error}
      </Alert>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="text-center py-5">
        <Terminal size={48} style={{ color: '#9ca3af', marginBottom: '16px' }} />
        <p style={{ color: '#6b7280', fontSize: '0.95em' }}>
          No logs available yet
        </p>
      </div>
    );
  }

  return (
    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
      {logs.map((log, index) => {
        const colors = getLogColor(log.log_level);
        return (
          <motion.div
            key={log.id || index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            style={{
              background: colors.bg,
              border: `1px solid ${colors.border}`,
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '12px'
            }}
          >
            <div className="d-flex justify-content-between align-items-start mb-2">
              <div className="d-flex align-items-center gap-2">
                {getLogIcon(log.log_level)}
                <Badge bg={getAgentBadgeColor(log.agent_name)} style={{ fontSize: '0.75em' }}>
                  {log.agent_name || 'System'}
                </Badge>
                <Badge bg="light" text="dark" style={{ fontSize: '0.7em' }}>
                  {log.log_level || 'info'}
                </Badge>
              </div>
              <small style={{ color: '#6b7280', fontSize: '0.75em' }}>
                {formatTimestamp(log.created_at)}
              </small>
            </div>
            <div style={{ 
              color: colors.text, 
              fontSize: '0.9em',
              lineHeight: '1.6',
              fontFamily: 'monospace'
            }}>
              {log.message}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default AgentLogsViewer;
