import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  FormControlLabel,
  Grid,
  IconButton,
  InputAdornment,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  Tab,
  Tabs,
  TextField,
  Typography
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';

import {
  AccountTree,
  Assessment,
  Assignment,
  CheckCircle,
  Dashboard,
  Engineering,
  Error,
  HealthAndSafety,
  Language,
  MonetizationOn,
  Notifications,
  People,
  Refresh,
  Schedule,
  School,
  Search,
  Security,
  Settings,
  SmartToy,
  TrendingUp,
  Warning
} from '@mui/icons-material';

import { useLanguage } from '../hooks/useLanguage';

const UnifiedWorkspace = () => {
  const { t, language, toggleLanguage, isRTL } = useLanguage();
  const [activeContext, setActiveContext] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [systemStatus, setSystemStatus] = useState('operational');
  
  // Unified State Management - Single source of truth
  const [unifiedData, setUnifiedData] = useState({
    overview: {
      totalClaims: 125847,
      accuracy: 96.8,
      revenue: 45200000,
      users: 1250,
      systemHealth: 'excellent'
    },
    nphies: {
      eligibilityChecks: 5420,
      claimsSubmitted: 12584,
      preAuthRequests: 892,
      successRate: 97.2,
      averageProcessingTime: '2.4 hours'
    },
    rcm: {
      firstPassRate: 96.2,
      denialRate: 1.8,
      collectionDays: 28,
      revenue: 15600000,
      pendingClaims: 235
    },
    training: {
      activeLearners: 1850,
      completedCertifications: 425,
      averageScore: 87.5,
      upcomingExams: 89
    },
    bot: {
      activeProjects: 3,
      completedPhases: 7,
      knowledgeTransfers: 12,
      clientSatisfaction: 94.2
    },
    operations: {
      riyadhStaff: 200,
      jeddahStaff: 150,
      dammamStaff: 100,
      activeShifts: 3,
      systemUptime: 99.97
    },
    aiAnalytics: {
      fraudDetected: 23,
      duplicatesFound: 156,
      arabicProcessed: 45670,
      accuracy: 94.8
    }
  });

  // Context Configuration - Unified module system
  const contextModules = useMemo(() => ({
    overview: {
      icon: Dashboard,
      title: isRTL ? 'لوحة التحكم الرئيسية' : 'Healthcare Overview',
      color: 'primary',
      description: isRTL ? 'نظرة شاملة على منصة الرعاية الصحية' : 'Comprehensive healthcare platform overview'
    },
    nphies: {
      icon: HealthAndSafety,
      title: isRTL ? 'منصة نفيس' : 'NPHIES Integration',
      color: 'success',
      description: isRTL ? 'تكامل منصة نفيس السعودية' : 'Saudi NPHIES platform integration'
    },
    rcm: {
      icon: MonetizationOn,
      title: isRTL ? 'إدارة دورة الإيرادات' : 'Revenue Cycle Management',
      color: 'info',
      description: isRTL ? 'إدارة شاملة لدورة الإيرادات الطبية' : 'Comprehensive medical revenue cycle management'
    },
    training: {
      icon: School,
      title: isRTL ? 'منصة التدريب' : 'Training Platform',
      color: 'warning',
      description: isRTL ? 'تدريب وتأهيل المتخصصين الطبيين' : 'Medical professionals training and certification'
    },
    bot: {
      icon: Engineering,
      title: isRTL ? 'إدارة مشاريع البوت' : 'BOT Projects',
      color: 'secondary',
      description: isRTL ? 'إدارة مشاريع البناء والتشغيل والنقل' : 'Build-Operate-Transfer project management'
    },
    operations: {
      icon: Assessment,
      title: isRTL ? 'مراكز العمليات' : 'Operations Centers',
      color: 'primary',
      description: isRTL ? 'مراكز العمليات على مدار الساعة' : '24/7 operations centers management'
    },
    aiAnalytics: {
      icon: SmartToy,
      title: isRTL ? 'التحليلات الذكية' : 'AI Analytics',
      color: 'info',
      description: isRTL ? 'التحليلات الذكية والذكاء الاصطناعي' : 'AI-powered analytics and insights'
    },
    oidTree: {
      icon: AccountTree,
      title: isRTL ? 'شجرة المعرفات' : 'OID Tree',
      color: 'default',
      description: isRTL ? 'إدارة معرفات الكائنات الطبية' : 'Healthcare object identifier management'
    }
  }), [isRTL]);

  // Unified search across all contexts
  const handleSearch = (query) => {
    setSearchQuery(query);
    // Implementation would search across all healthcare entities
  };

  // Context switching handler
  const handleContextChange = (event, newContext) => {
    setActiveContext(newContext);
  };

  // Real-time data updates (simulated)
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulated real-time updates
      setUnifiedData(prev => ({
        ...prev,
        overview: {
          ...prev.overview,
          totalClaims: prev.overview.totalClaims + Math.floor(Math.random() * 5)
        }
      }));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Unified Status Indicators
  const StatusIndicator = ({ status, label }) => (
    <Box display="flex" alignItems="center" gap={1}>
      {status === 'excellent' && <CheckCircle color="success" />}
      {status === 'good' && <TrendingUp color="info" />}
      {status === 'warning' && <Warning color="warning" />}
      {status === 'error' && <Error color="error" />}
      <Typography variant="body2">{label}</Typography>
    </Box>
  );

  // Unified Metric Card Component
  const MetricCard = ({ title, value, subtitle, trend, color = 'primary' }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h4" color={`${color}.main`} fontWeight="bold">
          {value}
        </Typography>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
        {trend && (
          <Box display="flex" alignItems="center" mt={1}>
            <TrendingUp color="success" fontSize="small" />
            <Typography variant="caption" color="success.main" ml={0.5}>
              {trend}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  // Context-specific content renderer
  const renderContextContent = () => {
    switch (activeContext) {
      case 'overview':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "إجمالي المطالبات" : "Total Claims"}
                value={unifiedData.overview.totalClaims.toLocaleString()}
                subtitle={isRTL ? "المطالبات المعالجة" : "Claims processed"}
                trend="+5.2%"
                color="primary"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "معدل الدقة" : "Accuracy Rate"}
                value={`${unifiedData.overview.accuracy}%`}
                subtitle={isRTL ? "دقة معالجة المطالبات" : "Claims processing accuracy"}
                trend="+1.1%"
                color="success"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "الإيرادات (ريال)" : "Revenue (SAR)"}
                value={`${(unifiedData.overview.revenue / 1000000).toFixed(1)}M`}
                subtitle={isRTL ? "إجمالي الإيرادات المحققة" : "Total revenue generated"}
                trend="+12.3%"
                color="info"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "المستخدمين النشطين" : "Active Users"}
                value={unifiedData.overview.users.toLocaleString()}
                subtitle={isRTL ? "المتخصصين المدربين" : "Trained professionals"}
                trend="+8.7%"
                color="warning"
              />
            </Grid>
          </Grid>
        );

      case 'nphies':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "فحوصات الأهلية" : "Eligibility Checks"}
                value={unifiedData.nphies.eligibilityChecks.toLocaleString()}
                subtitle={isRTL ? "فحوصات اليوم" : "Today's checks"}
                color="success"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "المطالبات المرسلة" : "Claims Submitted"}
                value={unifiedData.nphies.claimsSubmitted.toLocaleString()}
                subtitle={isRTL ? "هذا الشهر" : "This month"}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "معدل النجاح" : "Success Rate"}
                value={`${unifiedData.nphies.successRate}%`}
                subtitle={isRTL ? "معدل قبول المطالبات" : "Claims acceptance rate"}
                color="info"
              />
            </Grid>
          </Grid>
        );

      case 'rcm':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "معدل المرور الأول" : "First Pass Rate"}
                value={`${unifiedData.rcm.firstPassRate}%`}
                subtitle={isRTL ? "هدف: 95%+" : "Target: 95%+"}
                color="success"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "معدل الرفض" : "Denial Rate"}
                value={`${unifiedData.rcm.denialRate}%`}
                subtitle={isRTL ? "هدف: <2%" : "Target: <2%"}
                color="error"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "أيام التحصيل" : "Collection Days"}
                value={unifiedData.rcm.collectionDays}
                subtitle={isRTL ? "هدف: <30 يوم" : "Target: <30 days"}
                color="warning"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "الإيرادات الشهرية" : "Monthly Revenue"}
                value={`${(unifiedData.rcm.revenue / 1000000).toFixed(1)}M`}
                subtitle={isRTL ? "ريال سعودي" : "SAR"}
                color="primary"
              />
            </Grid>
          </Grid>
        );

      case 'training':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "المتدربين النشطين" : "Active Learners"}
                value={unifiedData.training.activeLearners.toLocaleString()}
                subtitle={isRTL ? "في برامج التدريب" : "In training programs"}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "الشهادات المكتملة" : "Certifications Completed"}
                value={unifiedData.training.completedCertifications}
                subtitle={isRTL ? "هذا الشهر" : "This month"}
                color="success"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "متوسط النتائج" : "Average Score"}
                value={`${unifiedData.training.averageScore}%`}
                subtitle={isRTL ? "هدف: 85%+" : "Target: 85%+"}
                color="info"
              />
            </Grid>
          </Grid>
        );

      case 'bot':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "المشاريع النشطة" : "Active Projects"}
                value={unifiedData.bot.activeProjects}
                subtitle={isRTL ? "مشاريع البوت الجارية" : "Ongoing BOT projects"}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "المراحل المكتملة" : "Completed Phases"}
                value={unifiedData.bot.completedPhases}
                subtitle={isRTL ? "عبر جميع المشاريع" : "Across all projects"}
                color="success"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <MetricCard
                title={isRTL ? "رضا العملاء" : "Client Satisfaction"}
                value={`${unifiedData.bot.clientSatisfaction}%`}
                subtitle={isRTL ? "هدف: 90%+" : "Target: 90%+"}
                color="info"
              />
            </Grid>
          </Grid>
        );

      case 'operations':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {isRTL ? "مركز الرياض" : "Riyadh Center"}
                  </Typography>
                  <Typography variant="h4" color="primary.main" fontWeight="bold">
                    {unifiedData.operations.riyadhStaff}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {isRTL ? "موظف نشط" : "Active staff"}
                  </Typography>
                  <StatusIndicator status="excellent" label={isRTL ? "تشغيل ممتاز" : "Excellent"} />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {isRTL ? "مركز جدة" : "Jeddah Center"}
                  </Typography>
                  <Typography variant="h4" color="success.main" fontWeight="bold">
                    {unifiedData.operations.jeddahStaff}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {isRTL ? "موظف نشط" : "Active staff"}
                  </Typography>
                  <StatusIndicator status="good" label={isRTL ? "تشغيل جيد" : "Good"} />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {isRTL ? "مركز الدمام" : "Dammam Center"}
                  </Typography>
                  <Typography variant="h4" color="info.main" fontWeight="bold">
                    {unifiedData.operations.dammamStaff}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {isRTL ? "موظف نشط" : "Active staff"}
                  </Typography>
                  <StatusIndicator status="good" label={isRTL ? "تشغيل جيد" : "Good"} />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      case 'aiAnalytics':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "احتيال مكتشف" : "Fraud Detected"}
                value={unifiedData.aiAnalytics.fraudDetected}
                subtitle={isRTL ? "هذا الشهر" : "This month"}
                color="error"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "تكرارات محذوفة" : "Duplicates Removed"}
                value={unifiedData.aiAnalytics.duplicatesFound}
                subtitle={isRTL ? "تحسين الجودة" : "Quality improvement"}
                color="warning"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "نصوص عربية معالجة" : "Arabic Texts Processed"}
                value={unifiedData.aiAnalytics.arabicProcessed.toLocaleString()}
                subtitle={isRTL ? "معالجة اللغة الطبيعية" : "NLP processing"}
                color="info"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <MetricCard
                title={isRTL ? "دقة الذكاء الاصطناعي" : "AI Accuracy"}
                value={`${unifiedData.aiAnalytics.accuracy}%`}
                subtitle={isRTL ? "هدف: 95%+" : "Target: 95%+"}
                color="success"
              />
            </Grid>
          </Grid>
        );

      case 'oidTree':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      {isRTL ? "إدارة شجرة المعرفات الطبية" : "Healthcare OID Tree Management"}
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<AccountTree />}
                      href="/oid-tree"
                      sx={{ textDecoration: 'none' }}
                    >
                      {isRTL ? "عرض الشجرة الكاملة" : "View Full Tree"}
                    </Button>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {isRTL 
                      ? "نظام إدارة معرفات الكائنات الطبية المتكامل مع جميع خدمات المنصة الصحية الموحدة"
                      : "Integrated healthcare object identifier management system connected to all unified platform services"
                    }
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <MetricCard
                        title={isRTL ? "العقد المسجلة" : "Registered Nodes"}
                        value="156"
                        subtitle={isRTL ? "معرفات طبية نشطة" : "Active healthcare identifiers"}
                        color="primary"
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <MetricCard
                        title={isRTL ? "خدمات متكاملة" : "Integrated Services"}
                        value="8"
                        subtitle={isRTL ? "وحدات المنصة الموحدة" : "Unified platform modules"}
                        color="success"
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <MetricCard
                        title={isRTL ? "مستوى التكامل" : "Integration Level"}
                        value="100%"
                        subtitle={isRTL ? "تكامل كامل مع الخدمات" : "Full service integration"}
                        color="info"
                      />
                    </Grid>
                  </Grid>
                  
                  <Box mt={3}>
                    <Typography variant="subtitle1" gutterBottom>
                      {isRTL ? "الخدمات المتكاملة مع شجرة المعرفات" : "OID-Integrated Services"}
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon><HealthAndSafety color="success" /></ListItemIcon>
                        <ListItemText 
                          primary={isRTL ? "تكامل منصة نفيس" : "NPHIES Integration"} 
                          secondary="1.3.6.1.4.1.61026.2.1"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><MonetizationOn color="info" /></ListItemIcon>
                        <ListItemText 
                          primary={isRTL ? "إدارة دورة الإيرادات" : "Revenue Cycle Management"} 
                          secondary="1.3.6.1.4.1.61026.2.5"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><School color="warning" /></ListItemIcon>
                        <ListItemText 
                          primary={isRTL ? "منصة التدريب" : "Training Platform"} 
                          secondary="1.3.6.1.4.1.61026.3"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><Engineering color="secondary" /></ListItemIcon>
                        <ListItemText 
                          primary={isRTL ? "مشاريع البوت" : "BOT Projects"} 
                          secondary="1.3.6.1.4.1.61026.4"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><Assessment color="primary" /></ListItemIcon>
                        <ListItemText 
                          primary={isRTL ? "مراكز العمليات" : "Operations Centers"} 
                          secondary="1.3.6.1.4.1.61026.5"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><SmartToy color="info" /></ListItemIcon>
                        <ListItemText 
                          primary={isRTL ? "التحليلات الذكية" : "AI Analytics"} 
                          secondary="1.3.6.1.4.1.61026.2.6"
                        />
                      </ListItem>
                    </List>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      default:
        return (
          <Alert severity="info">
            {isRTL ? "السياق المحدد غير متوفر" : "Selected context not available"}
          </Alert>
        );
    }
  };

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        {/* Unified Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Box>
            <Typography variant="h4" component="h1" fontWeight="bold">
              {isRTL ? "منصة الرعاية الصحية الموحدة" : "BrainSAIT Healthcare Unification Platform"}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {isRTL ? "نظام موحد لإدارة الرعاية الصحية السعودية" : "Unified Saudi Healthcare Management System"}
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center" gap={2}>
            <FormControlLabel
              control={<Switch checked={isRTL} onChange={toggleLanguage} />}
              label={<Language />}
            />
            <IconButton>
              <Notifications />
            </IconButton>
            <IconButton>
              <Settings />
            </IconButton>
          </Box>
        </Box>

        {/* Unified Search Bar */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <TextField
              fullWidth
              placeholder={isRTL ? "البحث في جميع وحدات الرعاية الصحية..." : "Search across all healthcare modules..."}
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </CardContent>
        </Card>

        {/* Unified Context Navigation */}
        <Card sx={{ mb: 3 }}>
          <Tabs
            value={activeContext}
            onChange={handleContextChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ px: 2 }}
          >
            {Object.entries(contextModules).map(([key, module]) => {
              const IconComponent = module.icon;
              return (
                <Tab
                  key={key}
                  value={key}
                  icon={<IconComponent />}
                  label={module.title}
                  sx={{ minHeight: 72 }}
                />
              );
            })}
          </Tabs>
        </Card>

        {/* System Status Bar */}
        <Alert 
          severity={systemStatus === 'operational' ? 'success' : 'warning'} 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" startIcon={<Refresh />}>
              {isRTL ? "تحديث" : "Refresh"}
            </Button>
          }
        >
          {isRTL ? "جميع الأنظمة تعمل بشكل طبيعي - وقت التشغيل: 99.97%" : "All systems operational - Uptime: 99.97%"}
        </Alert>

        {/* Context-Specific Content */}
        <Box>
          {renderContextContent()}
        </Box>

        {/* Enhanced Real-time Collaboration Features */}
        <Box mt={4}>
          <Typography variant="h5" gutterBottom>
            {isRTL ? "التعاون المباشر بين الفرق" : "Real-time Team Collaboration"}
          </Typography>
          <Grid container spacing={3}>
            {/* Cross-role Communication Panel */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {isRTL ? "التواصل بين الأدوار" : "Cross-Role Communication"}
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon><People color="primary" /></ListItemIcon>
                      <ListItemText 
                        primary={isRTL ? "طبيب → ممرض: تحديث العلامات الحيوية" : "Doctor → Nurse: Update vitals"}
                        secondary={isRTL ? "منذ 5 دقائق" : "5 minutes ago"}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><Assignment color="success" /></ListItemIcon>
                      <ListItemText 
                        primary={isRTL ? "ممرض → صيدلي: طلب دواء جديد" : "Nurse → Pharmacist: New medication request"}
                        secondary={isRTL ? "منذ 12 دقيقة" : "12 minutes ago"}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><MonetizationOn color="warning" /></ListItemIcon>
                      <ListItemText 
                        primary={isRTL ? "RCM → مالية: مراجعة مطالبة" : "RCM → Finance: Claim review"}
                        secondary={isRTL ? "منذ 18 دقيقة" : "18 minutes ago"}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Unified Task Queue */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {isRTL ? "قائمة المهام الموحدة" : "Unified Task Queue"}
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText 
                        primary={isRTL ? "تم إكمال فحص الأهلية - نفيس" : "Eligibility Check Completed - NPHIES"}
                        secondary={isRTL ? "المريض: أحمد محمد" : "Patient: Ahmed Mohammed"}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><Schedule color="warning" /></ListItemIcon>
                      <ListItemText 
                        primary={isRTL ? "في انتظار اعتماد المطالبة" : "Claim Approval Pending"}
                        secondary={isRTL ? "المبلغ: 1,250 ريال" : "Amount: 1,250 SAR"}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><School color="info" /></ListItemIcon>
                      <ListItemText 
                        primary={isRTL ? "تدريب جديد متاح: ترميز NPHIES" : "New Training: NPHIES Coding"}
                        secondary={isRTL ? "المدة: 16 ساعة" : "Duration: 16 hours"}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Voice-Enabled Quick Actions */}
            <Grid item xs={12} md={4}>
              <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {isRTL ? "الأوامر الصوتية السريعة" : "Voice Quick Actions"}
                  </Typography>
                  <Box display="flex" flexDirection="column" gap={1}>
                    <Button variant="outlined" sx={{ color: 'white', borderColor: 'white' }} startIcon={<Assignment />}>
                      {isRTL ? "ابدأ ملاحظة SOAP" : "Start SOAP Note"}
                    </Button>
                    <Button variant="outlined" sx={{ color: 'white', borderColor: 'white' }} startIcon={<HealthAndSafety />}>
                      {isRTL ? "سجل العلامات الحيوية" : "Record Vitals"}
                    </Button>
                    <Button variant="outlined" sx={{ color: 'white', borderColor: 'white' }} startIcon={<Assignment />}>
                      {isRTL ? "أنشئ مهمة جديدة" : "Create New Task"}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* AI-Powered Insights */}
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {isRTL ? "رؤى الذكاء الاصطناعي" : "AI-Powered Insights"}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Alert severity="warning" icon={<SmartToy />}>
                        <Typography variant="body2">
                          {isRTL 
                            ? "تم اكتشاف 3 مطالبات مشبوهة تحتاج مراجعة"
                            : "3 suspicious claims detected requiring review"
                          }
                        </Typography>
                      </Alert>
                    </Grid>
                    <Grid item xs={6}>
                      <Alert severity="info" icon={<TrendingUp />}>
                        <Typography variant="body2">
                          {isRTL 
                            ? "توقع زيادة 15% في المطالبات الشهر القادم"
                            : "15% increase in claims predicted next month"
                          }
                        </Typography>
                      </Alert>
                    </Grid>
                    <Grid item xs={6}>
                      <Alert severity="success" icon={<Assessment />}>
                        <Typography variant="body2">
                          {isRTL 
                            ? "تحسن دقة الترميز إلى 96.8%"
                            : "Coding accuracy improved to 96.8%"
                          }
                        </Typography>
                      </Alert>
                    </Grid>
                    <Grid item xs={6}>
                      <Alert severity="error" icon={<Security />}>
                        <Typography variant="body2">
                          {isRTL 
                            ? "تم اكتشاف 2 محاولة وصول مشبوهة"
                            : "2 suspicious access attempts detected"
                          }
                        </Typography>
                      </Alert>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Enhanced Integration Status */}
        <Box mt={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {isRTL ? "حالة التكامل مع الأنظمة الخارجية" : "External Systems Integration Status"}
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center" p={2}>
                    <HealthAndSafety sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
                    <Typography variant="h6">{isRTL ? "نفيس" : "NPHIES"}</Typography>
                    <Chip label={isRTL ? "متصل" : "Connected"} color="success" size="small" />
                    <Typography variant="caption" display="block" mt={1}>
                      {isRTL ? "آخر مزامنة: منذ 2 دقيقة" : "Last sync: 2 min ago"}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center" p={2}>
                    <MonetizationOn sx={{ fontSize: 48, color: 'info.main', mb: 1 }} />
                    <Typography variant="h6">{isRTL ? "البنوك السعودية" : "Saudi Banks"}</Typography>
                    <Chip label={isRTL ? "متصل" : "Connected"} color="success" size="small" />
                    <Typography variant="caption" display="block" mt={1}>
                      {isRTL ? "الدفعات: 99.8% نجاح" : "Payments: 99.8% success"}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center" p={2}>
                    <School sx={{ fontSize: 48, color: 'warning.main', mb: 1 }} />
                    <Typography variant="h6">{isRTL ? "منصة التعلم" : "Learning Platform"}</Typography>
                    <Chip label={isRTL ? "نشط" : "Active"} color="success" size="small" />
                    <Typography variant="caption" display="block" mt={1}>
                      {isRTL ? "1,850 متدرب نشط" : "1,850 active learners"}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center" p={2}>
                    <Assessment sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h6">{isRTL ? "مراكز العمليات" : "Operations Centers"}</Typography>
                    <Chip label={isRTL ? "3 مراكز نشطة" : "3 Centers Active"} color="success" size="small" />
                    <Typography variant="caption" display="block" mt={1}>
                      {isRTL ? "450 موظف متاح" : "450 staff available"}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>

        {/* Unified Footer Information */}
        <Box mt={6} pt={3} borderTop={1} borderColor="divider">
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                {isRTL ? "الوضع الحالي" : "Current Status"}
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                  <ListItemText primary={isRTL ? "نفيس متصل" : "NPHIES Connected"} />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                  <ListItemText primary={isRTL ? "قاعدة البيانات نشطة" : "Database Active"} />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                  <ListItemText primary={isRTL ? "مراكز العمليات متاحة" : "Operations Centers Online"} />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                {isRTL ? "الأداء المباشر" : "Live Performance"}
              </Typography>
              <Box mb={2}>
                <Typography variant="body2">{isRTL ? "معدل معالجة المطالبات" : "Claims Processing Rate"}</Typography>
                <LinearProgress variant="determinate" value={96.8} sx={{ mt: 1, height: 8 }} />
                <Typography variant="caption">96.8%</Typography>
              </Box>
              <Box mb={2}>
                <Typography variant="body2">{isRTL ? "رضا المستخدمين" : "User Satisfaction"}</Typography>
                <LinearProgress variant="determinate" value={94.2} color="success" sx={{ mt: 1, height: 8 }} />
                <Typography variant="caption">94.2%</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                {isRTL ? "الوصول السريع" : "Quick Actions"}
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Button variant="outlined" size="small" startIcon={<Assignment />}>
                  {isRTL ? "تقرير جديد" : "New Report"}
                </Button>
                <Button variant="outlined" size="small" startIcon={<People />}>
                  {isRTL ? "إدارة المستخدمين" : "Manage Users"}
                </Button>
                <Button variant="outlined" size="small" startIcon={<Settings />}>
                  {isRTL ? "إعدادات النظام" : "System Settings"}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  );
};

export default UnifiedWorkspace;