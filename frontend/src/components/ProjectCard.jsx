import React from 'react';
import { Card, Badge, ProgressBar, Button } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  HourglassSplit,
  Download,
  Eye
} from 'react-bootstrap-icons';

const ProjectCard = ({ project, onViewDetails, onDownload }) => {
  const getStatusInfo = (status) => {
    const statusMap = {
      'draft': { 
        color: 'secondary', 
        icon: <Clock size={16} />, 
        text: 'Draft',
        progress: 0
      },
      'pending_dataset': { 
        color: 'info', 
        icon: <HourglassSplit size={16} />, 
        text: 'Fetching Dataset',
        progress: 25
      },
      'pending_training': { 
        color: 'warning', 
        icon: <HourglassSplit size={16} />, 
        text: 'Training Model',
        progress: 50
      },
      'pending_evaluation': { 
        color: 'primary', 
        icon: <HourglassSplit size={16} />, 
        text: 'Evaluating',
        progress: 75
      },
      'completed': { 
        color: 'success', 
        icon: <CheckCircle size={16} />, 
        text: 'Completed',
        progress: 100
      },
      'export_ready': { 
        color: 'success', 
        icon: <CheckCircle size={16} />, 
        text: 'Ready to Download',
        progress: 100
      },
      'failed': { 
        color: 'danger', 
        icon: <XCircle size={16} />, 
        text: 'Failed',
        progress: 0
      }
    };
    return statusMap[status] || statusMap['draft'];
  };

  const statusInfo = getStatusInfo(project.status);
  const accuracy = project.metadata?.accuracy || project.accuracy;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, boxShadow: '0 8px 24px rgba(0,0,0,0.12)' }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-0 shadow-sm" style={{ 
        borderRadius: '16px',
        overflow: 'hidden',
        height: '100%'
      }}>
        <div style={{
          height: '6px',
          background: `linear-gradient(90deg, 
            ${statusInfo.color === 'success' ? '#10b981' : 
              statusInfo.color === 'warning' ? '#f59e0b' : 
              statusInfo.color === 'info' ? '#3b82f6' : 
              statusInfo.color === 'danger' ? '#ef4444' : '#6b7280'} 0%, 
            ${statusInfo.color === 'success' ? '#059669' : 
              statusInfo.color === 'warning' ? '#d97706' : 
              statusInfo.color === 'info' ? '#2563eb' : 
              statusInfo.color === 'danger' ? '#dc2626' : '#4b5563'} 100%)`
        }} />
        
        <Card.Body className="p-4">
          <div className="d-flex justify-content-between align-items-start mb-3">
            <div style={{ flex: 1 }}>
              <h5 className="mb-2 fw-bold" style={{ color: '#1f2937' }}>
                {project.name || 'Untitled Project'}
              </h5>
              <div className="d-flex gap-2 flex-wrap">
                <Badge 
                  bg={statusInfo.color}
                  className="d-flex align-items-center gap-1"
                  style={{ fontSize: '0.8em', padding: '6px 12px' }}
                >
                  {statusInfo.icon}
                  {statusInfo.text}
                </Badge>
                <Badge bg="light" text="dark" style={{ fontSize: '0.8em', padding: '6px 12px' }}>
                  {project.framework || 'PyTorch'}
                </Badge>
                {project.task_type && (
                  <Badge bg="light" text="dark" style={{ fontSize: '0.8em', padding: '6px 12px' }}>
                    {project.task_type.replace('_', ' ')}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {statusInfo.progress > 0 && statusInfo.progress < 100 && (
            <div className="mb-3">
              <div className="d-flex justify-content-between mb-1">
                <small className="text-muted">Progress</small>
                <small className="text-muted fw-bold">{statusInfo.progress}%</small>
              </div>
              <ProgressBar 
                now={statusInfo.progress} 
                variant={statusInfo.color}
                style={{ height: '8px', borderRadius: '4px' }}
                animated
              />
            </div>
          )}

          {accuracy && (
            <div className="mb-3 p-3" style={{ 
              background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
              borderRadius: '12px',
              border: '1px solid #bbf7d0'
            }}>
              <div className="d-flex justify-content-between align-items-center">
                <span style={{ color: '#166534', fontSize: '0.9em', fontWeight: '600' }}>
                  Model Accuracy
                </span>
                <span style={{ 
                  color: '#15803d', 
                  fontSize: '1.5em', 
                  fontWeight: 'bold' 
                }}>
                  {(accuracy * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          )}

          {project.search_keywords && project.search_keywords.length > 0 && (
            <div className="mb-3">
              <small className="text-muted d-block mb-2">Keywords:</small>
              <div className="d-flex gap-1 flex-wrap">
                {project.search_keywords.slice(0, 3).map((keyword, idx) => (
                  <span 
                    key={idx}
                    style={{
                      fontSize: '0.75em',
                      padding: '4px 10px',
                      background: '#f3f4f6',
                      color: '#4b5563',
                      borderRadius: '12px'
                    }}
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          {project.metadata?.max_dataset_size_gb && project.metadata.max_dataset_size_gb < 50 && (
            <div className="mb-3">
              <small className="text-muted d-block mb-2">Dataset Size Limit:</small>
              <span 
                style={{
                  fontSize: '0.75em',
                  padding: '4px 10px',
                  background: '#fef3c7',
                  color: '#92400e',
                  borderRadius: '12px',
                  display: 'inline-block'
                }}
              >
                📦 Max {project.metadata.max_dataset_size_gb}GB
              </span>
            </div>
          )}

          <div className="d-flex gap-2 mt-3">
            <Button
              variant="outline-primary"
              size="sm"
              onClick={() => onViewDetails(project)}
              className="flex-grow-1"
              style={{ 
                borderRadius: '10px',
                fontWeight: '600',
                padding: '8px'
              }}
            >
              <Eye size={16} className="me-1" />
              View Details
            </Button>
            
            {(project.status === 'completed' || project.status === 'export_ready') && (
              <Button
                variant="success"
                size="sm"
                onClick={() => onDownload(project)}
                style={{ 
                  borderRadius: '10px',
                  fontWeight: '600',
                  padding: '8px 16px'
                }}
              >
                <Download size={16} />
              </Button>
            )}
          </div>

          <div className="mt-3 pt-3" style={{ borderTop: '1px solid #e5e7eb' }}>
            <small className="text-muted">
              Created {new Date(project.created_at).toLocaleDateString()}
            </small>
          </div>
        </Card.Body>
      </Card>
    </motion.div>
  );
};

export default ProjectCard;
