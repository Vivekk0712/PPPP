import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Spinner, Badge } from 'react-bootstrap';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  Image as ImageIcon, 
  CheckCircle, 
  XCircle,
  Cpu
} from 'react-bootstrap-icons';
import { getMLProjects, testModel } from '../services/mlApi';

const ModelTester = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCompletedProjects();
  }, []);

  const fetchCompletedProjects = async () => {
    try {
      const response = await getMLProjects();
      const completed = (response.data.projects || []).filter(
        p => p.status === 'completed' || p.status === 'export_ready'
      );
      setProjects(completed);
    } catch (err) {
      console.error('Error fetching projects:', err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }
      
      setSelectedFile(file);
      setError(null);
      setResult(null);
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleTest = async (e) => {
    e.preventDefault();
    
    if (!selectedProject) {
      setError('Please select a model');
      return;
    }
    
    if (!selectedFile) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await testModel(selectedProject, selectedFile);
      setResult(response.data);
    } catch (err) {
      console.error('Error testing model:', err);
      setError(err.response?.data?.error || 'Failed to test model. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  return (
    <Card className="border-0 shadow-sm" style={{ borderRadius: '20px', overflow: 'hidden', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        padding: '30px',
        color: 'white'
      }}>
        <div className="d-flex align-items-center gap-3">
          <Cpu size={40} />
          <div>
            <h4 className="mb-1 fw-bold">Test Your Model</h4>
            <p className="mb-0" style={{ opacity: 0.9, fontSize: '0.95em' }}>
              Upload an image to test your trained models
            </p>
          </div>
        </div>
      </div>

      <Card.Body className="p-4">
        <Form onSubmit={handleTest}>
          <Form.Group className="mb-4">
            <Form.Label className="fw-semibold mb-2">Select Model</Form.Label>
            <Form.Select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              disabled={loading}
              style={{
                borderRadius: '12px',
                border: '2px solid #e5e7eb',
                padding: '12px',
                fontSize: '0.95em'
              }}
            >
              <option value="">Choose a trained model...</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name} 
                  {project.accuracy && ` - ${(project.accuracy * 100).toFixed(1)}% accuracy`}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-4">
            <Form.Label className="fw-semibold mb-2">Upload Image</Form.Label>
            <div
              style={{
                border: '2px dashed #d1d5db',
                borderRadius: '16px',
                padding: '40px',
                textAlign: 'center',
                background: preview ? 'transparent' : '#f9fafb',
                cursor: 'pointer',
                transition: 'all 0.3s',
                position: 'relative'
              }}
              onDragOver={(e) => {
                e.preventDefault();
                e.currentTarget.style.borderColor = '#f59e0b';
                e.currentTarget.style.background = '#fffbeb';
              }}
              onDragLeave={(e) => {
                e.currentTarget.style.borderColor = '#d1d5db';
                e.currentTarget.style.background = preview ? 'transparent' : '#f9fafb';
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.currentTarget.style.borderColor = '#d1d5db';
                e.currentTarget.style.background = preview ? 'transparent' : '#f9fafb';
                const file = e.dataTransfer.files[0];
                if (file) {
                  handleFileChange({ target: { files: [file] } });
                }
              }}
            >
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                disabled={loading}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  opacity: 0,
                  cursor: 'pointer'
                }}
              />
              
              {preview ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <img
                    src={preview}
                    alt="Preview"
                    style={{
                      maxWidth: '100%',
                      maxHeight: '300px',
                      borderRadius: '12px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleReset();
                    }}
                    className="mt-3"
                    style={{ borderRadius: '8px' }}
                  >
                    Remove Image
                  </Button>
                </motion.div>
              ) : (
                <div>
                  <Upload size={48} style={{ color: '#9ca3af', marginBottom: '16px' }} />
                  <p style={{ color: '#6b7280', marginBottom: '8px', fontSize: '0.95em' }}>
                    <strong>Click to upload</strong> or drag and drop
                  </p>
                  <p style={{ color: '#9ca3af', fontSize: '0.85em', margin: 0 }}>
                    PNG, JPG, JPEG up to 10MB
                  </p>
                </div>
              )}
            </div>
          </Form.Group>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <Alert 
                  variant="danger" 
                  className="border-0 mb-4"
                  style={{ borderRadius: '12px' }}
                >
                  <XCircle size={18} className="me-2" />
                  {error}
                </Alert>
              </motion.div>
            )}

            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Card 
                  className="border-0 mb-4"
                  style={{
                    background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
                    borderRadius: '16px',
                    border: '2px solid #a7f3d0'
                  }}
                >
                  <Card.Body className="p-4">
                    <div className="d-flex align-items-center gap-2 mb-3">
                      <CheckCircle size={24} style={{ color: '#059669' }} />
                      <h5 className="mb-0 fw-bold" style={{ color: '#065f46' }}>
                        Prediction Result
                      </h5>
                    </div>
                    
                    <div className="d-flex justify-content-between align-items-center p-3"
                      style={{
                        background: 'white',
                        borderRadius: '12px',
                        marginBottom: '12px'
                      }}
                    >
                      <span style={{ color: '#374151', fontWeight: '600' }}>
                        Predicted Class:
                      </span>
                      <Badge 
                        bg="success" 
                        style={{ 
                          fontSize: '1em', 
                          padding: '8px 16px',
                          fontWeight: '600'
                        }}
                      >
                        {result.prediction || result.class}
                      </Badge>
                    </div>

                    {result.confidence && (
                      <div className="d-flex justify-content-between align-items-center p-3"
                        style={{
                          background: 'white',
                          borderRadius: '12px'
                        }}
                      >
                        <span style={{ color: '#374151', fontWeight: '600' }}>
                          Confidence:
                        </span>
                        <span style={{ 
                          color: '#059669', 
                          fontSize: '1.2em',
                          fontWeight: 'bold'
                        }}>
                          {(result.confidence * 100).toFixed(2)}%
                        </span>
                      </div>
                    )}
                  </Card.Body>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="d-grid">
            <Button
              type="submit"
              disabled={loading || !selectedProject || !selectedFile}
              style={{
                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                border: 'none',
                borderRadius: '12px',
                padding: '14px',
                fontSize: '1em',
                fontWeight: '600',
                boxShadow: '0 4px 12px rgba(245,158,11,0.3)'
              }}
            >
              {loading ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Testing Model...
                </>
              ) : (
                <>
                  <ImageIcon size={18} className="me-2" />
                  Test Model
                </>
              )}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default ModelTester;
