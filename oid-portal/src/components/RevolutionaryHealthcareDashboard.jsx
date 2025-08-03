import {
  Add,
  Analytics,
  Biotech,
  Close,
  Dashboard,
  Emergency,
  FilterList,
  HealthAndSafety,
  LocalHospital,
  Menu as MenuIcon,
  MonitorHeart,
  Notifications,
  PersonAdd,
  Psychology,
  Search,
  Security,
  Settings,
} from "@mui/icons-material";
import {
  Alert,
  AppBar,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Drawer,
  Fade,
  Grid,
  Grow,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Slide,
  SpeedDial,
  SpeedDialAction,
  TextField,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useEffect, useState } from "react";

/**
 * Revolutionary Healthcare Dashboard - ULTIMATE UNIFIED DESIGN SYSTEM
 * This component showcases the neural glass-morphism design system
 * for creating disruptive change in healthcare interfaces
 */
const RevolutionaryHealthcareDashboard = () => {
  const theme = useTheme();
  const _isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [notifications] = useState(3);
  const [loading, setLoading] = useState(false);

  // Update time every second for real-time feel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleQuickAction = (action) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      console.log(`${action} executed`);
    }, 1500);
  };

  const speedDialActions = [
    { icon: <PersonAdd />, name: "Add Patient", action: "add-patient" },
    { icon: <Emergency />, name: "Emergency Alert", action: "emergency" },
    { icon: <MonitorHeart />, name: "Vital Signs", action: "vitals" },
    { icon: <Analytics />, name: "Analytics", action: "analytics" },
  ];

  const menuItems = [
    { icon: <Dashboard />, text: "Dashboard", color: "#0ea5e9" },
    { icon: <LocalHospital />, text: "Patients", color: "#06d6a0" },
    { icon: <MonitorHeart />, text: "Vital Signs", color: "#f72585" },
    { icon: <Biotech />, text: "Lab Results", color: "#a855f7" },
    { icon: <Security />, text: "Compliance", color: "#06b6d4" },
    { icon: <Psychology />, text: "AI Insights", color: "#8b5cf6" },
    { icon: <Analytics />, text: "Analytics", color: "#10b981" },
    { icon: <Settings />, text: "Settings", color: "#64748b" },
  ];

  const healthcareMetrics = [
    {
      title: "Active Patients",
      value: "2,847",
      change: "+12%",
      status: "success",
    },
    {
      title: "Critical Alerts",
      value: "3",
      change: "-50%",
      status: "critical",
    },
    {
      title: "Consultations Today",
      value: "127",
      change: "+8%",
      status: "success",
    },
    {
      title: "System Uptime",
      value: "99.97%",
      change: "+0.02%",
      status: "success",
    },
  ];

  const recentAlerts = [
    {
      type: "critical",
      message: "Patient Ahmed Al-Rashid - Irregular heartbeat detected",
      time: "2 min ago",
    },
    {
      type: "warning",
      message: "Medication shortage alert - Insulin supplies low",
      time: "15 min ago",
    },
    {
      type: "info",
      message: "System backup completed successfully",
      time: "1 hour ago",
    },
  ];

  return (
    <Box
      className="neural-glass-immersive"
      sx={{ minHeight: "100vh", position: "relative" }}
    >
      {/* Neural Navigation Bar */}
      <AppBar
        position="fixed"
        className="neural-nav"
        sx={{
          background: "transparent",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
          boxShadow: "0 4px 20px rgba(14, 165, 233, 0.15)",
        }}
      >
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setDrawerOpen(true)}
            sx={{ mr: 2, display: { md: "none" } }}
            className="neural-btn"
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
            BrainSAIT Healthcare Platform
          </Typography>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Typography
              variant="body2"
              sx={{ opacity: 0.8, display: { xs: "none", sm: "block" } }}
            >
              {currentTime.toLocaleTimeString("ar-SA", {
                hour: "2-digit",
                minute: "2-digit",
                timeZone: "Asia/Riyadh",
              })}
            </Typography>

            <IconButton color="inherit" className="neural-btn">
              <Notifications />
              {notifications > 0 && (
                <Chip
                  label={notifications}
                  size="small"
                  color="error"
                  sx={{
                    position: "absolute",
                    top: 0,
                    right: 0,
                    minWidth: 20,
                    height: 20,
                    fontSize: "0.75rem",
                  }}
                />
              )}
            </IconButton>

            <Avatar
              sx={{
                width: 32,
                height: 32,
                background:
                  "linear-gradient(135deg, rgba(14, 165, 233, 0.8), rgba(168, 85, 247, 0.8))",
                border: "2px solid rgba(255, 255, 255, 0.2)",
              }}
            >
              د
            </Avatar>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Neural Side Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          className: "neural-glass-secondary",
          sx: {
            width: 280,
            background: "transparent",
            backdropFilter: "blur(40px)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
          },
        }}
      >
        <Box sx={{ p: 2, borderBottom: "1px solid rgba(255, 255, 255, 0.1)" }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Navigation
            </Typography>
            <IconButton
              onClick={() => setDrawerOpen(false)}
              className="neural-btn"
            >
              <Close />
            </IconButton>
          </Box>
        </Box>

        <List sx={{ p: 1 }}>
          {menuItems.map((item, index) => (
            <Fade in timeout={300 + index * 100} key={item.text}>
              <ListItem
                button
                className="neural-nav-item"
                sx={{
                  borderRadius: "var(--radius-neural-medium)",
                  margin: "4px 0",
                  "&:hover": {
                    background: `linear-gradient(135deg, ${item.color}20, ${item.color}10)`,
                    transform: "translateX(8px)",
                  },
                }}
              >
                <ListItemIcon sx={{ color: item.color, minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{ fontWeight: 500 }}
                />
              </ListItem>
            </Fade>
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ pt: 12, pb: 4 }}>
        {/* Hero Section */}
        <Slide in direction="down" timeout={600}>
          <Box className="neural-card" sx={{ mb: 4, textAlign: "center" }}>
            <Typography
              variant="h3"
              className="neural-card-title"
              sx={{
                background: "linear-gradient(135deg, #0ea5e9, #a855f7)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                mb: 2,
              }}
            >
              نظام الرعاية الصحية الموحد
            </Typography>
            <Typography variant="h4" sx={{ mb: 2, opacity: 0.9 }}>
              Ultimate Unified Healthcare Intelligence
            </Typography>
            <Typography
              variant="body1"
              sx={{ opacity: 0.7, maxWidth: 600, mx: "auto" }}
            >
              Experience the future of healthcare management with our
              revolutionary glass-morphism design system, optimized for
              Arabic-first interfaces and clinical precision.
            </Typography>
          </Box>
        </Slide>

        {/* Loading Progress */}
        {loading && (
          <Grow in>
            <Box className="neural-card" sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Processing Healthcare Operation...
              </Typography>
              <LinearProgress
                sx={{
                  height: 8,
                  borderRadius: 4,
                  background: "rgba(255, 255, 255, 0.1)",
                  "& .MuiLinearProgress-bar": {
                    background: "linear-gradient(90deg, #0ea5e9, #a855f7)",
                    borderRadius: 4,
                  },
                }}
              />
            </Box>
          </Grow>
        )}

        {/* Healthcare Metrics Grid */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {healthcareMetrics.map((metric, index) => (
            <Grid item xs={12} sm={6} md={3} key={metric.title}>
              <Fade in timeout={800 + index * 200}>
                <Card
                  className={`neural-card neural-status-${metric.status}`}
                  sx={{
                    height: "100%",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    "&:hover": {
                      transform: "translateY(-8px) scale(1.02)",
                    },
                  }}
                >
                  <CardContent>
                    <Typography variant="h3" sx={{ mb: 1, fontWeight: 700 }}>
                      {metric.value}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.8, mb: 1 }}>
                      {metric.title}
                    </Typography>
                    <Chip
                      label={metric.change}
                      size="small"
                      color={metric.status === "critical" ? "error" : "success"}
                      sx={{
                        background:
                          metric.status === "critical"
                            ? "rgba(239, 68, 68, 0.2)"
                            : "rgba(34, 197, 94, 0.2)",
                        backdropFilter: "blur(10px)",
                      }}
                    />
                  </CardContent>
                </Card>
              </Fade>
            </Grid>
          ))}
        </Grid>

        {/* Recent Alerts */}
        <Slide in direction="up" timeout={1000}>
          <Box className="neural-card" sx={{ mb: 4 }}>
            <Typography
              variant="h5"
              className="neural-card-title"
              sx={{ mb: 3 }}
            >
              Real-time Healthcare Alerts
            </Typography>

            {recentAlerts.map((alert, index) => (
              <Fade in timeout={1200 + index * 200} key={index}>
                <Alert
                  severity={
                    alert.type === "critical"
                      ? "error"
                      : alert.type === "warning"
                      ? "warning"
                      : "info"
                  }
                  sx={{
                    mb: 2,
                    background: "rgba(255, 255, 255, 0.05)",
                    backdropFilter: "blur(10px)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    "& .MuiAlert-icon": {
                      color:
                        alert.type === "critical"
                          ? "#ef4444"
                          : alert.type === "warning"
                          ? "#f59e0b"
                          : "#3b82f6",
                    },
                  }}
                >
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {alert.message}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.7 }}>
                      {alert.time}
                    </Typography>
                  </Box>
                </Alert>
              </Fade>
            ))}
          </Box>
        </Slide>

        {/* Quick Actions Grid */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Grow in timeout={1400}>
              <Box className="neural-card">
                <Typography
                  variant="h5"
                  className="neural-card-title"
                  sx={{ mb: 3 }}
                >
                  Patient Management Interface
                </Typography>

                <Box sx={{ mb: 3, display: "flex", gap: 2, flexWrap: "wrap" }}>
                  <TextField
                    placeholder="Search patients..."
                    className="neural-input"
                    size="small"
                    sx={{ flex: 1, minWidth: 200 }}
                    InputProps={{
                      startAdornment: <Search sx={{ mr: 1, opacity: 0.7 }} />,
                    }}
                  />
                  <Button className="neural-btn" startIcon={<FilterList />}>
                    Filter
                  </Button>
                  <Button className="neural-btn" startIcon={<Add />}>
                    Add Patient
                  </Button>
                </Box>

                <Typography variant="body2" sx={{ opacity: 0.7 }}>
                  Advanced patient management with AI-powered insights and
                  real-time monitoring capabilities. Seamlessly integrated with
                  NPHIES and FHIR R4 standards for comprehensive healthcare data
                  management.
                </Typography>
              </Box>
            </Grow>
          </Grid>

          <Grid item xs={12} md={4}>
            <Grow in timeout={1600}>
              <Box className="neural-card">
                <Typography
                  variant="h6"
                  className="neural-card-title"
                  sx={{ mb: 2 }}
                >
                  System Status
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Neural Processing
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={87}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      background: "rgba(255, 255, 255, 0.1)",
                      "& .MuiLinearProgress-bar": {
                        background: "linear-gradient(90deg, #06d6a0, #0ea5e9)",
                        borderRadius: 3,
                      },
                    }}
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Database Sync
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={95}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      background: "rgba(255, 255, 255, 0.1)",
                      "& .MuiLinearProgress-bar": {
                        background: "linear-gradient(90deg, #a855f7, #ec4899)",
                        borderRadius: 3,
                      },
                    }}
                  />
                </Box>

                <Button
                  variant="outlined"
                  fullWidth
                  className="neural-btn"
                  startIcon={<HealthAndSafety />}
                >
                  System Health Check
                </Button>
              </Box>
            </Grow>
          </Grid>
        </Grid>
      </Container>

      {/* Floating Action Speed Dial */}
      <SpeedDial
        ariaLabel="Healthcare Quick Actions"
        sx={{
          position: "fixed",
          bottom: 24,
          right: 24,
          "& .MuiFab-primary": {
            background: "linear-gradient(135deg, #0ea5e9, #a855f7)",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            "&:hover": {
              background: "linear-gradient(135deg, #0284c7, #9333ea)",
            },
          },
        }}
        icon={<Add />}
        openIcon={<Close />}
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={() => handleQuickAction(action.action)}
            sx={{
              "& .MuiFab-primary": {
                background: "rgba(255, 255, 255, 0.1)",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                color: "white",
                "&:hover": {
                  background: "rgba(255, 255, 255, 0.2)",
                },
              },
            }}
          />
        ))}
      </SpeedDial>
    </Box>
  );
};

export default RevolutionaryHealthcareDashboard;
