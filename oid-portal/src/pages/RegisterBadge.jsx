import {
    Assignment,
    Business,
    Cancel,
    LocalHospital,
    Person,
    Save,
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    TextField,
    Typography,
} from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../hooks/useLanguage';

const RegisterBadge = () => {
  const { isRTL } = useLanguage();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    nameAr: '',
    type: '',
    organization: '',
    department: '',
    nationalId: '',
    accessLevel: '',
    description: '',
  });
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  const entityTypes = [
    { value: 'provider', label: isRTL ? 'مقدم خدمة' : 'Provider', icon: <LocalHospital /> },
    { value: 'organization', label: isRTL ? 'مؤسسة' : 'Organization', icon: <Business /> },
    { value: 'person', label: isRTL ? 'شخص' : 'Person', icon: <Person /> },
    { value: 'system', label: isRTL ? 'نظام' : 'System', icon: <Assignment /> },
  ];

  const accessLevels = [
    { value: 'low', label: isRTL ? 'منخفض' : 'Low' },
    { value: 'medium', label: isRTL ? 'متوسط' : 'Medium' },
    { value: 'high', label: isRTL ? 'عالي' : 'High' },
    { value: 'critical', label: isRTL ? 'حرج' : 'Critical' },
  ];

  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value
    });
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors({
        ...errors,
        [field]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = isRTL ? 'الاسم مطلوب' : 'Name is required';
    }
    
    if (!formData.type) {
      newErrors.type = isRTL ? 'نوع الكيان مطلوب' : 'Entity type is required';
    }
    
    if (!formData.organization.trim()) {
      newErrors.organization = isRTL ? 'المؤسسة مطلوبة' : 'Organization is required';
    }
    
    if (!formData.accessLevel) {
      newErrors.accessLevel = isRTL ? 'مستوى الوصول مطلوب' : 'Access level is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    
    if (validateForm()) {
      // Simulate API call
      setTimeout(() => {
        setSuccess(true);
        setTimeout(() => {
          navigate('/oid-tree');
        }, 2000);
      }, 1000);
    }
  };

  const handleCancel = () => {
    navigate(-1);
  };

  if (success) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <Alert severity="success" sx={{ maxWidth: 400 }}>
          <Typography variant="h6" gutterBottom>
            {isRTL ? 'تم التسجيل بنجاح!' : 'Registration Successful!'}
          </Typography>
          <Typography variant="body2">
            {isRTL ? 'سيتم توجيهك إلى شجرة المعرفات...' : 'Redirecting to OID tree...'}
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {isRTL ? 'تسجيل معرف جديد' : 'Register New Identity'}
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={4}>
        {isRTL ? 'إنشاء معرف جديد في النظام الصحي الموحد' : 'Create a new identifier in the unified healthcare system'}
      </Typography>

      <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assignment />
                {isRTL ? 'المعلومات الأساسية' : 'Basic Information'}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={isRTL ? 'الاسم (إنجليزي)' : 'Name (English)'}
                value={formData.name}
                onChange={handleChange('name')}
                error={!!errors.name}
                helperText={errors.name}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={isRTL ? 'الاسم (عربي)' : 'Name (Arabic)'}
                value={formData.nameAr}
                onChange={handleChange('nameAr')}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!errors.type} required>
                <InputLabel>{isRTL ? 'نوع الكيان' : 'Entity Type'}</InputLabel>
                <Select
                  value={formData.type}
                  onChange={handleChange('type')}
                  label={isRTL ? 'نوع الكيان' : 'Entity Type'}
                >
                  {entityTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Box display="flex" alignItems="center" gap={1}>
                        {type.icon}
                        {type.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!errors.accessLevel} required>
                <InputLabel>{isRTL ? 'مستوى الوصول' : 'Access Level'}</InputLabel>
                <Select
                  value={formData.accessLevel}
                  onChange={handleChange('accessLevel')}
                  label={isRTL ? 'مستوى الوصول' : 'Access Level'}
                >
                  {accessLevels.map((level) => (
                    <MenuItem key={level.value} value={level.value}>
                      {level.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Organization Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                <Business />
                {isRTL ? 'معلومات المؤسسة' : 'Organization Information'}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={isRTL ? 'المؤسسة' : 'Organization'}
                value={formData.organization}
                onChange={handleChange('organization')}
                error={!!errors.organization}
                helperText={errors.organization}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={isRTL ? 'القسم' : 'Department'}
                value={formData.department}
                onChange={handleChange('department')}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={isRTL ? 'رقم الهوية الوطنية' : 'National ID'}
                value={formData.nationalId}
                onChange={handleChange('nationalId')}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label={isRTL ? 'الوصف' : 'Description'}
                value={formData.description}
                onChange={handleChange('description')}
                multiline
                rows={4}
                helperText={isRTL ? 'وصف مفصل للكيان ودوره في النظام' : 'Detailed description of the entity and its role in the system'}
              />
            </Grid>

            {/* Preview */}
            {formData.name && formData.type && (
              <Grid item xs={12}>
                <Card sx={{ bgcolor: 'primary.main', color: 'primary.contrastText' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {isRTL ? 'معاينة المعرف' : 'Identity Preview'}
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      <Chip label={`${isRTL ? 'الاسم:' : 'Name:'} ${formData.name}`} />
                      <Chip label={`${isRTL ? 'النوع:' : 'Type:'} ${formData.type}`} />
                      <Chip label={`${isRTL ? 'المؤسسة:' : 'Org:'} ${formData.organization}`} />
                      {formData.accessLevel && (
                        <Chip label={`${isRTL ? 'المستوى:' : 'Level:'} ${formData.accessLevel}`} />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Actions */}
            <Grid item xs={12}>
              <Box display="flex" gap={2} justifyContent="flex-end" mt={2}>
                <Button
                  variant="outlined"
                  startIcon={<Cancel />}
                  onClick={handleCancel}
                >
                  {isRTL ? 'إلغاء' : 'Cancel'}
                </Button>
                <Button
                  variant="contained"
                  type="submit"
                  startIcon={<Save />}
                >
                  {isRTL ? 'تسجيل' : 'Register'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
};

export default RegisterBadge;
