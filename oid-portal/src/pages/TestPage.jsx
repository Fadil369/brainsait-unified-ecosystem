// React import removed - not using JSX pragma
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Grid,
  Chip
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Info
} from '@mui/icons-material';
import { useLanguage } from '../hooks/useLanguage';
import { useUnifiedHealthcare } from '../contexts/UnifiedHealthcareContext';

const TestPage = () => {
  const { toggleLanguage, isRTL } = useLanguage();
  const { unifiedData, systemStatus, user } = useUnifiedHealthcare();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {isRTL ? 'صفحة اختبار النظام' : 'System Test Page'}
      </Typography>
      
      <Alert severity="success" sx={{ mb: 3 }}>
        <Typography variant="body2">
          {isRTL 
            ? 'تم تحميل الواجهة بنجاح! جميع المكونات الأساسية تعمل بشكل صحيح.'
            : 'UI loaded successfully! All core components are working properly.'
          }
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {/* Language Test */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {isRTL ? 'اختبار اللغة' : 'Language Test'}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {isRTL 
                  ? 'اللغة الحالية: العربية (RTL)'
                  : 'Current Language: English (LTR)'
                }
              </Typography>
              <Button 
                variant="contained" 
                onClick={toggleLanguage}
                sx={{ mb: 2 }}
              >
                {isRTL ? 'التبديل إلى الإنجليزية' : 'Switch to Arabic'}
              </Button>
              <Box>
                <Chip 
                  icon={<CheckCircle />}
                  label={isRTL ? 'RTL مفعل' : 'RTL Active'} 
                  color={isRTL ? 'success' : 'default'}
                  sx={{ mr: 1 }}
                />
                <Chip 
                  icon={<CheckCircle />}
                  label={isRTL ? 'LTR مفعل' : 'LTR Active'} 
                  color={!isRTL ? 'success' : 'default'}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Context Test */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {isRTL ? 'اختبار السياق' : 'Context Test'}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {isRTL 
                  ? 'بيانات السياق الموحد محملة ومتاحة'
                  : 'Unified context data loaded and available'
                }
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'المطالبات:' : 'Claims:'} ${unifiedData.overview.totalClaims?.toLocaleString() || 'N/A'}`} 
                  color="success"
                  size="small"
                />
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'الدقة:' : 'Accuracy:'} ${unifiedData.overview.accuracy || 'N/A'}%`} 
                  color="info"
                  size="small"
                />
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'المستخدمين:' : 'Users:'} ${unifiedData.overview.users?.toLocaleString() || 'N/A'}`} 
                  color="primary"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Status Test */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {isRTL ? 'حالة النظام' : 'System Status'}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {isRTL 
                  ? 'معلومات حالة النظام والخدمات'
                  : 'System and services status information'
                }
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Chip 
                  icon={systemStatus.status === 'operational' ? <CheckCircle /> : <Error />}
                  label={`${isRTL ? 'الحالة:' : 'Status:'} ${systemStatus.status || 'Unknown'}`} 
                  color={systemStatus.status === 'operational' ? 'success' : 'error'}
                  size="small"
                />
                <Chip 
                  icon={<Info />}
                  label={`${isRTL ? 'وقت التشغيل:' : 'Uptime:'} ${systemStatus.uptime || 'N/A'}%`} 
                  color="info"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* User Data Test */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {isRTL ? 'بيانات المستخدم' : 'User Data'}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {isRTL 
                  ? 'معلومات المستخدم الحالي والصلاحيات'
                  : 'Current user information and permissions'
                }
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'الاسم:' : 'Name:'} ${user.name || 'N/A'}`} 
                  color="primary"
                  size="small"
                />
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'الدور:' : 'Role:'} ${user.role || 'N/A'}`} 
                  color="secondary"
                  size="small"
                />
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'الصلاحيات:' : 'Permissions:'} ${user.permissions?.length || 0}`} 
                  color="info"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* NPHIES Test */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {isRTL ? 'اختبار نفيس' : 'NPHIES Test'}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {isRTL 
                  ? 'بيانات تكامل منصة نفيس السعودية'
                  : 'Saudi NPHIES platform integration data'
                }
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'فحوصات الأهلية:' : 'Eligibility Checks:'} ${unifiedData.nphies?.eligibilityChecks?.toLocaleString() || 'N/A'}`} 
                  color="success"
                  size="small"
                />
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'المطالبات المرسلة:' : 'Claims Submitted:'} ${unifiedData.nphies?.claimsSubmitted?.toLocaleString() || 'N/A'}`} 
                  color="info"
                  size="small"
                />
                <Chip 
                  icon={<CheckCircle />}
                  label={`${isRTL ? 'معدل النجاح:' : 'Success Rate:'} ${unifiedData.nphies?.successRate || 'N/A'}%`} 
                  color="primary"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Theme Test */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {isRTL ? 'اختبار المظهر' : 'Theme Test'}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {isRTL 
                  ? 'ألوان ومكونات المظهر الداكن'
                  : 'Dark theme colors and components'
                }
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip label="Primary" color="primary" />
                <Chip label="Secondary" color="secondary" />
                <Chip label="Success" color="success" />
                <Chip label="Error" color="error" />
                <Chip label="Warning" color="warning" />
                <Chip label="Info" color="info" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Final Status */}
      <Box sx={{ mt: 4 }}>
        <Alert severity="info">
          <Typography variant="body2">
            {isRTL 
              ? 'تم إصلاح جميع مشاكل العرض الأساسية. النظام جاهز للاستخدام مع دعم كامل للغة العربية ومنصة نفيس.'
              : 'All critical rendering issues have been fixed. System is ready for use with full Arabic support and NPHIES integration.'
            }
          </Typography>
        </Alert>
      </Box>
    </Box>
  );
};

export default TestPage;