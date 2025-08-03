import {
    AccessTime,
    BookOutlined,
    CheckCircle,
    GroupOutlined,
    PlayCircleOutlined,
    School,
    SchoolOutlined,
    TrendingUp,
    VerifiedUser,
    WorkspacePremium
} from '@mui/icons-material';
import {
    Avatar,
    Box,
    Button,
    Card,
    CardContent,
    CardMedia,
    Chip,
    Container,
    Divider,
    Grid,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Paper,
    Tab,
    Tabs,
    Typography
} from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../hooks/useLanguage';

const TrainingPlatform = () => {
  const navigate = useNavigate();
  const { t: _t } = useLanguage();
  const [activeTab, setActiveTab] = useState(0);

  // Training programs data based on BOT.md
  const trainingPrograms = [
    {
      id: 'MCC-101',
      title: 'Medical Coding Foundations',
      titleAr: 'أساسيات الترميز الطبي',
      description: 'Comprehensive 300-hour program covering ICD-10, CPT, and HCPCS coding systems',
      descriptionAr: 'برنامج شامل لمدة 300 ساعة يغطي أنظمة الترميز ICD-10 و CPT و HCPCS',
      duration: 300,
      price: 4999,
      type: 'foundation',
      certification: 'CPC',
      modules: 4,
      enrolled: 1250,
      rating: 4.8,
      image: '/api/placeholder/400/250',
      progress: 0,
    },
    {
      id: 'NCC-201',
      title: 'NPHIES Compliance Certification',
      titleAr: 'شهادة الامتثال لنظام نفيس',
      description: 'Master NPHIES platform integration and compliance requirements',
      descriptionAr: 'إتقان تكامل منصة نفيس ومتطلبات الامتثال',
      duration: 160,
      price: 2999,
      type: 'advanced',
      certification: 'NPHIES',
      modules: 6,
      enrolled: 890,
      rating: 4.9,
      image: '/api/placeholder/400/250',
      progress: 0,
    },
    {
      id: 'RCM-301',
      title: 'Revenue Cycle Management Professional',
      titleAr: 'محترف إدارة دورة الإيرادات',
      description: 'Advanced RCM strategies for healthcare organizations',
      descriptionAr: 'استراتيجيات متقدمة لإدارة دورة الإيرادات للمؤسسات الصحية',
      duration: 240,
      price: 7999,
      type: 'specialization',
      certification: 'RCMP',
      modules: 8,
      enrolled: 456,
      rating: 4.7,
      image: '/api/placeholder/400/250',
      progress: 0,
    },
    {
      id: 'HIT-401',
      title: 'Healthcare IT Integration Specialist',
      titleAr: 'أخصائي تكامل تقنية المعلومات الصحية',
      description: 'Master healthcare system integration and FHIR standards',
      descriptionAr: 'إتقان تكامل الأنظمة الصحية ومعايير FHIR',
      duration: 200,
      price: 6999,
      type: 'specialization',
      certification: 'HITS',
      modules: 7,
      enrolled: 234,
      rating: 4.6,
      image: '/api/placeholder/400/250',
      progress: 0,
    },
  ];

  // My enrolled courses (sample data)
  const myEnrollments = [
    {
      ...trainingPrograms[0],
      progress: 65,
      nextModule: 'Module 3: NPHIES Integration',
      completionDate: '2025-04-15',
    },
    {
      ...trainingPrograms[1],
      progress: 30,
      nextModule: 'Module 2: Claims Submission',
      completionDate: '2025-06-30',
    },
  ];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getTypeColor = (type) => {
    const colors = {
      foundation: 'primary',
      advanced: 'secondary',
      specialization: 'warning',
      corporate: 'success',
    };
    return colors[type] || 'default';
  };

  const renderProgramCard = (program, isEnrolled = false) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
    >
      <CardMedia
        component="img"
        height="200"
        image={program.image}
        alt={program.title}
        sx={{ objectFit: 'cover' }}
      />
      <CardContent sx={{ flexGrow: 1, p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="h6" component="h3" gutterBottom>
            {program.title}
          </Typography>
          <Chip
            label={program.type.toUpperCase()}
            color={getTypeColor(program.type)}
            size="small"
          />
        </Box>

        <Typography variant="body2" color="text.secondary" paragraph>
          {program.description}
        </Typography>

        {isEnrolled && (
          <Box mb={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2" color="text.secondary">
                Progress
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {program.progress}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={program.progress}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary" mt={1}>
              Next: {program.nextModule}
            </Typography>
          </Box>
        )}

        <Grid container spacing={2} mb={2}>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={0.5}>
              <AccessTime fontSize="small" color="action" />
              <Typography variant="body2">{program.duration} hours</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={0.5}>
              <BookOutlined fontSize="small" color="action" />
              <Typography variant="body2">{program.modules} modules</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={0.5}>
              <GroupOutlined fontSize="small" color="action" />
              <Typography variant="body2">{program.enrolled} enrolled</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={0.5}>
              <WorkspacePremium fontSize="small" color="action" />
              <Typography variant="body2">{program.certification}</Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" color="primary">
            SAR {program.price.toLocaleString()}
          </Typography>
          {isEnrolled ? (
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayCircleOutlined />}
              onClick={() => navigate(`/training/course/${program.id}`)}
            >
              Continue Learning
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate(`/training/enroll/${program.id}`)}
            >
              Enroll Now
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );

  const renderCertificationStats = () => (
    <Grid container spacing={3} mb={4}>
      <Grid item xs={12} md={3}>
        <Paper
          sx={{
            p: 3,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          }}
        >
          <SchoolOutlined sx={{ fontSize: 48, mb: 1 }} />
          <Typography variant="h4" fontWeight="bold">
            25,000+
          </Typography>
          <Typography variant="body2">Certified Professionals</Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} md={3}>
        <Paper
          sx={{
            p: 3,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
          }}
        >
          <VerifiedUser sx={{ fontSize: 48, mb: 1 }} />
          <Typography variant="h4" fontWeight="bold">
            85%
          </Typography>
          <Typography variant="body2">Pass Rate</Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} md={3}>
        <Paper
          sx={{
            p: 3,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white',
          }}
        >
          <TrendingUp sx={{ fontSize: 48, mb: 1 }} />
          <Typography variant="h4" fontWeight="bold">
            SAR 45K
          </Typography>
          <Typography variant="body2">Avg. Salary Increase</Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} md={3}>
        <Paper
          sx={{
            p: 3,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            color: 'white',
          }}
        >
          <School sx={{ fontSize: 48, mb: 1 }} />
          <Typography variant="h4" fontWeight="bold">
            4.8/5
          </Typography>
          <Typography variant="body2">Student Rating</Typography>
        </Paper>
      </Grid>
    </Grid>
  );

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Medical Coding Training & Certification
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Industry-leading training programs aligned with Saudi Vision 2030 healthcare transformation
        </Typography>

        {renderCertificationStats()}

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 4 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="My Courses" />
            <Tab label="All Programs" />
            <Tab label="Certifications" />
            <Tab label="Corporate Training" />
          </Tabs>
        </Box>

        {activeTab === 0 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              My Enrolled Courses
            </Typography>
            <Grid container spacing={3}>
              {myEnrollments.map((program) => (
                <Grid item xs={12} md={6} lg={4} key={program.id}>
                  {renderProgramCard(program, true)}
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              Available Training Programs
            </Typography>
            <Grid container spacing={3}>
              {trainingPrograms.map((program) => (
                <Grid item xs={12} md={6} lg={4} key={program.id}>
                  {renderProgramCard(program)}
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {activeTab === 2 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              Professional Certifications
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ p: 3 }}>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                      <WorkspacePremium />
                    </Avatar>
                    <Box>
                      <Typography variant="h6">CPC - Certified Professional Coder</Typography>
                      <Typography variant="body2" color="text.secondary">
                        AAPC Certification
                      </Typography>
                    </Box>
                  </Box>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary="Internationally recognized certification" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary="300-hour comprehensive training" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary="Saudi healthcare system focus" />
                    </ListItem>
                  </List>
                  <Button variant="contained" fullWidth sx={{ mt: 2 }}>
                    Learn More
                  </Button>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ p: 3 }}>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Avatar sx={{ bgcolor: 'secondary.main', width: 56, height: 56 }}>
                      <VerifiedUser />
                    </Avatar>
                    <Box>
                      <Typography variant="h6">NPHIES Compliance Specialist</Typography>
                      <Typography variant="body2" color="text.secondary">
                        SCFHS Approved
                      </Typography>
                    </Box>
                  </Box>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary="Saudi-specific certification" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary="160-hour focused program" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary="Direct NPHIES platform training" />
                    </ListItem>
                  </List>
                  <Button variant="contained" fullWidth sx={{ mt: 2 }}>
                    Learn More
                  </Button>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {activeTab === 3 && (
          <Box>
            <Typography variant="h5" gutterBottom mb={3}>
              Corporate Training Solutions
            </Typography>
            <Card sx={{ p: 4 }}>
              <Grid container spacing={4} alignItems="center">
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Transform Your Healthcare Workforce
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Customized training programs for healthcare organizations implementing NPHIES
                    compliance and revenue cycle optimization.
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="On-site and virtual training options"
                        secondary="Flexible delivery to suit your needs"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Custom curriculum development"
                        secondary="Tailored to your organization's specific requirements"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Train-the-trainer programs"
                        secondary="Build internal expertise for sustainability"
                      />
                    </ListItem>
                  </List>
                  <Button variant="contained" size="large" sx={{ mt: 2 }}>
                    Request Corporate Quote
                  </Button>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box
                    component="img"
                    src="/api/placeholder/600/400"
                    alt="Corporate Training"
                    sx={{
                      width: '100%',
                      borderRadius: 2,
                      boxShadow: 3,
                    }}
                  />
                </Grid>
              </Grid>
            </Card>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default TrainingPlatform;