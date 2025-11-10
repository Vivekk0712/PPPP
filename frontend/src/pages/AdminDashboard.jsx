import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Spinner, Alert, Tabs, Tab, Button } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { 
  People, 
  Folder, 
  Database, 
  Cpu, 
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  Download
} from 'react-bootstrap-icons';
import { getAdminStats, getAllUsers, getAllProjects, getAllLogs } from '../services/adminApi';
import { downloadModel } from '../services/mlApi';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsRes, usersRes, projectsRes, logsRes] = await Promise.all([
        getAdminStats(),
        getAllUsers(),
        getAllProjects(50),
        getAllLogs(100)
      ]);

      setStats(statsRes.data);
      setUsers(usersRes.data.users);
      setProjects(projectsRes.data.projects);
      setLogs(logsRes.data.logs);
    } catch (err) {
      console.error('Error fetching admin data:', err);
      setError('Failed to load admin data. Please check your permissions.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadModel = async (project) => {
    try {
      const response = await downloadModel(project.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.name}_model.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading model:', error);
      alert('Failed to download model. Please try again.');
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'completed': { bg: 'success', icon: <CheckCircle size={14} /> },
      'failed': { bg: 'danger', icon: <XCircle size={14} /> },
      'pending_dataset': { bg: 'info', icon: <Clock size={14} /> },
      'pending_training': { bg: 'warning', icon: <Clock size={14} /> },
      'pending_evaluation': { bg: 'primary', icon: <Clock size={14} /> },
      'draft': { bg: 'secondary', icon: <Clock size={14} /> }
    };
    const info = statusMap[status] || statusMap['draft'];
    return (
      <Badge bg={info.bg} className="d-flex align-items-center gap-1">
        {info.icon} {status}
      </Badge>
    );
  };

  if (loading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" style={{ color: '#667eea' }} />
        <p className="mt-3 text-muted">Loading admin dashboard...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="mb-4">
          <h2 className="fw-bold mb-2" style={{ color: '#1f2937' }}>
            🔧 Admin Dashboard
          </h2>
          <p style={{ color: '#6b7280', fontSize: '1.05em' }}>
            System overview and management
          </p>
        </div>

        {/* Stats Cards */}
        <Row className="g-4 mb-4">
          <Col xs={12} md={6} lg={3}>
            <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <small className="text-muted">Total Users</small>
                    <h3 className="fw-bold mb-0 mt-1">{stats?.total_users || 0}</h3>
                  </div>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white'
                  }}>
                    <People size={24} />
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col xs={12} md={6} lg={3}>
            <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <small className="text-muted">Total Projects</small>
                    <h3 className="fw-bold mb-0 mt-1">{stats?.total_projects || 0}</h3>
                    <small className="text-success">+{stats?.recent_projects_24h || 0} today</small>
                  </div>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white'
                  }}>
                    <Folder size={24} />
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col xs={12} md={6} lg={3}>
            <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <small className="text-muted">Total Datasets</small>
                    <h3 className="fw-bold mb-0 mt-1">{stats?.total_datasets || 0}</h3>
                  </div>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white'
                  }}>
                    <Database size={24} />
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col xs={12} md={6} lg={3}>
            <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <small className="text-muted">Trained Models</small>
                    <h3 className="fw-bold mb-0 mt-1">{stats?.total_models || 0}</h3>
                  </div>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white'
                  }}>
                    <Cpu size={24} />
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Status Breakdown */}
        {stats?.status_breakdown && (
          <Row className="mb-4">
            <Col xs={12}>
              <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
                <Card.Body>
                  <h5 className="fw-bold mb-3">Project Status Breakdown</h5>
                  <Row>
                    {Object.entries(stats.status_breakdown).map(([status, count]) => (
                      <Col key={status} xs={6} md={4} lg={2} className="mb-3">
                        <div className="text-center">
                          {getStatusBadge(status)}
                          <div className="fw-bold mt-2" style={{ fontSize: '1.5em' }}>{count}</div>
                        </div>
                      </Col>
                    ))}
                  </Row>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}

        {/* Tabs for detailed data */}
        <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
          <Card.Body>
            <Tabs defaultActiveKey="users" className="mb-3">
              <Tab eventKey="users" title={`Users (${users.length})`}>
                <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                  <Table hover responsive>
                    <thead>
                      <tr>
                        <th>Firebase UID</th>
                        <th>Email</th>
                        <th>Projects</th>
                        <th>Created</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td><code style={{ fontSize: '0.85em' }}>{user.firebase_uid}</code></td>
                          <td>{user.email || 'N/A'}</td>
                          <td><Badge bg="primary">{user.project_count}</Badge></td>
                          <td>{new Date(user.created_at).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </Tab>

              <Tab eventKey="projects" title={`Projects (${projects.length})`}>
                <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                  <Table hover responsive>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>User</th>
                        <th>Status</th>
                        <th>Framework</th>
                        <th>Created</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {projects.map((project) => (
                        <tr key={project.id}>
                          <td className="fw-bold">{project.name}</td>
                          <td><code style={{ fontSize: '0.85em' }}>{project.users?.firebase_uid || 'N/A'}</code></td>
                          <td>{getStatusBadge(project.status)}</td>
                          <td><Badge bg="secondary">{project.framework || 'PyTorch'}</Badge></td>
                          <td>{new Date(project.created_at).toLocaleString()}</td>
                          <td>
                            {(project.status === 'completed' || project.status === 'export_ready') && (
                              <Button
                                size="sm"
                                variant="success"
                                onClick={() => handleDownloadModel(project)}
                                style={{ borderRadius: '8px' }}
                              >
                                <Download size={14} className="me-1" />
                                Download
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </Tab>

              <Tab eventKey="logs" title={`Logs (${logs.length})`}>
                <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                  <Table hover responsive>
                    <thead>
                      <tr>
                        <th>Time</th>
                        <th>Agent</th>
                        <th>Project</th>
                        <th>Level</th>
                        <th>Message</th>
                      </tr>
                    </thead>
                    <tbody>
                      {logs.map((log) => (
                        <tr key={log.id}>
                          <td style={{ fontSize: '0.85em' }}>{new Date(log.created_at).toLocaleString()}</td>
                          <td><Badge bg="info">{log.agent_name}</Badge></td>
                          <td style={{ fontSize: '0.85em' }}>{log.projects?.name || 'N/A'}</td>
                          <td>
                            <Badge bg={
                              log.log_level === 'error' ? 'danger' :
                              log.log_level === 'warning' ? 'warning' : 'success'
                            }>
                              {log.log_level}
                            </Badge>
                          </td>
                          <td style={{ fontSize: '0.85em', maxWidth: '400px' }}>
                            {log.message.length > 100 ? log.message.substring(0, 100) + '...' : log.message}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </Tab>
            </Tabs>
          </Card.Body>
        </Card>
      </motion.div>
    </Container>
  );
};

export default AdminDashboard;
