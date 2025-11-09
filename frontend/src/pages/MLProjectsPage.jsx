import React, { useState } from 'react';
import { Container, Row, Col, Modal, Button, Tab, Tabs, Badge } from 'react-bootstrap';
import { motion } from 'framer-motion';
import MLChatBot from '../components/MLChatBot';
import ProjectList from '../components/ProjectList';
import AgentLogsViewer from '../components/AgentLogsViewer';
import { downloadModel } from '../services/mlApi';
import { 
  Download, 
  X, 
  Activity,
  Database,
  Cpu,
  BarChart
} from 'react-bootstrap-icons';

const MLProjectsPage = ({ user }) => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const handleProjectCreated = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleViewDetails = (project) => {
    setSelectedProject(project);
    setShowDetailsModal(true);
  };

  const handleDownload = async (project) => {
    try {
      const response = await downloadModel(project.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.name}_model.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading model:', error);
      alert('Failed to download model. Please try again.');
    }
  };

  const getAgentStatus = (status) => {
    const stages = {
      'draft': { active: 'planner', completed: [] },
      'pending_dataset': { active: 'dataset', completed: ['planner'] },
      'pending_training': { active: 'training', completed: ['planner', 'dataset'] },
      'pending_evaluation': { active: 'evaluation', completed: ['planner', 'dataset', 'training'] },
      'completed': { active: null, completed: ['planner', 'dataset', 'training', 'evaluation'] },
      'export_ready': { active: null, completed: ['planner', 'dataset', 'training', 'evaluation'] }
    };
    return stages[status] || stages['draft'];
  };

  const AgentPipeline = ({ status }) => {
    const agentStatus = getAgentStatus(status);
    const agents = [
      { name: 'Planner', icon: <Activity size={20} />, key: 'planner' },
      { name: 'Dataset', icon: <Database size={20} />, key: 'dataset' },
      { name: 'Training', icon: <Cpu size={20} />, key: 'training' },
      { name: 'Evaluation', icon: <BarChart size={20} />, key: 'evaluation' }
    ];

    return (
      <div className="d-flex justify-content-between align-items-center mb-4">
        {agents.map((agent, idx) => {
          const isCompleted = agentStatus.completed.includes(agent.key);
          const isActive = agentStatus.active === agent.key;
          
          return (
            <React.Fragment key={agent.key}>
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: idx * 0.1 }}
                className="text-center"
                style={{ flex: 1 }}
              >
                <div
                  style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    background: isCompleted 
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                      : isActive
                      ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
                      : '#e5e7eb',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 8px',
                    color: isCompleted || isActive ? 'white' : '#9ca3af',
                    boxShadow: isActive ? '0 0 20px rgba(59,130,246,0.5)' : 'none',
                    animation: isActive ? 'pulse 2s infinite' : 'none'
                  }}
                >
                  {agent.icon}
                </div>
                <small style={{ 
                  color: isCompleted || isActive ? '#1f2937' : '#9ca3af',
                  fontWeight: isActive ? '600' : '500',
                  fontSize: '0.85em'
                }}>
                  {agent.name}
                </small>
                {isActive && (
                  <div className="mt-1">
                    <Badge bg="primary" style={{ fontSize: '0.7em' }}>
                      In Progress
                    </Badge>
                  </div>
                )}
              </motion.div>
              
              {idx < agents.length - 1 && (
                <div
                  style={{
                    flex: 0.5,
                    height: '3px',
                    background: isCompleted 
                      ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                      : '#e5e7eb',
                    marginBottom: '30px'
                  }}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="mb-4">
          <h2 className="fw-bold mb-2" style={{ color: '#1f2937' }}>
            🚀 ML Projects
          </h2>
          <p style={{ color: '#6b7280', fontSize: '1.05em' }}>
            Create and manage your machine learning projects
          </p>
        </div>

        <Row className="g-4">
          <Col xs={12} lg={5} xxl={4}>
            <div style={{ position: 'sticky', top: '100px' }}>
              <MLChatBot user={user} onProjectCreated={handleProjectCreated} />
            </div>
          </Col>
          
          <Col xs={12} lg={7} xxl={8}>
            <div style={{ 
              background: 'white',
              borderRadius: '20px',
              padding: '30px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              minHeight: '600px'
            }}>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="fw-bold mb-0" style={{ color: '#1f2937' }}>
                  Your Projects
                </h5>
                <Badge bg="primary" style={{ fontSize: '0.9em', padding: '8px 16px' }}>
                  {refreshTrigger} Total
                </Badge>
              </div>
              
              <ProjectList
                refreshTrigger={refreshTrigger}
                onViewDetails={handleViewDetails}
                onDownload={handleDownload}
              />
            </div>
          </Col>
        </Row>
      </motion.div>

      {/* Project Details Modal */}
      <Modal
        show={showDetailsModal}
        onHide={() => setShowDetailsModal(false)}
        size="lg"
        centered
      >
        <Modal.Header 
          closeButton 
          style={{ 
            border: 'none',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}
        >
          <Modal.Title className="fw-bold">
            {selectedProject?.name || 'Project Details'}
          </Modal.Title>
        </Modal.Header>
        
        <Modal.Body className="p-4">
          {selectedProject && (
            <>
              <AgentPipeline status={selectedProject.status} />
              
              <Tabs defaultActiveKey="details" className="mb-4">
                <Tab eventKey="details" title="Details">
                  <div className="mt-3">
                    <div className="mb-3 p-3" style={{ 
                      background: '#f9fafb', 
                      borderRadius: '12px' 
                    }}>
                      <small className="text-muted d-block mb-1">Task Type</small>
                      <strong style={{ color: '#1f2937' }}>
                        {selectedProject.task_type?.replace('_', ' ') || 'N/A'}
                      </strong>
                    </div>
                    
                    <div className="mb-3 p-3" style={{ 
                      background: '#f9fafb', 
                      borderRadius: '12px' 
                    }}>
                      <small className="text-muted d-block mb-1">Framework</small>
                      <strong style={{ color: '#1f2937' }}>
                        {selectedProject.framework || 'PyTorch'}
                      </strong>
                    </div>

                    {selectedProject.search_keywords && (
                      <div className="mb-3 p-3" style={{ 
                        background: '#f9fafb', 
                        borderRadius: '12px' 
                      }}>
                        <small className="text-muted d-block mb-2">Keywords</small>
                        <div className="d-flex gap-2 flex-wrap">
                          {selectedProject.search_keywords.map((keyword, idx) => (
                            <Badge key={idx} bg="secondary">
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedProject.accuracy && (
                      <div className="mb-3 p-3" style={{ 
                        background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
                        borderRadius: '12px',
                        border: '2px solid #a7f3d0'
                      }}>
                        <small className="text-muted d-block mb-1">Model Accuracy</small>
                        <strong style={{ color: '#059669', fontSize: '1.5em' }}>
                          {(selectedProject.accuracy * 100).toFixed(2)}%
                        </strong>
                      </div>
                    )}
                  </div>
                </Tab>
                
                <Tab eventKey="logs" title="Agent Logs">
                  <div className="mt-3">
                    <AgentLogsViewer projectId={selectedProject.id} />
                  </div>
                </Tab>
                
                <Tab eventKey="metadata" title="Metadata">
                  <div className="mt-3">
                    <pre style={{ 
                      background: '#1f2937',
                      color: '#f9fafb',
                      padding: '20px',
                      borderRadius: '12px',
                      fontSize: '0.85em',
                      maxHeight: '300px',
                      overflow: 'auto'
                    }}>
                      {JSON.stringify(selectedProject.metadata || {}, null, 2)}
                    </pre>
                  </div>
                </Tab>
              </Tabs>
            </>
          )}
        </Modal.Body>
        
        <Modal.Footer style={{ border: 'none', padding: '20px' }}>
          {(selectedProject?.status === 'completed' || 
            selectedProject?.status === 'export_ready') && (
            <Button
              variant="success"
              onClick={() => handleDownload(selectedProject)}
              style={{ borderRadius: '10px', fontWeight: '600' }}
            >
              <Download size={18} className="me-2" />
              Download Model
            </Button>
          )}
          <Button
            variant="outline-secondary"
            onClick={() => setShowDetailsModal(false)}
            style={{ borderRadius: '10px', fontWeight: '600' }}
          >
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 0 20px rgba(59,130,246,0.5);
          }
          50% {
            box-shadow: 0 0 30px rgba(59,130,246,0.8);
          }
        }
      `}</style>
    </div>
  );
};

export default MLProjectsPage;
