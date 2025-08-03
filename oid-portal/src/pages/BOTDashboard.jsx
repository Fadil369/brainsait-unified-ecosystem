import {
  Box,
  Card,
  CardContent,
  Container,
  Grid,
  Typography,
  LinearProgress,
  Chip,
  Button,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Build,
  Engineering,
  TransferWithinAStation,
  CheckCircle,
  Schedule,
  Warning,
  TrendingUp,
  Assignment,
  School,
  Analytics,
} from '@mui/icons-material';
import { useState } from 'react';
import { useLanguage } from '../hooks/useLanguage';

const BOTDashboard = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState(0);

  // Sample BOT project data aligned with BOT.md
  const botProjects = [
    {
      id: "BOT-2025-001",
      project_name: "King Faisal Hospital RCM Transformation",
      client_organization: "King Faisal Specialist Hospital",
      project_type: "full_platform",
      contract_value_sar: 15000000,
      current_phase: "build",
      phase_progress: 65,
      build_start: "2025-01-15",
      build_end: "2025-12-15",
      operate_start: "2026-01-01",
      operate_end: "2028-12-31",
      transfer_start: "2029-01-01",
      transfer_end: "2029-12-31",
      status: "on_track",
      key_metrics: {
        staff_trained: 125,
        target_staff: 200,
        systems_integrated: 3,
        target_systems: 5,
        claims_processed: 25000,
        accuracy_rate: 96.2
      }
    },
    {
      id: "BOT-2025-002", 
      project_name: "Saudi German Hospital Network RCM",
      client_organization: "Saudi German Hospital Group",
      project_type: "rcm_operations",
      contract_value_sar: 8500000,
      current_phase: "operate",
      phase_progress: 45,
      build_start: "2024-06-01",
      build_end: "2025-05-31",
      operate_start: "2025-06-01",
      operate_end: "2027-05-31",
      transfer_start: "2027-06-01",
      transfer_end: "2028-05-31", 
      status: "on_track",
      key_metrics: {
        staff_trained: 85,
        target_staff: 150,
        systems_integrated: 4,
        target_systems: 4,
        claims_processed: 45000,
        accuracy_rate: 97.8
      }
    }
  ];

  // BOT lifecycle milestones
  const currentMilestones = [
    {
      project_id: "BOT-2025-001",
      phase: "build",
      milestone_name: "NPHIES Integration Development",
      progress: 85,
      target_date: "2025-04-30",
      status: "on_track",
      deliverables: ["NPHIES API integration", "FHIR R4 compliance", "Security certification"]
    },
    {
      project_id: "BOT-2025-001", 
      phase: "build",
      milestone_name: "Staff Training & Certification",
      progress: 62,
      target_date: "2025-08-15",
      status: "in_progress",
      deliverables: ["500+ medical coders trained", "CPC certifications", "NPHIES compliance training"]
    },
    {
      project_id: "BOT-2025-002",
      phase: "operate", 
      milestone_name: "Performance Optimization",
      progress: 78,
      target_date: "2025-12-31",
      status: "ahead",
      deliverables: ["95%+ accuracy sustained", "Cost savings demonstrated", "Client satisfaction 90%+"]
    }
  ];

  // Knowledge transfer tracking
  const knowledgeTransfers = [
    {
      project_id: "BOT-2025-002",
      transfer_type: "documentation",
      title: "Operations Procedures Manual",
      completion_status: "completed",
      recipient_count: 25,
      feedback_score: 4.8
    },
    {
      project_id: "BOT-2025-002",
      transfer_type: "training", 
      title: "Medical Coding Specialist Training",
      completion_status: "in_progress",
      recipient_count: 15,
      feedback_score: 4.6
    },
    {
      project_id: "BOT-2025-001",
      transfer_type: "technology",
      title: "Platform Technology Stack",
      completion_status: "pending",
      recipient_count: 0,
      feedback_score: null
    }
  ];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getPhaseColor = (phase) => {
    const colors = {
      planning: 'info',
      build: 'primary', 
      operate: 'success',
      transfer: 'warning',
      completed: 'default'
    };
    return colors[phase] || 'default';
  };

  const getStatusColor = (status) => {
    const colors = {
      on_track: 'success',
      ahead: 'info',
      behind: 'warning',
      at_risk: 'error'
    };
    return colors[status] || 'default';
  };

  const renderProjectCard = (project) => (
    <Card key={project.id} sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h6" gutterBottom>
              {project.project_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {project.client_organization}
            </Typography>
            <Typography variant="caption" display="block" mt={1}>
              Contract Value: SAR {project.contract_value_sar.toLocaleString()}
            </Typography>
          </Box>
          <Box textAlign="right">
            <Chip 
              label={project.current_phase.toUpperCase()} 
              color={getPhaseColor(project.current_phase)}
              sx={{ mb: 1 }}
            />
            <Chip 
              label={project.status.replace('_', ' ').toUpperCase()}
              color={getStatusColor(project.status)}
              size="small"
            />
          </Box>
        </Box>

        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Phase Progress</Typography>
            <Typography variant="body2" fontWeight="bold">
              {project.phase_progress}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={project.phase_progress}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary">
                {project.key_metrics.staff_trained}
              </Typography>
              <Typography variant="caption">Staff Trained</Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary">
                {project.key_metrics.accuracy_rate}%
              </Typography>
              <Typography variant="caption">Accuracy Rate</Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary">
                {(project.key_metrics.claims_processed / 1000).toFixed(0)}K
              </Typography>
              <Typography variant="caption">Claims Processed</Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary">
                {project.key_metrics.systems_integrated}/{project.key_metrics.target_systems}
              </Typography>
              <Typography variant="caption">Systems Integrated</Typography>
            </Box>
          </Grid>
        </Grid>

        <Box mt={2} display="flex" gap={1}>
          <Button variant="outlined" size="small" startIcon={<Analytics />}>
            View Details
          </Button>
          <Button variant="outlined" size="small" startIcon={<Assignment />}>
            Milestones
          </Button>
          <Button variant="outlined" size="small" startIcon={<TrendingUp />}>
            Metrics
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderMilestoneTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Project</TableCell>
            <TableCell>Phase</TableCell>
            <TableCell>Milestone</TableCell>
            <TableCell>Progress</TableCell>
            <TableCell>Target Date</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {currentMilestones.map((milestone, index) => (
            <TableRow key={index}>
              <TableCell>
                <Typography variant="body2" fontWeight="bold">
                  {milestone.project_id}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip 
                  label={milestone.phase.toUpperCase()} 
                  color={getPhaseColor(milestone.phase)}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {milestone.milestone_name}
                </Typography>
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  <LinearProgress 
                    variant="determinate" 
                    value={milestone.progress}
                    sx={{ width: 80, height: 6 }}
                  />
                  <Typography variant="caption">
                    {milestone.progress}%
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {milestone.target_date}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip 
                  label={milestone.status.replace('_', ' ')}
                  color={getStatusColor(milestone.status)}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Button size="small" variant="outlined">
                  Update
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderKnowledgeTransfer = () => (
    <Grid container spacing={3}>
      {knowledgeTransfers.map((transfer, index) => (
        <Grid item xs={12} md={6} key={index}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  {transfer.transfer_type === 'documentation' && <Assignment />}
                  {transfer.transfer_type === 'training' && <School />}
                  {transfer.transfer_type === 'technology' && <Engineering />}
                </Avatar>
                <Box>
                  <Typography variant="h6">
                    {transfer.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {transfer.transfer_type.toUpperCase()} • {transfer.project_id}
                  </Typography>
                </Box>
              </Box>

              <Box mb={2}>
                <Chip 
                  label={transfer.completion_status.replace('_', ' ').toUpperCase()}
                  color={transfer.completion_status === 'completed' ? 'success' : 
                         transfer.completion_status === 'in_progress' ? 'primary' : 'default'}
                  size="small"
                />
              </Box>

              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="body2">
                  Recipients: {transfer.recipient_count}
                </Typography>
                {transfer.feedback_score && (
                  <Typography variant="body2">
                    Rating: {transfer.feedback_score}/5.0
                  </Typography>
                )}
              </Box>

              <Button variant="outlined" fullWidth size="small">
                View Details
              </Button>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Build-Operate-Transfer Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Comprehensive BOT lifecycle management for healthcare transformation projects
        </Typography>

        {/* Key Performance Indicators */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={3}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <Build sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="primary">
                {botProjects.filter(p => p.current_phase === 'build').length}
              </Typography>
              <Typography variant="body2">Active BUILD Projects</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <Engineering sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {botProjects.filter(p => p.current_phase === 'operate').length}
              </Typography>
              <Typography variant="body2">OPERATE Phase</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <TransferWithinAStation sx={{ fontSize: 48, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="warning.main">
                {botProjects.filter(p => p.current_phase === 'transfer').length}
              </Typography>
              <Typography variant="body2">TRANSFER Phase</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <TrendingUp sx={{ fontSize: 48, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="info.main">
                SAR {(botProjects.reduce((sum, p) => sum + p.contract_value_sar, 0) / 1000000).toFixed(1)}M
              </Typography>
              <Typography variant="body2">Total Contract Value</Typography>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 4 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Active Projects" />
            <Tab label="Milestones & Deliverables" />
            <Tab label="Knowledge Transfer" />
            <Tab label="Performance Analytics" />
          </Tabs>
        </Box>

        {activeTab === 0 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              Active BOT Projects
            </Typography>
            {botProjects.map(renderProjectCard)}
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              Project Milestones & Deliverables
            </Typography>
            {renderMilestoneTable()}
          </Box>
        )}

        {activeTab === 2 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              Knowledge Transfer Progress
            </Typography>
            {renderKnowledgeTransfer()}
          </Box>
        )}

        {activeTab === 3 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              BOT Performance Analytics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Client Satisfaction Metrics
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                        <ListItemText 
                          primary="Overall Satisfaction: 92.5%" 
                          secondary="Target: 90%+"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                        <ListItemText 
                          primary="Knowledge Transfer Quality: 94.2%" 
                          secondary="Feedback from 150+ recipients"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                        <ListItemText 
                          primary="Operational Independence: 87%" 
                          secondary="Average across TRANSFER projects"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Business Impact Delivered
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon><TrendingUp color="primary" /></ListItemIcon>
                        <ListItemText 
                          primary="Cost Savings: SAR 45M+" 
                          secondary="Across all active projects"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><TrendingUp color="primary" /></ListItemIcon>
                        <ListItemText 
                          primary="Claims Accuracy: 96.8%" 
                          secondary="Average across all projects"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><TrendingUp color="primary" /></ListItemIcon>
                        <ListItemText 
                          primary="Staff Certified: 1,250+" 
                          secondary="Medical coding professionals"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default BOTDashboard;