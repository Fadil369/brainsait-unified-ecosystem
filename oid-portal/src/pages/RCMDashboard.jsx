import {
    CheckCircle as CheckCircleIcon,
    MonetizationOn as MoneyIcon,
    Savings as SavingsIcon,
    Schedule as ScheduleIcon,
    TrendingDown as TrendingDownIcon,
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
    Divider,
    Grid,
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
    Typography
} from '@mui/material';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { useLanguage } from '../hooks/useLanguage';

// Sample RCM data
const rcmMetrics = [
  { month: 'Jan', revenue: 2400000, collected: 2200000, denials: 50000, avgDays: 28 },
  { month: 'Feb', revenue: 2800000, collected: 2650000, denials: 45000, avgDays: 25 },
  { month: 'Mar', revenue: 3200000, collected: 3050000, denials: 55000, avgDays: 23 },
  { month: 'Apr', revenue: 2900000, collected: 2750000, denials: 48000, avgDays: 26 },
  { month: 'May', revenue: 3500000, collected: 3350000, denials: 52000, avgDays: 22 },
  { month: 'Jun', revenue: 3800000, collected: 3650000, denials: 47000, avgDays: 21 },
];

const organizationPerformance = [
  { name: 'King Faisal Hospital', claims: 450, approved: 425, denied: 25, revenue: 1850000, collectionRate: 94.4 },
  { name: 'Saudi German Hospital', claims: 380, approved: 350, denied: 30, revenue: 1520000, collectionRate: 92.1 },
  { name: 'Dr. Sulaiman Al Habib', claims: 520, approved: 495, denied: 25, revenue: 2180000, collectionRate: 95.2 },
  { name: 'National Guard Hospital', claims: 320, approved: 300, denied: 20, revenue: 1340000, collectionRate: 93.8 },
];

const denialReasons = [
  { reason: 'Missing Documentation', count: 45, percentage: 28 },
  { reason: 'Invalid Procedure Code', count: 32, percentage: 20 },
  { reason: 'Prior Authorization Required', count: 28, percentage: 17 },
  { reason: 'Patient Not Eligible', count: 25, percentage: 15 },
  { reason: 'Duplicate Claim', count: 20, percentage: 12 },
  { reason: 'Other', count: 13, percentage: 8 },
];

const costSavingsData = [
  { category: 'Duplicate Detection', savings: 485000, color: '#06d6a0' },
  { category: 'AI-Powered Coding', savings: 320000, color: '#00b4d8' },
  { category: 'Automated Workflows', savings: 275000, color: '#f72585' },
  { category: 'Denial Prevention', savings: 195000, color: '#ffd166' },
];

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`rcm-tabpanel-${index}`}
    aria-labelledby={`rcm-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const RCMDashboard = () => {
  const { t, isRTL } = useLanguage();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Calculate total statistics
  const totalStats = {
    totalRevenue: rcmMetrics.reduce((sum, m) => sum + m.revenue, 0),
    totalCollected: rcmMetrics.reduce((sum, m) => sum + m.collected, 0),
    totalDenials: rcmMetrics.reduce((sum, m) => sum + m.denials, 0),
    avgCollectionDays: rcmMetrics.reduce((sum, m) => sum + m.avgDays, 0) / rcmMetrics.length,
    totalSavings: costSavingsData.reduce((sum, s) => sum + s.savings, 0),
  };

  const collectionRate = ((totalStats.totalCollected / totalStats.totalRevenue) * 100).toFixed(1);
  const denialRate = ((totalStats.totalDenials / totalStats.totalRevenue) * 100).toFixed(1);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {t('rcm')} {t('dashboard')}
        </Typography>
        <Box>
          <Button variant="outlined" sx={{ mr: 1 }}>
            {t('export')} Report
          </Button>
          <Button variant="contained">
            Generate Insights
          </Button>
        </Box>
      </Box>

      {/* Key Performance Indicators */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #00b4d8 0%, #0077b6 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      {(totalStats.totalRevenue / 1000000).toFixed(1)}M SAR
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      Total Revenue
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <TrendingUpIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        +12.5% from last month
                      </Typography>
                    </Box>
                  </Box>
                  <MoneyIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #06d6a0 0%, #048a81 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      {collectionRate}%
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('collectionRate')}
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <TrendingUpIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        +2.3% improvement
                      </Typography>
                    </Box>
                  </Box>
                  <CheckCircleIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #ffd166 0%, #ffb700 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      {totalStats.avgCollectionDays.toFixed(0)} Days
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('avgCollectionDays')}
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <TrendingDownIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        -3.2 days improvement
                      </Typography>
                    </Box>
                  </Box>
                  <ScheduleIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ Scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #f72585 0%, #c41e3a 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color="white">
                      {(totalStats.totalSavings / 1000000).toFixed(1)}M SAR
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('costSavings')}
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <SavingsIcon sx={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', mr: 0.5 }} />
                      <Typography variant="caption" color="rgba(255,255,255,0.8)">
                        AI-powered optimization
                      </Typography>
                    </Box>
                  </Box>
                  <SavingsIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
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
          aria-label="RCM dashboard tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label={t('revenueAnalytics')} />
          <Tab label={t('denialManagement')} />
          <Tab label="Organization Performance" />
          <Tab label={t('costSavings')} />
        </Tabs>

        {/* Revenue Analytics Tab */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            {t('revenueAnalytics')}
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={rcmMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`} />
                  <Tooltip 
                    formatter={(value) => [`${(value / 1000000).toFixed(2)}M SAR`, '']}
                    labelFormatter={(label) => `Month: ${label}`}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="revenue" 
                    stackId="1"
                    stroke="#00b4d8" 
                    fill="#00b4d8"
                    fillOpacity={0.6}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="collected" 
                    stackId="2"
                    stroke="#06d6a0" 
                    fill="#06d6a0"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} lg={4}>
              <Card sx={{ p: 2, background: 'linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%)' }}>
                <Typography variant="h6" gutterBottom>
                  Revenue Breakdown
                </Typography>
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    Total Billed
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="primary.main">
                    {(totalStats.totalRevenue / 1000000).toFixed(1)}M SAR
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    Total Collected
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="success.main">
                    {(totalStats.totalCollected / 1000000).toFixed(1)}M SAR
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    Outstanding AR
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="warning.main">
                    {((totalStats.totalRevenue - totalStats.totalCollected) / 1000000).toFixed(1)}M SAR
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Collection Efficiency
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="info.main">
                    {collectionRate}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={parseFloat(collectionRate)} 
                    sx={{ mt: 1, height: 8, borderRadius: 4 }}
                    color="success"
                  />
                </Box>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Denial Management Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            {t('denialManagement')}
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={6}>
              <Card sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Top Denial Reasons
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Reason</TableCell>
                        <TableCell align="center">Count</TableCell>
                        <TableCell align="center">Percentage</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {denialReasons.map((reason, index) => (
                        <TableRow key={index}>
                          <TableCell>{reason.reason}</TableCell>
                          <TableCell align="center">{reason.count}</TableCell>
                          <TableCell align="center">
                            <Box display="flex" alignItems="center" justifyContent="center">
                              <Typography variant="body2" sx={{ mr: 1 }}>
                                {reason.percentage}%
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={reason.percentage}
                                sx={{ width: 60, height: 6, borderRadius: 3 }}
                                color={reason.percentage > 20 ? 'error' : reason.percentage > 15 ? 'warning' : 'success'}
                              />
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Card>
            </Grid>
            <Grid item xs={12} lg={6}>
              <Card sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Denial Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={rcmMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`} />
                    <Tooltip formatter={(value) => [`${(value / 1000).toFixed(1)}K SAR`, 'Denials']} />
                    <Bar dataKey="denials" fill="#f72585" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
                <Alert severity="success" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Denial rate decreased by 15% this quarter through AI-powered claim validation.
                  </Typography>
                </Alert>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Organization Performance Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Healthcare Organization Performance
          </Typography>
          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Organization</TableCell>
                  <TableCell align="center">Total Claims</TableCell>
                  <TableCell align="center">Approved</TableCell>
                  <TableCell align="center">Denied</TableCell>
                  <TableCell align="right">Revenue (SAR)</TableCell>
                  <TableCell align="center">Collection Rate</TableCell>
                  <TableCell align="center">Performance</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {organizationPerformance.map((org, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                          {org.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
                        </Avatar>
                        <Typography variant="body2" fontWeight="bold">
                          {org.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">{org.claims}</TableCell>
                    <TableCell align="center">
                      <Chip 
                        label={org.approved} 
                        color="success" 
                        size="small" 
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip 
                        label={org.denied} 
                        color="error" 
                        size="small" 
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {org.revenue.toLocaleString()}
                    </TableCell>
                    <TableCell align="center">
                      <Box display="flex" alignItems="center" justifyContent="center">
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          {org.collectionRate}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={org.collectionRate}
                          sx={{ width: 60, height: 6, borderRadius: 3 }}
                          color={org.collectionRate > 94 ? 'success' : org.collectionRate > 92 ? 'warning' : 'error'}
                        />
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={org.collectionRate > 94 ? 'Excellent' : org.collectionRate > 92 ? 'Good' : 'Needs Improvement'}
                        color={org.collectionRate > 94 ? 'success' : org.collectionRate > 92 ? 'warning' : 'error'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Cost Savings Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            {t('costSavings')} Analysis
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={6}>
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={costSavingsData}
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="savings"
                    label={({ category, savings }) => `${category}: ${(savings / 1000).toFixed(0)}K SAR`}
                  >
                    {costSavingsData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${(value / 1000).toFixed(0)}K SAR`, 'Savings']} />
                </PieChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} lg={6}>
              <Card sx={{ p: 3, background: 'linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%)' }}>
                <Typography variant="h6" gutterBottom>
                  Cost Savings Breakdown
                </Typography>
                {costSavingsData.map((item, index) => (
                  <Box key={index} mb={3}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="body2">{item.category}</Typography>
                      <Typography variant="h6" fontWeight="bold" style={{ color: item.color }}>
                        {(item.savings / 1000).toFixed(0)}K SAR
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(item.savings / totalStats.totalSavings) * 100}
                      sx={{ 
                        height: 8, 
                        borderRadius: 4,
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: item.color,
                        }
                      }}
                    />
                    <Typography variant="caption" color="textSecondary">
                      {((item.savings / totalStats.totalSavings) * 100).toFixed(1)}% of total savings
                    </Typography>
                  </Box>
                ))}
                <Divider sx={{ my: 2 }} />
                <Box>
                  <Typography variant="h5" fontWeight="bold" color="success.main">
                    Total: {(totalStats.totalSavings / 1000000).toFixed(1)}M SAR
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Annual cost savings through BrainSAIT AI optimization
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>
          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="body2">
              <strong>AI-Powered Insights:</strong> Our machine learning algorithms have identified potential additional savings of 450K SAR through workflow optimization and predictive denial prevention.
            </Typography>
          </Alert>
        </TabPanel>
      </Card>
    </Box>
  );
};

export default RCMDashboard;
