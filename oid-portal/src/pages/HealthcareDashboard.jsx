import {
    Add as AddIcon,
    Analytics as AnalyticsIcon,
    Business as BusinessIcon,
    Delete as DeleteIcon,
    Edit as EditIcon,
    LocalHospital as HospitalIcon,
    Person as PersonIcon,
    Visibility as ViewIcon
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
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography
} from '@mui/material';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { toast } from 'react-hot-toast';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { useLanguage } from '../hooks/useLanguage';

// API functions
const fetchHealthcareIdentities = async () => {
  const response = await fetch('/api/healthcare-identities');
  if (!response.ok) throw new Error('Failed to fetch healthcare identities');
  return response.json();
};

const createHealthcareIdentity = async (data) => {
  const response = await fetch('/api/healthcare-identities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create healthcare identity');
  return response.json();
};

const HealthcareDashboard = () => {
  const { t, isRTL } = useLanguage();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [selectedIdentity, setSelectedIdentity] = useState(null);
  const [formData, setFormData] = useState({
    entity_type: 'provider',
    user_id: '',
    name: '',
    name_ar: '',
    role: 'physician',
    access_level: 'medium',
    organization: '',
    department: '',
    national_id: '',
    nphies_id: '',
    expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  });

  // Fetch healthcare identities
  const { data: identitiesData, isLoading, error } = useQuery(
    'healthcare-identities',
    fetchHealthcareIdentities,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  // Create identity mutation
  const createMutation = useMutation(createHealthcareIdentity, {
    onSuccess: () => {
      queryClient.invalidateQueries('healthcare-identities');
      toast.success(t('success'));
      setOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const resetForm = () => {
    setFormData({
      entity_type: 'provider',
      user_id: '',
      name: '',
      name_ar: '',
      role: 'physician',
      access_level: 'medium',
      organization: '',
      department: '',
      national_id: '',
      nphies_id: '',
      expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    });
  };

  const handleSubmit = () => {
    createMutation.mutate(formData);
  };

  const getEntityTypeIcon = (type) => {
    switch (type) {
      case 'patient': return <PersonIcon />;
      case 'provider': return <HospitalIcon />;
      case 'organization': return <BusinessIcon />;
      default: return <AnalyticsIcon />;
    }
  };

  const getAccessLevelColor = (level) => {
    switch (level) {
      case 'low': return 'info';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  // Calculate statistics
  const stats = identitiesData?.identities ? {
    total: identitiesData.identities.length,
    providers: identitiesData.identities.filter(i => i.entity_type === 'provider').length,
    patients: identitiesData.identities.filter(i => i.entity_type === 'patient').length,
    organizations: identitiesData.identities.filter(i => i.entity_type === 'organization').length,
  } : { total: 0, providers: 0, patients: 0, organizations: 0 };

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error.message}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {t('healthcare')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
          sx={{ borderRadius: 2 }}
        >
          {t('identityRegistration')}
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
                      {stats.total}
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('totalIdentities')}
                    </Typography>
                  </Box>
                  <PersonIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
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
                      {stats.providers}
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('activeProviders')}
                    </Typography>
                  </Box>
                  <HospitalIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
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
                      {stats.patients}
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('patient')}s
                    </Typography>
                  </Box>
                  <PersonIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
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
                      {stats.organizations}
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {t('organizationManagement')}
                    </Typography>
                  </Box>
                  <BusinessIcon sx={{ fontSize: 40, color: 'rgba(255,255,255,0.8)' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Healthcare Identities Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {t('healthcare')} {t('totalIdentities')}
          </Typography>
          
          {isLoading && <LinearProgress sx={{ mb: 2 }} />}
          
          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{t('name')}</TableCell>
                  <TableCell>{t('role')}</TableCell>
                  <TableCell>{t('organization')}</TableCell>
                  <TableCell>{t('accessLevel')}</TableCell>
                  <TableCell>{t('nphiesId')}</TableCell>
                  <TableCell align="center">{t('edit')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {identitiesData?.identities?.map((identity) => (
                  <TableRow key={identity.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getEntityTypeIcon(identity.entity_type)}
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {isRTL && identity.name_ar ? identity.name_ar : identity.name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {identity.full_oid}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={t(identity.role)} 
                        variant="outlined" 
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{identity.organization || '-'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={t(identity.access_level)} 
                        color={getAccessLevelColor(identity.access_level)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{identity.nphies_id || '-'}</TableCell>
                    <TableCell align="center">
                      <IconButton size="small" color="primary">
                        <ViewIcon />
                      </IconButton>
                      <IconButton size="small" color="warning">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Registration Dialog */}
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
            {t('identityRegistration')}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('provider')}</InputLabel>
                <Select
                  value={formData.entity_type}
                  onChange={(e) => setFormData({ ...formData, entity_type: e.target.value })}
                >
                  <MenuItem value="patient">{t('patient')}</MenuItem>
                  <MenuItem value="provider">{t('provider')}</MenuItem>
                  <MenuItem value="organization">{t('organization')}</MenuItem>
                  <MenuItem value="device">{t('device')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('role')}
                select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              >
                <MenuItem value="patient">{t('patient')}</MenuItem>
                <MenuItem value="physician">{t('physician')}</MenuItem>
                <MenuItem value="nurse">{t('nurse')}</MenuItem>
                <MenuItem value="pharmacist">{t('pharmacist')}</MenuItem>
                <MenuItem value="technician">{t('technician')}</MenuItem>
                <MenuItem value="administrator">{t('administrator')}</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('name')}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('nameAr')}
                value={formData.name_ar}
                onChange={(e) => setFormData({ ...formData, name_ar: e.target.value })}
                InputProps={{
                  dir: 'rtl'
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('organization')}
                value={formData.organization}
                onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('department')}
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('nationalId')}
                value={formData.national_id}
                onChange={(e) => setFormData({ ...formData, national_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('nphiesId')}
                value={formData.nphies_id}
                onChange={(e) => setFormData({ ...formData, nphies_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('accessLevel')}
                select
                value={formData.access_level}
                onChange={(e) => setFormData({ ...formData, access_level: e.target.value })}
              >
                <MenuItem value="low">{t('low')}</MenuItem>
                <MenuItem value="medium">{t('medium')}</MenuItem>
                <MenuItem value="high">{t('high')}</MenuItem>
                <MenuItem value="critical">{t('critical')}</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('expirationDate')}
                type="date"
                value={formData.expires}
                onChange={(e) => setFormData({ ...formData, expires: e.target.value })}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('cancel')}</Button>
          <Button 
            variant="contained" 
            onClick={handleSubmit}
            disabled={createMutation.isLoading}
          >
            {createMutation.isLoading ? t('loading') : t('save')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HealthcareDashboard;
