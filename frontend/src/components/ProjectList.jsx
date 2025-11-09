import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner, Alert } from 'react-bootstrap';
import { motion } from 'framer-motion';
import ProjectCard from './ProjectCard';
import { getMLProjects } from '../services/mlApi';
import { FolderX } from 'react-bootstrap-icons';

const ProjectList = ({ refreshTrigger, onViewDetails, onDownload }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getMLProjects();
      setProjects(response.data.projects || []);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [refreshTrigger]);

  if (loading) {
    return (
      <div className="text-center py-5">
        <Spinner animation="border" style={{ color: '#667eea' }} />
        <p className="mt-3 text-muted">Loading your projects...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger" className="border-0 shadow-sm" style={{ borderRadius: '12px' }}>
        {error}
      </Alert>
    );
  }

  if (projects.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-5"
        style={{
          background: 'linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)',
          borderRadius: '20px',
          padding: '60px 20px'
        }}
      >
        <FolderX size={64} style={{ color: '#9ca3af', marginBottom: '20px' }} />
        <h5 style={{ color: '#4b5563', marginBottom: '12px' }}>No Projects Yet</h5>
        <p style={{ color: '#6b7280', fontSize: '0.95em' }}>
          Start by creating your first ML project using the chat above!
        </p>
      </motion.div>
    );
  }

  return (
    <Row className="g-3">
      {projects.map((project, index) => (
        <Col key={project.id} xs={12} lg={6} xl={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <ProjectCard
              project={project}
              onViewDetails={onViewDetails}
              onDownload={onDownload}
            />
          </motion.div>
        </Col>
      ))}
    </Row>
  );
};

export default ProjectList;
