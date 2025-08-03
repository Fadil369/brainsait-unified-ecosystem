/**
 * AI Testing Component - PyBrain AI Integration Verification
 * 
 * This component provides comprehensive testing and verification of PyBrain AI integration
 * including Arabic NLP, healthcare analytics, and intelligent automation features.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Chip,
  Alert,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Psychology as AIIcon,
  Language as LanguageIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
  Assessment as AnalyticsIcon
} from '@mui/icons-material';
import { useUnifiedPyBrain } from '../hooks/useUnifiedPyBrain';
import { useLanguage } from '../hooks/useLanguage';

const AITestingComponent = () => {
  const { currentLanguage, isRTL } = useLanguage();
  const {
    isAIReady,
    isProcessing,
    _getAIInsights,
    analyzeHealthcareData,
    processArabicText,
    _analyzeClaims,
    detectFraud,
    getFormAssistance,
    _validateInput,
    _getRevenueRecommendations,
    getMedicalCodingAssistance,
    getPredictiveAnalytics,
    getAIPerformanceMetrics,
    AI_MODELS
  } = useUnifiedPyBrain({
    enabled: true,
    context: 'ai_testing',
    culturalContext: 'SAUDI_ARABIA',
    enableCaching: true,
    enablePerformanceMonitoring: true
  });

  const [testResults, setTestResults] = useState({});
  const [currentTest, setCurrentTest] = useState(null);
  const [testLog, setTestLog] = useState([]);
  const [arabicTestText, setArabicTestText] = useState('المريض يشكو من صداع شديد وحمى منذ يومين');
  const [performanceMetrics, setPerformanceMetrics] = useState(null);

  // Test scenarios
  const testScenarios = [
    {
      id: 'arabic_nlp',
      name: currentLanguage === 'ar' ? 'معالجة النصوص العربية الطبية' : 'Arabic Medical NLP',
      description: currentLanguage === 'ar' 
        ? 'اختبار معالجة النصوص الطبية باللغة العربية وتحليل السياق الثقافي'
        : 'Test Arabic medical text processing and cultural context analysis',
      category: 'language'
    },
    {
      id: 'healthcare_analysis',
      name: currentLanguage === 'ar' ? 'تحليل البيانات الصحية' : 'Healthcare Data Analysis',
      description: currentLanguage === 'ar'
        ? 'تحليل البيانات الطبية واستخراج الرؤى الذكية'
        : 'Analyze medical data and extract intelligent insights',
      category: 'healthcare'
    },
    {
      id: 'claims_fraud_detection',
      name: currentLanguage === 'ar' ? 'كشف الاحتيال في المطالبات' : 'Claims Fraud Detection',
      description: currentLanguage === 'ar'
        ? 'اكتشاف المطالبات المشبوهة والاحتيال المحتمل'
        : 'Detect suspicious claims and potential fraud',
      category: 'security'
    },
    {
      id: 'predictive_analytics',
      name: currentLanguage === 'ar' ? 'التحليلات التنبؤية' : 'Predictive Analytics',
      description: currentLanguage === 'ar'
        ? 'تنبؤات ذكية لنتائج المرضى والموارد'
        : 'Intelligent predictions for patient outcomes and resources',
      category: 'analytics'
    },
    {
      id: 'form_assistance',
      name: currentLanguage === 'ar' ? 'مساعد النماذج الذكي' : 'Intelligent Form Assistant',
      description: currentLanguage === 'ar'
        ? 'مساعدة ذكية في ملء النماذج والتحقق من البيانات'
        : 'Smart assistance in form filling and data validation',
      category: 'automation'
    },
    {
      id: 'medical_coding',
      name: currentLanguage === 'ar' ? 'مساعد الترميز الطبي' : 'Medical Coding Assistant',
      description: currentLanguage === 'ar'
        ? 'مساعدة في الترميز الطبي ICD-10 و SNOMED CT'
        : 'Assistance with ICD-10 and SNOMED CT medical coding',
      category: 'healthcare'
    }
  ];

  // Add test log entry
  const addLogEntry = (message, type = 'info', data = null) => {
    const timestamp = new Date().toLocaleTimeString();
    setTestLog(prev => [{
      timestamp,
      message,
      type,
      data,
      id: Date.now()
    }, ...prev.slice(0, 49)]); // Keep last 50 entries
  };

  // Run individual test
  const runTest = async (testId) => {
    if (!isAIReady) {
      addLogEntry('AI service not ready', 'error');
      return;
    }

    setCurrentTest(testId);
    addLogEntry(`Starting test: ${testId}`, 'info');
    
    try {
      let result = null;
      
      switch (testId) {
        case 'arabic_nlp':
          result = await processArabicText(arabicTestText, 'medical_analysis');
          break;
          
        case 'healthcare_analysis':
          result = await analyzeHealthcareData({
            patient_id: 'test_001',
            vitals: { temperature: 38.5, blood_pressure: '140/90', heart_rate: 85 },
            symptoms: ['headache', 'fever', 'fatigue'],
            medical_history: ['diabetes', 'hypertension']
          }, 'comprehensive');
          break;
          
        case 'claims_fraud_detection':
          result = await detectFraud({
            claim_id: 'CLM_001',
            amount: 25000,
            provider_id: 'PRV_123',
            services: ['consultation', 'lab_tests', 'medication'],
            patient_history: { previous_claims: 3, total_amount: 45000 }
          });
          break;
          
        case 'predictive_analytics':
          result = await getPredictiveAnalytics(
            {
              patient_demographics: { age: 45, gender: 'male' },
              medical_history: ['diabetes'],
              current_treatment: 'medication_management'
            },
            'patient_outcome',
            '30d'
          );
          break;
          
        case 'form_assistance':
          result = await getFormAssistance('patient_registration', {
            name: 'أحمد محمد',
            age: 35,
            symptoms: 'صداع'
          }, { language: 'ar', cultural_context: 'saudi' });
          break;
          
        case 'medical_coding':
          result = await getMedicalCodingAssistance({
            diagnosis: 'صداع مزمن مع حمى',
            symptoms: ['headache', 'fever'],
            procedures: ['consultation', 'examination']
          }, 'ICD10');
          break;
          
        default:
          throw new Error(`Unknown test: ${testId}`);
      }
      
      setTestResults(prev => ({
        ...prev,
        [testId]: {
          status: 'success',
          result,
          timestamp: new Date().toISOString(),
          responseTime: 1200 // This would be measured in real implementation
        }
      }));
      
      addLogEntry(`Test ${testId} completed successfully`, 'success', result);
      
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [testId]: {
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        }
      }));
      
      addLogEntry(`Test ${testId} failed: ${error.message}`, 'error');
    } finally {
      setCurrentTest(null);
    }
  };

  // Run all tests
  const runAllTests = async () => {
    addLogEntry('Starting comprehensive AI test suite', 'info');
    
    for (const test of testScenarios) {
      await runTest(test.id);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    addLogEntry('All tests completed', 'success');
  };

  // Get performance metrics
  useEffect(() => {
    if (isAIReady) {
      const updateMetrics = () => {
        const metrics = getAIPerformanceMetrics();
        setPerformanceMetrics(metrics);
      };
      
      updateMetrics();
      const interval = setInterval(updateMetrics, 5000);
      return () => clearInterval(interval);
    }
  }, [isAIReady, getAIPerformanceMetrics]);

  // Get category icon
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'language': return <LanguageIcon />;
      case 'healthcare': return <AIIcon />;
      case 'security': return <SecurityIcon />;
      case 'analytics': return <AnalyticsIcon />;
      case 'automation': return <PerformanceIcon />;
      default: return <AIIcon />;
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      case 'running': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box p={3} dir={isRTL ? 'rtl' : 'ltr'}>
      <Typography variant="h4" gutterBottom>
        {currentLanguage === 'ar' ? 'اختبار تكامل الذكاء الاصطناعي PyBrain' : 'PyBrain AI Integration Testing'}
      </Typography>
      
      {/* AI Status Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {currentLanguage === 'ar' ? 'حالة النظام' : 'System Status'}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip 
                  label={isAIReady ? (currentLanguage === 'ar' ? 'جاهز' : 'Ready') : (currentLanguage === 'ar' ? 'غير جاهز' : 'Not Ready')}
                  color={isAIReady ? 'success' : 'error'}
                  icon={<AIIcon />}
                />
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip 
                  label={isProcessing ? (currentLanguage === 'ar' ? 'معالجة' : 'Processing') : (currentLanguage === 'ar' ? 'خامل' : 'Idle')}
                  color={isProcessing ? 'warning' : 'success'}
                />
                {isProcessing && <CircularProgress size={16} />}
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                {currentLanguage === 'ar' ? 'النماذج المتاحة:' : 'Available Models:'} {Object.keys(AI_MODELS).length}
              </Typography>
            </Grid>
          </Grid>
          
          {/* Performance Metrics */}
          {performanceMetrics && (
            <Box mt={2} p={2} sx={{ backgroundColor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                {currentLanguage === 'ar' ? 'مقاييس الأداء' : 'Performance Metrics'}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2">
                    {currentLanguage === 'ar' ? 'الاستجابة:' : 'Response:'} {Math.round(performanceMetrics.avgResponseTime || 0)}ms
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2">
                    {currentLanguage === 'ar' ? 'التخزين المؤقت:' : 'Cache:'} {performanceMetrics.cacheSize || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2">
                    {currentLanguage === 'ar' ? 'النجاح:' : 'Success:'} {performanceMetrics.successfulRequests || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2">
                    {currentLanguage === 'ar' ? 'الأخطاء:' : 'Errors:'} {performanceMetrics.failedRequests || 0}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Arabic Text Input for Testing */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {currentLanguage === 'ar' ? 'نص الاختبار العربي' : 'Arabic Test Text'}
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={arabicTestText}
            onChange={(e) => setArabicTestText(e.target.value)}
            placeholder={currentLanguage === 'ar' 
              ? 'أدخل النص الطبي العربي للاختبار...'
              : 'Enter Arabic medical text for testing...'}
            sx={{ direction: 'rtl' }}
          />
        </CardContent>
      </Card>

      {/* Test Controls */}
      <Box mb={3} display="flex" gap={2} flexWrap="wrap">
        <Button
          variant="contained"
          onClick={runAllTests}
          disabled={!isAIReady || isProcessing}
          startIcon={<AIIcon />}
        >
          {currentLanguage === 'ar' ? 'تشغيل جميع الاختبارات' : 'Run All Tests'}
        </Button>
        
        <Button
          variant="outlined"
          onClick={() => {
            setTestResults({});
            setTestLog([]);
          }}
        >
          {currentLanguage === 'ar' ? 'مسح النتائج' : 'Clear Results'}
        </Button>
      </Box>

      {/* Test Scenarios */}
      <Typography variant="h6" gutterBottom>
        {currentLanguage === 'ar' ? 'سيناريوهات الاختبار' : 'Test Scenarios'}
      </Typography>
      
      {testScenarios.map((test) => (
        <Accordion key={test.id} sx={{ mb: 1 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2} flex={1}>
              {getCategoryIcon(test.category)}
              <Box flex={1}>
                <Typography variant="subtitle1">{test.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {test.description}
                </Typography>
              </Box>
              <Box>
                {testResults[test.id] && (
                  <Chip
                    label={testResults[test.id].status}
                    color={getStatusColor(testResults[test.id].status)}
                    size="small"
                  />
                )}
                {currentTest === test.id && (
                  <CircularProgress size={20} sx={{ ml: 1 }} />
                )}
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Button
                variant="outlined"
                size="small"
                onClick={() => runTest(test.id)}
                disabled={!isAIReady || currentTest === test.id}
                sx={{ mb: 2 }}
              >
                {currentLanguage === 'ar' ? 'تشغيل الاختبار' : 'Run Test'}
              </Button>
              
              {testResults[test.id] && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    {currentLanguage === 'ar' ? 'النتيجة:' : 'Result:'}
                  </Typography>
                  {testResults[test.id].status === 'success' ? (
                    <Box component="pre" sx={{ 
                      backgroundColor: 'background.default', 
                      p: 1, 
                      borderRadius: 1,
                      fontSize: '0.8rem',
                      overflow: 'auto',
                      maxHeight: 200
                    }}>
                      {JSON.stringify(testResults[test.id].result, null, 2)}
                    </Box>
                  ) : (
                    <Alert severity="error">
                      {testResults[test.id].error}
                    </Alert>
                  )}
                </Box>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Test Log */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {currentLanguage === 'ar' ? 'سجل الاختبارات' : 'Test Log'}
          </Typography>
          <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
            <List dense>
              {testLog.map((entry) => (
                <React.Fragment key={entry.id}>
                  <ListItem>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip 
                            label={entry.type} 
                            size="small" 
                            color={getStatusColor(entry.type)}
                          />
                          <Typography variant="body2">
                            {entry.message}
                          </Typography>
                        </Box>
                      }
                      secondary={entry.timestamp}
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AITestingComponent;