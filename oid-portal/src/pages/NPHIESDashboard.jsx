import {
    Add as AddIcon,
    Cancel as CancelIcon,
    CheckCircle as CheckCircleIcon,
    Receipt as ReceiptIcon,
    Schedule as ScheduleIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    Grid,
    MenuItem,
    Paper,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tabs,
    TextField,
    Typography
} from '@mui/material';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { useLanguage } from '../hooks/useLanguage';

// Sample data for NPHIES claims
const sampleClaimsData = [
  { id: 'CLM001', patientId: 'PT001', providerId: 'PR001', amount: 1500, status: 'approved', date: '2025-01-15' },
  { id: 'CLM002', patientId: 'PT002', providerId: 'PR002', amount: 3200, status: 'pending', date: '2025-01-14' },
  { id: 'CLM003', patientId: 'PT003', providerId: 'PR001', amount: 850, status: 'denied', date: '2025-01-13' },
  { id: 'CLM004', patientId: 'PT004', providerId: 'PR003', amount: 2100, status: 'approved', date: '2025-01-12' },
];

const chartData = [
  { name: 'Jan', approved: 240, denied: 15, pending: 30 },
  { name: 'Feb', approved: 300, denied: 20, pending: 25 },
  { name: 'Mar', approved: 280, denied: 18, pending: 35 },
  { name: 'Apr', approved: 350, denied: 22, pending: 40 },
  { name: 'May', approved: 420, denied: 25, pending: 45 },
  { name: 'Jun', approved: 380, denied: 20, pending: 35 },
];

const statusDistribution = [
  { name: 'Approved', value: 75, color: '#06d6a0' },
  { name: 'Pending', value: 15, color: '#ffd166' },
  { name: 'Denied', value: 10, color: '#f72585' },
];

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`nphies-tabpanel-${index}`}
    aria-labelledby={`nphies-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const NPHIESDashboard = () => {
  const { t, isRTL } = useLanguage();
  const [tabValue, setTabValue] = useState(0);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    claim_id: '',
    patient_nphies_id: '',
    provider_nphies_id: '',
    claim_type: 'outpatient',
    amount: '',
    diagnosis_codes: [],
    procedure_codes: [],
  });

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'denied': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircleIcon fontSize="small" />;
      case 'pending': return <ScheduleIcon fontSize="small" />;
      case 'denied': return <CancelIcon fontSize="small" />;
      default: return <ReceiptIcon fontSize="small" />;
    }
  };

  // Calculate statistics
  const stats = {
    totalClaims: sampleClaimsData.length,
    approvedClaims: sampleClaimsData.filter(c => c.status === 'approved').length,
    deniedClaims: sampleClaimsData.filter(c => c.status === 'denied').length,
    pendingClaims: sampleClaimsData.filter(c => c.status === 'pending').length,
    totalAmount: sampleClaimsData.reduce((sum, c) => sum + c.amount, 0),
    approvedAmount: sampleClaimsData.filter(c => c.status === 'approved').reduce((sum, c) => sum + c.amount, 0),
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {t('nphies')} {t('dashboard')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
          sx={{ borderRadius: 2 }}
        >
          {t('claimsSubmission')}
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #00b4d8 0%, #0077b6 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold" color="white">
                      {stats.totalClaims}
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('totalClaims')}
                    </Typography>
                  </Box>
                  <ReceiptIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
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
                    <Typography variant="h4" fontWeight="bold" color="white">
                      {stats.approvedClaims}
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('approvedClaims')}
                    </Typography>
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
                    <Typography variant="h4" fontWeight="bold" color="white">
                      {stats.pendingClaims}
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('pendingClaims')}
                    </Typography>
                  </Box>
                  <ScheduleIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.02 }}>
            <Card sx={{ background: 'linear-gradient(135deg, #f72585 0%, #c41e3a 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold" color="white">
                      {((stats.approvedAmount / stats.totalAmount) * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('collectionRate')}
                    </Typography>
                  </Box>
                  <TrendingUpIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
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
          aria-label="NPHIES dashboard tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label={t('claimsTracking')} />
          <Tab label={t('revenueAnalytics')} />
          <Tab label={t('eligibilityVerification')} />
          <Tab label={t('preAuthorization')} />
        </Tabs>

        {/* Claims Tracking Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <Typography variant="h6" gutterBottom>
                {t('claimsTracking')}
              </Typography>
              <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Claim ID</TableCell>
                      <TableCell>Patient ID</TableCell>
                      <TableCell>Provider ID</TableCell>
                      <TableCell align="right">Amount (SAR)</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sampleClaimsData.map((claim) => (
                      <TableRow key={claim.id} hover>
                        <TableCell>{claim.id}</TableCell>
                        <TableCell>{claim.patientId}</TableCell>
                        <TableCell>{claim.providerId}</TableCell>
                        <TableCell align="right">
                          {claim.amount.toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(claim.status)}
                            label={t(claim.status)}
                            color={getStatusColor(claim.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{claim.date}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>

            <Grid item xs={12} lg={4}>
              <Typography variant="h6" gutterBottom>
                Status Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {statusDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Revenue Analytics Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            {t('revenueAnalytics')}
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="approved" stroke="#06d6a0" strokeWidth={3} />
                  <Line type="monotone" dataKey="denied" stroke="#f72585" strokeWidth={3} />
                  <Line type="monotone" dataKey="pending" stroke="#ffd166" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} lg={4}>
              <Card sx={{ p: 2, background: 'linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%)' }}>
                <Typography variant="h6" gutterBottom>
                  Revenue Summary
                </Typography>
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    Total Revenue
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="primary.main">
                    {stats.totalAmount.toLocaleString()} SAR
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    Collected Revenue
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {stats.approvedAmount.toLocaleString()} SAR
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Collection Rate
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="warning.main">
                    {((stats.approvedAmount / stats.totalAmount) * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Eligibility Verification Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            {t('eligibilityVerification')}
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            This feature allows real-time verification of patient eligibility through NPHIES platform.
          </Alert>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Patient Eligibility Check
                </Typography>
                <TextField
                  fullWidth
                  label="Patient NPHIES ID"
                  margin="normal"
                  placeholder="Enter patient NPHIES ID"
                />
                <TextField
                  fullWidth
                  label="Insurance ID"
                  margin="normal"
                  placeholder="Enter insurance ID"
                />
                <Button
                  variant="contained"
                  sx={{ mt: 2 }}
                  fullWidth
                >
                  Verify Eligibility
                </Button>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ p: 3, backgroundColor: 'success.dark', color: 'white' }}>
                <Typography variant="h6" gutterBottom>
                  Verification Result
                </Typography>
                <Typography variant="body1" paragraph>
                  Patient is eligible for the requested services.
                </Typography>
                <Typography variant="body2">
                  Coverage: Comprehensive Health Insurance
                </Typography>
                <Typography variant="body2">
                  Valid Until: December 31, 2025
                </Typography>
                <Typography variant="body2">
                  Copayment: 20%
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Pre-Authorization Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            {t('preAuthorization')}
          </Typography>
          <Alert severity="warning" sx={{ mb: 3 }}>
            Pre-authorization is required for certain procedures and high-value treatments.
          </Alert>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Submit Pre-Authorization Request
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Patient NPHIES ID"
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Provider NPHIES ID"
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Procedure Code"
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Estimated Cost (SAR)"
                      type="number"
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Clinical Justification"
                      multiline
                      rows={4}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      variant="contained"
                      color="primary"
                      size="large"
                    >
                      Submit Pre-Authorization Request
                    </Button>
                  </Grid>
                </Grid>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Card>

      {/* Claim Submission Dialog */}
      <Dialog 
        open={open} 
        onClose={() => setOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { borderRadius: 2 }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight="bold">
            {t('claimsSubmission')}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Claim ID"
                value={formData.claim_id}
                onChange={(e) => setFormData({ ...formData, claim_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Patient NPHIES ID"
                value={formData.patient_nphies_id}
                onChange={(e) => setFormData({ ...formData, patient_nphies_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Provider NPHIES ID"
                value={formData.provider_nphies_id}
                onChange={(e) => setFormData({ ...formData, provider_nphies_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Claim Type"
                select
                value={formData.claim_type}
                onChange={(e) => setFormData({ ...formData, claim_type: e.target.value })}
              >
                <MenuItem value="outpatient">Outpatient</MenuItem>
                <MenuItem value="inpatient">Inpatient</MenuItem>
                <MenuItem value="emergency">Emergency</MenuItem>
                <MenuItem value="pharmacy">Pharmacy</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Amount (SAR)"
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('cancel')}</Button>
          <Button variant="contained">
            Submit Claim
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NPHIESDashboard;
