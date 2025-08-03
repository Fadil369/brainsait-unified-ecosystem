import {
    Analytics as AnalyticsIcon,
    AutoAwesome as AutoAwesomeIcon,
    Download as DownloadIcon,
    Insights as InsightsIcon,
    Psychology as PsychologyIcon,
    Refresh as RefreshIcon,
    Speed as SpeedIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import {
    Alert,
    Avatar,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Grid,
    IconButton,
    LinearProgress,
    Paper,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tabs,
    Tooltip,
    Typography
} from '@mui/material';
import { motion } from 'framer-motion';
import { useState } from 'react';
import {
    Area,
    AreaChart,
    CartesianGrid,
    PolarAngleAxis,
    PolarGrid,
    PolarRadiusAxis,
    Radar,
    RadarChart,
    ResponsiveContainer,
    XAxis,
    YAxis
} from 'recharts';
import { useLanguage } from '../hooks/useLanguage';

// Sample AI Analytics data
const aiInsights = [
  { month: 'Jan', accuracy: 95.2, predictions: 1250, savings: 185000, efficiency: 88 },
  { month: 'Feb', accuracy: 96.1, predictions: 1380, savings: 205000, efficiency: 91 },
  { month: 'Mar', accuracy: 97.3, predictions: 1520, savings: 235000, efficiency: 94 },
  { month: 'Apr', accuracy: 96.8, predictions: 1420, savings: 215000, efficiency: 92 },
  { month: 'May', accuracy: 98.1, predictions: 1650, savings: 275000, efficiency: 96 },
  { month: 'Jun', accuracy: 98.5, predictions: 1780, savings: 295000, efficiency: 98 },
];

const predictiveModels = [
  { 
    name: 'Claim Denial Prediction', 
    accuracy: 98.5, 
    lastTrained: '2024-01-15', 
    predictions: 1780,
    status: 'active',
    confidence: 95.2
  },
  { 
    name: 'Fraud Detection', 
    accuracy: 97.2, 
    lastTrained: '2024-01-12', 
    predictions: 890,
    status: 'active',
    confidence: 92.8
  },
  { 
    name: 'Patient Risk Assessment', 
    accuracy: 94.8, 
    lastTrained: '2024-01-10', 
    predictions: 2150,
    status: 'active',
    confidence: 89.5
  },
  { 
    name: 'Resource Optimization', 
    accuracy: 96.3, 
    lastTrained: '2024-01-14', 
    predictions: 650,
    status: 'training',
    confidence: 91.7
  },
];

const aiRecommendations = [
  {
    type: 'cost_optimization',
    priority: 'high',
    title: 'Optimize Emergency Department Staffing',
    description: 'AI predicts 25% reduction in wait times by adjusting staff schedules during peak hours',
    expectedSavings: 125000,
    confidence: 94.2,
    timeframe: '2 weeks'
  },
  {
    type: 'fraud_detection',
    priority: 'critical',
    title: 'Potential Billing Anomaly Detected',
    description: 'Unusual pattern in radiology billing codes requires immediate review',
    expectedSavings: 85000,
    confidence: 97.8,
    timeframe: 'immediate'
  },
  {
    type: 'efficiency',
    priority: 'medium',
    title: 'Automate Prior Authorization Process',
    description: 'ML model can approve 78% of routine authorizations automatically',
    expectedSavings: 65000,
    confidence: 91.5,
    timeframe: '1 month'
  },
  {
    type: 'quality',
    priority: 'high',
    title: 'Enhanced Clinical Decision Support',
    description: 'Implement AI-powered diagnosis assistance for complex cases',
    expectedSavings: 185000,
    confidence: 88.9,
    timeframe: '6 weeks'
  },
];

const riskAssessment = [
  { category: 'Financial Risk', current: 15, target: 8, status: 'improving' },
  { category: 'Operational Risk', current: 22, target: 12, status: 'stable' },
  { category: 'Compliance Risk', current: 8, target: 5, status: 'improving' },
  { category: 'Clinical Risk', current: 12, target: 6, status: 'attention' },
  { category: 'Technology Risk', current: 18, target: 10, status: 'improving' },
  { category: 'Security Risk', current: 6, target: 3, status: 'excellent' },
];

const performanceMetrics = [
  { metric: 'AI Model Accuracy', value: 98.5, target: 95, unit: '%' },
  { metric: 'Processing Speed', value: 2.3, target: 3.0, unit: 'sec' },
  { metric: 'Cost Savings', value: 1.8, target: 1.5, unit: 'M SAR' },
  { metric: 'Automation Rate', value: 87, target: 80, unit: '%' },
  { metric: 'Prediction Confidence', value: 94.2, target: 90, unit: '%' },
  { metric: 'System Uptime', value: 99.9, target: 99.5, unit: '%' },
];

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`ai-tabpanel-${index}`}
    aria-labelledby={`ai-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const AIAnalytics = () => {
  const { t, isRTL } = useLanguage();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'excellent': return '#06d6a0';
      case 'improving': return '#00b4d8';
      case 'stable': return '#ffd166';
      case 'attention': return '#f72585';
      default: return '#6c757d';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center">
          <PsychologyIcon sx={{ fontSize: 32, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" fontWeight="bold">
            AI {t('analytics')} & Insights
          </Typography>
        </Box>
        <Box>
          <Tooltip title="Refresh AI Models">
            <IconButton sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button variant="outlined" sx={{ mr: 1 }} startIcon={<DownloadIcon />}>
            Export Report
          </Button>
          <Button variant="contained" startIcon={<AutoAwesomeIcon />}>
            Generate Insights
          </Button>
        </Box>
      </Box>

      {/* Key AI Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      98.5%
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      AI Model Accuracy
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <TrendingUpIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        +2.1% this month
                      </Typography>
                    </Box>
                  </Box>
                  <PsychologyIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      1.8M SAR
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      AI-Generated Savings
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <TrendingUpIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        +15.2% increase
                      </Typography>
                    </Box>
                  </Box>
                  <InsightsIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      7,890
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      Predictions Made
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <SpeedIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        Real-time processing
                      </Typography>
                    </Box>
                  </Box>
                  <AnalyticsIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      87%
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      Automation Rate
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <AutoAwesomeIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        Intelligent automation
                      </Typography>
                    </Box>
                  </Box>
                  <AutoAwesomeIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Card>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="AI analytics tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Performance Metrics" />
          <Tab label="Predictive Models" />
          <Tab label="AI Recommendations" />
          <Tab label="Risk Assessment" />
        </Tabs>

        {/* Performance Metrics Tab */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            AI Performance Metrics
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={aiInsights}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="accuracy" 
                    stackId="1"
                    stroke="#667eea" 
                    fill="#667eea"
                    fillOpacity={0.8}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} lg={4}>
              <Card sx={{ p: 2, background: 'linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%)' }}>
                <Typography variant="h6" gutterBottom>
                  Performance Overview
                </Typography>
                {performanceMetrics.map((metric, index) => (
                  <Box key={index} mb={3}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="body2">{metric.metric}</Typography>
                      <Typography variant="h6" fontWeight="bold" color={
                        metric.unit === 'sec' 
                          ? (metric.value <= metric.target ? 'success.main' : 'warning.main')
                          : (metric.value >= metric.target ? 'success.main' : 'warning.main')
                      }>
                        {metric.value}{metric.unit}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={
                        metric.unit === 'sec' 
                          ? Math.min((metric.target / metric.value) * 100, 100)
                          : Math.min((metric.value / metric.target) * 100, 100)
                      }
                      sx={{ height: 8, borderRadius: 4 }}
                      color={
                        metric.unit === 'sec' 
                          ? (metric.value <= metric.target ? 'success' : 'warning')
                          : (metric.value >= metric.target ? 'success' : 'warning')
                      }
                    />
                    <Typography variant="caption" color="textSecondary">
                      Target: {metric.target}{metric.unit}
                    </Typography>
                  </Box>
                ))}
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Predictive Models Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            AI Predictive Models
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Model Name</TableCell>
                      <TableCell align="center">Accuracy</TableCell>
                      <TableCell align="center">Predictions</TableCell>
                      <TableCell align="center">Confidence</TableCell>
                      <TableCell align="center">Last Training</TableCell>
                      <TableCell align="center">Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {predictiveModels.map((model, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                              <PsychologyIcon />
                            </Avatar>
                            <Typography variant="body2" fontWeight="bold">
                              {model.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Box display="flex" alignItems="center" justifyContent="center">
                            <Typography variant="body2" sx={{ mr: 1 }}>
                              {model.accuracy}%
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={model.accuracy}
                              sx={{ width: 60, height: 6, borderRadius: 3 }}
                              color={model.accuracy > 95 ? 'success' : model.accuracy > 90 ? 'warning' : 'error'}
                            />
                          </Box>
                        </TableCell>
                        <TableCell align="center">{model.predictions.toLocaleString()}</TableCell>
                        <TableCell align="center">
                          <Chip 
                            label={`${model.confidence}%`} 
                            color={model.confidence > 90 ? 'success' : 'warning'} 
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">{model.lastTrained}</TableCell>
                        <TableCell align="center">
                          <Chip
                            label={model.status}
                            color={model.status === 'active' ? 'success' : 'warning'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Button size="small" variant="outlined">
                            Retrain
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            <Grid item xs={12} mt={3}>
              <Alert severity="info">
                <Typography variant="body2">
                  <strong>Model Performance:</strong> All AI models are performing above baseline accuracy. The Claim Denial Prediction model shows exceptional performance at 98.5% accuracy.
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </TabPanel>

        {/* AI Recommendations Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            AI-Generated Recommendations
          </Typography>
          <Grid container spacing={3}>
            {aiRecommendations.map((recommendation, index) => (
              <Grid item xs={12} md={6} key={index}>
                <motion.div whileHover={{ scale: 1.02 }}>
                  <Card sx={{ p: 3, height: '100%' }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Chip 
                        label={recommendation.priority.toUpperCase()} 
                        color={getPriorityColor(recommendation.priority)}
                        size="small"
                      />
                      <Typography variant="body2" color="textSecondary">
                        {recommendation.timeframe}
                      </Typography>
                    </Box>
                    <Typography variant="h6" fontWeight="bold" mb={1}>
                      {recommendation.title}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      {recommendation.description}
                    </Typography>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Expected Savings
                        </Typography>
                        <Typography variant="h6" fontWeight="bold" color="success.main">
                          {(recommendation.expectedSavings / 1000).toFixed(0)}K SAR
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Confidence
                        </Typography>
                        <Typography variant="h6" fontWeight="bold" color="primary.main">
                          {recommendation.confidence}%
                        </Typography>
                      </Box>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={recommendation.confidence}
                      sx={{ mb: 2, height: 8, borderRadius: 4 }}
                      color="primary"
                    />
                    <Box display="flex" justifyContent="space-between">
                      <Button size="small" variant="outlined">
                        Learn More
                      </Button>
                      <Button size="small" variant="contained">
                        Implement
                      </Button>
                    </Box>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Risk Assessment Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            AI-Powered Risk Assessment
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={6}>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={riskAssessment}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="category" />
                  <PolarRadiusAxis angle={0} domain={[0, 30]} />
                  <Radar
                    name="Current Risk"
                    dataKey="current"
                    stroke="#f72585"
                    fill="#f72585"
                    fillOpacity={0.6}
                  />
                  <Radar
                    name="Target Risk"
                    dataKey="target"
                    stroke="#06d6a0"
                    fill="#06d6a0"
                    fillOpacity={0.6}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} lg={6}>
              <Card sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Risk Analysis Summary
                </Typography>
                {riskAssessment.map((risk, index) => (
                  <Box key={index} mb={3}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="body2">{risk.category}</Typography>
                      <Box display="flex" alignItems="center">
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          {risk.current}%
                        </Typography>
                        <Chip 
                          label={risk.status} 
                          size="small"
                          sx={{ 
                            backgroundColor: getStatusColor(risk.status),
                            color: 'white',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(risk.current / 30) * 100}
                      sx={{ height: 8, borderRadius: 4, mb: 1 }}
                      color={risk.current <= risk.target ? 'success' : risk.current <= 15 ? 'warning' : 'error'}
                    />
                    <Typography variant="caption" color="textSecondary">
                      Target: {risk.target}% | Reduction needed: {Math.max(0, risk.current - risk.target)}%
                    </Typography>
                  </Box>
                ))}
              </Card>
            </Grid>
          </Grid>
          <Alert severity="warning" sx={{ mt: 3 }}>
            <Typography variant="body2">
              <strong>Risk Alert:</strong> Clinical Risk levels require immediate attention. AI recommends implementing additional quality control measures and staff training programs.
            </Typography>
          </Alert>
        </TabPanel>
      </Card>
    </Box>
  );
};

export default AIAnalytics;
