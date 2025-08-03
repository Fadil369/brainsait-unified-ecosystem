/**
 * Healthcare Identity Management Component
 * Consolidated from HealthcareDashboard.jsx with enhanced features
 * Includes Arabic support and real-time updates
 */

import { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  HealthAndSafety,
  Business,
  LocalHospital
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useLanguage } from '../../hooks/useLanguage';

// Mock API functions (would connect to actual backend)
const fetchHealthcareIdentities = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    identities: [
      {
        id: '1',
        name: 'Dr. Ahmed Al-Rashid',
        name_ar: 'د. أحمد الراشد',
        entity_type: 'provider',
        role: 'physician',
        organization: 'King Fahd University Hospital',
        organization_ar: 'مستشفى الملك فهد الجامعي',
        access_level: 'high',
        nphies_id: 'NPHIES_001',
        full_oid: '1.3.6.1.4.1.61026.1.2.001',
        status: 'active'
      },
      {
        id: '2',
        name: 'Nurse Sara Mohamed',
        name_ar: 'الممرضة سارة محمد',
        entity_type: 'provider',
        role: 'nurse',
        organization: 'Riyadh Medical Complex',
        organization_ar: 'مجمع الرياض الطبي',
        access_level: 'medium',
        nphies_id: 'NPHIES_002',
        full_oid: '1.3.6.1.4.1.61026.1.2.002',
        status: 'active'
      },
      {
        id: '3',
        name: 'Patient Ali Hassan',
        name_ar: 'المريض علي حسن',
        entity_type: 'patient',
        role: 'patient',
        organization: null,
        access_level: 'low',
        nphies_id: 'NPHIES_003',
        full_oid: '1.3.6.1.4.1.61026.1.1.003',
        status: 'active'
      }
    ]
  };
};

const createHealthcareIdentity = async (data) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  return {
    id: Date.now().toString(),
    full_oid: `1.3.6.1.4.1.61026.1.${data.entity_type === 'patient' ? '1' : '2'}.${Date.now()}`,
    ...data,
    status: 'active'
  };
};

const HealthcareIdentityManagement = ({ data, isLoading: propLoading, error: propError }) => {
  const { currentLanguage, isRTL } = useLanguage();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    entity_type: 'provider',
    name: '',
    name_ar: '',
    role: 'physician',
    access_level: 'medium',
    organization: '',
    organization_ar: '',
    department: '',
    national_id: '',
    nphies_id: ''
  });

  // Fetch healthcare identities
  const { data: identitiesData, isLoading, error } = useQuery(
    'healthcare-identities',
    fetchHealthcareIdentities,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      staleTime: 10000
    }
  );

  // Create identity mutation
  const createMutation = useMutation(createHealthcareIdentity, {
    onSuccess: () => {
      queryClient.invalidateQueries('healthcare-identities');
      setOpen(false);
      resetForm();
    }
  });

  const resetForm = () => {
    setFormData({
      entity_type: 'provider',
      name: '',
      name_ar: '',
      role: 'physician',
      access_level: 'medium',
      organization: '',
      organization_ar: '',
      department: '',
      national_id: '',
      nphies_id: ''
    });
  };

  const handleSubmit = () => {
    createMutation.mutate(formData);
  };

  const getEntityTypeIcon = (type) => {
    switch (type) {
      case 'patient': return <PersonIcon />;
      case 'provider': return <HealthAndSafety />;
      case 'organization': return <Business />;
      default: return <LocalHospital />;
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
  const stats = useMemo(() => {
    if (!identitiesData?.identities) return { total: 0, providers: 0, patients: 0, organizations: 0 };
    
    const identities = identitiesData.identities;
    return {
      total: identities.length,
      providers: identities.filter(i => i.entity_type === 'provider').length,
      patients: identities.filter(i => i.entity_type === 'patient').length,
      organizations: identities.filter(i => i.entity_type === 'organization').length,
    };
  }, [identitiesData]);

  if (error || propError) {
    return (
      <Alert severity="error">
        {error?.message || propError || 'Failed to load healthcare identities'}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header with Statistics */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="bold">
          {currentLanguage === 'ar' ? 'إدارة الهوية الطبية' : 'Healthcare Identity Management'}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          {currentLanguage === 'ar' ? 'تسجيل هوية جديدة' : 'Register New Identity'}
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        {[
          { 
            key: 'total', 
            label: { en: 'Total Identities', ar: 'إجمالي الهويات' }, 
            color: 'primary', 
            icon: PersonIcon 
          },
          { 
            key: 'providers', 
            label: { en: 'Healthcare Providers', ar: 'مقدمو الرعاية' }, 
            color: 'success', 
            icon: HealthAndSafety 
          },
          { 
            key: 'patients', 
            label: { en: 'Patients', ar: 'المرضى' }, 
            color: 'info', 
            icon: PersonIcon 
          },
          { 
            key: 'organizations', 
            label: { en: 'Organizations', ar: 'المؤسسات' }, 
            color: 'warning', 
            icon: Business 
          }
        ].map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <Grid item xs={12} sm={6} md={3} key={stat.key}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography variant="h4" fontWeight="bold" color={`${stat.color}.main`}>
                          {stats[stat.key]}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {stat.label[currentLanguage]}
                        </Typography>
                      </Box>
                      <IconComponent sx={{ fontSize: 32, color: `${stat.color}.main`, opacity: 0.7 }} />
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          );
        })}
      </Grid>

      {/* Healthcare Identities Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {currentLanguage === 'ar' ? 'الهويات الطبية المسجلة' : 'Registered Healthcare Identities'}
          </Typography>
          
          {(isLoading || propLoading) && <LinearProgress sx={{ mb: 2 }} />}
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    {currentLanguage === 'ar' ? 'الاسم' : 'Name'}
                  </TableCell>
                  <TableCell>
                    {currentLanguage === 'ar' ? 'الدور' : 'Role'}
                  </TableCell>
                  <TableCell>
                    {currentLanguage === 'ar' ? 'المؤسسة' : 'Organization'}
                  </TableCell>
                  <TableCell>
                    {currentLanguage === 'ar' ? 'مستوى الوصول' : 'Access Level'}
                  </TableCell>
                  <TableCell>
                    {currentLanguage === 'ar' ? 'معرف نفيس' : 'NPHIES ID'}
                  </TableCell>
                  <TableCell align="center">
                    {currentLanguage === 'ar' ? 'الإجراءات' : 'Actions'}
                  </TableCell>
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
                            {currentLanguage === 'ar' && identity.name_ar 
                              ? identity.name_ar 
                              : identity.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {identity.full_oid}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={identity.role} 
                        variant="outlined" 
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {currentLanguage === 'ar' && identity.organization_ar
                        ? identity.organization_ar
                        : identity.organization || '-'}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={identity.access_level} 
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
                )) || (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="text.secondary">
                        {currentLanguage === 'ar' ? 'لا توجد هويات مسجلة' : 'No identities registered'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Registration Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {currentLanguage === 'ar' ? 'تسجيل هوية طبية جديدة' : 'Register New Healthcare Identity'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>
                  {currentLanguage === 'ar' ? 'نوع الكيان' : 'Entity Type'}
                </InputLabel>
                <Select
                  value={formData.entity_type}
                  onChange={(e) => setFormData({ ...formData, entity_type: e.target.value })}
                >
                  <MenuItem value="patient">
                    {currentLanguage === 'ar' ? 'مريض' : 'Patient'}
                  </MenuItem>
                  <MenuItem value="provider">
                    {currentLanguage === 'ar' ? 'مقدم رعاية' : 'Healthcare Provider'}
                  </MenuItem>
                  <MenuItem value="organization">
                    {currentLanguage === 'ar' ? 'مؤسسة' : 'Organization'}
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={currentLanguage === 'ar' ? 'الدور' : 'Role'}
                select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              >
                <MenuItem value="patient">{currentLanguage === 'ar' ? 'مريض' : 'Patient'}</MenuItem>
                <MenuItem value="physician">{currentLanguage === 'ar' ? 'طبيب' : 'Physician'}</MenuItem>
                <MenuItem value="nurse">{currentLanguage === 'ar' ? 'ممرض' : 'Nurse'}</MenuItem>
                <MenuItem value="pharmacist">{currentLanguage === 'ar' ? 'صيدلي' : 'Pharmacist'}</MenuItem>
                <MenuItem value="technician">{currentLanguage === 'ar' ? 'تقني' : 'Technician'}</MenuItem>
                <MenuItem value="administrator">{currentLanguage === 'ar' ? 'مدير' : 'Administrator'}</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={currentLanguage === 'ar' ? 'الاسم (إنجليزي)' : 'Name (English)'}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={currentLanguage === 'ar' ? 'الاسم (عربي)' : 'Name (Arabic)'}
                value={formData.name_ar}
                onChange={(e) => setFormData({ ...formData, name_ar: e.target.value })}
                InputProps={{ dir: 'rtl' }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={currentLanguage === 'ar' ? 'المؤسسة' : 'Organization'}
                value={formData.organization}
                onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={currentLanguage === 'ar' ? 'معرف نفيس' : 'NPHIES ID'}
                value={formData.nphies_id}
                onChange={(e) => setFormData({ ...formData, nphies_id: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>
            {currentLanguage === 'ar' ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSubmit}
            disabled={createMutation.isLoading}
          >
            {createMutation.isLoading 
              ? (currentLanguage === 'ar' ? 'جاري الحفظ...' : 'Saving...') 
              : (currentLanguage === 'ar' ? 'حفظ' : 'Save')
            }
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HealthcareIdentityManagement;