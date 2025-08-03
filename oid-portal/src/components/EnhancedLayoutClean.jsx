import { useState, useEffect } from 'react';
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  Avatar,
  Chip,
  useTheme,
  useMediaQuery,
  Fade,
  Slide,
  Button,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  LocalHospital,
  MonitorHeart,
  Security,
  Settings,
  Notifications,
  Language,
  AccountCircle,
  Logout,
  Psychology,
  Analytics,
  HealthAndSafety
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const EnhancedLayout = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [notificationCount] = useState(3);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const menuItems = [
    {
      text: 'Revolutionary Dashboard',
      icon: <Psychology />,
      path: '/revolutionary',
      color: '#a855f7',
      description: 'Future of Healthcare UI'
    },
    {
      text: 'Unified Workspace',
      icon: <Dashboard />,
      path: '/',
      color: '#0ea5e9',
      description: 'Main Healthcare Hub'
    },
    {
      text: 'Patient Management',
      icon: <LocalHospital />,
      path: '/patients',
      color: '#06d6a0',
      description: 'Patient Care Center'
    },
    {
      text: 'Vital Monitoring',
      icon: <MonitorHeart />,
      path: '/vitals',
      color: '#f59e0b',
      description: 'Real-time Health Data'
    },
    {
      text: 'OID Management',
      icon: <Security />,
      path: '/oid-tree',
      color: '#06b6d4',
      description: 'Identity & Security'
    },
    {
      text: 'Healthcare Analytics',
      icon: <Analytics />,
      path: '/analytics',
      color: '#8b5cf6',
      description: 'AI-Powered Insights'
    },
    {
      text: 'System Health',
      icon: <HealthAndSafety />,
      path: '/health',
      color: '#10b981',
      description: 'Platform Monitoring'
    },
    {
      text: 'Settings',
      icon: <Settings />,
      path: '/settings',
      color: '#64748b',
      description: 'System Configuration'
    },
  ];

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const isCurrentPath = (path) => {
    return location.pathname === path;
  };

  const drawer = (
    <Box className="neural-glass-secondary" sx={{ height: '100%', width: 280 }}>
      <Box sx={{ p: 3, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontWeight: 700,
            background: 'linear-gradient(135deg, #0ea5e9, #a855f7)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textAlign: 'center'
          }}
        >
          BrainSAIT Healthcare
        </Typography>
        <Typography 
          variant="caption" 
          sx={{ 
            display: 'block', 
            textAlign: 'center', 
            opacity: 0.7,
            mt: 0.5
          }}
        >
          Revolutionary Intelligence System
        </Typography>
      </Box>

      <List sx={{ p: 2, height: 'calc(100% - 140px)', overflowY: 'auto' }}>
        {menuItems.map((item, index) => (
          <Fade in timeout={300 + index * 100} key={item.text}>
            <ListItem 
              button 
              onClick={() => handleNavigation(item.path)}
              className="neural-nav-item"
              sx={{ 
                borderRadius: 'var(--radius-neural-medium)',
                margin: '6px 0',
                padding: '12px 16px',
                background: isCurrentPath(item.path) 
                  ? `linear-gradient(135deg, ${item.color}30, ${item.color}15)`
                  : 'transparent',
                border: isCurrentPath(item.path) 
                  ? `1px solid ${item.color}50`
                  : '1px solid transparent',
                transition: 'all 0.3s ease',
                '&:hover': {
                  background: `linear-gradient(135deg, ${item.color}25, ${item.color}10)`,
                  transform: 'translateX(8px)',
                  border: `1px solid ${item.color}40`,
                }
              }}
            >
              <ListItemIcon 
                sx={{ 
                  color: item.color, 
                  minWidth: 40,
                  '& .MuiSvgIcon-root': {
                    fontSize: 24
                  }
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                secondary={item.description}
                primaryTypographyProps={{ 
                  fontWeight: isCurrentPath(item.path) ? 600 : 500,
                  fontSize: '0.95rem'
                }}
                secondaryTypographyProps={{
                  fontSize: '0.75rem',
                  opacity: 0.6
                }}
              />
            </ListItem>
          </Fade>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar 
        position="fixed" 
        className="neural-nav"
        sx={{ 
          background: 'transparent',
          backdropFilter: 'blur(40px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 4px 32px rgba(14, 165, 233, 0.15)',
          zIndex: theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            className="neural-btn"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1,
              fontWeight: 600,
              background: 'linear-gradient(135deg, #ffffff, #e2e8f0)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {menuItems.find(item => isCurrentPath(item.path))?.text || 'Healthcare Platform'}
          </Typography>

          <Typography 
            variant="body2" 
            sx={{ 
              mr: 2, 
              opacity: 0.8,
              display: { xs: 'none', sm: 'block' },
              fontFamily: 'monospace'
            }}
          >
            {currentTime.toLocaleTimeString('ar-SA', { 
              hour: '2-digit', 
              minute: '2-digit',
              second: '2-digit',
              timeZone: 'Asia/Riyadh'
            })}
          </Typography>

          <IconButton 
            color="inherit" 
            className="neural-btn"
            sx={{ mr: 1 }}
          >
            <Language />
          </IconButton>

          <IconButton 
            color="inherit" 
            className="neural-btn"
            sx={{ mr: 1, position: 'relative' }}
          >
            <Notifications />
            {notificationCount > 0 && (
              <Chip 
                label={notificationCount} 
                size="small" 
                color="error"
                sx={{ 
                  position: 'absolute', 
                  top: 0, 
                  right: 0,
                  minWidth: 20,
                  height: 20,
                  fontSize: '0.7rem',
                  background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                  animation: 'neural-pulse 2s ease-in-out infinite'
                }}
              />
            )}
          </IconButton>

          <IconButton
            color="inherit"
            onClick={handleUserMenuOpen}
            className="neural-btn"
          >
            <Avatar 
              sx={{ 
                width: 32, 
                height: 32,
                background: 'linear-gradient(135deg, #0ea5e9, #a855f7)',
                border: '2px solid rgba(255, 255, 255, 0.2)',
                fontSize: '1rem',
                fontWeight: 600
              }}
            >
              د
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={handleUserMenuClose}
            PaperProps={{
              className: "neural-glass-secondary",
              sx: {
                mt: 2,
                minWidth: 200,
                background: 'transparent',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            <MenuItem onClick={handleUserMenuClose} className="neural-nav-item">
              <AccountCircle sx={{ mr: 2, color: '#0ea5e9' }} />
              Profile Settings
            </MenuItem>
            <MenuItem onClick={handleUserMenuClose} className="neural-nav-item">
              <Logout sx={{ mr: 2, color: '#ef4444' }} />
              Sign Out
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        variant={isMobile ? 'temporary' : 'persistent'}
        open={isMobile ? drawerOpen : true}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        PaperProps={{
          sx: {
            background: 'transparent',
            border: 'none',
          }
        }}
      >
        {drawer}
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: isMobile ? 0 : '280px',
          paddingTop: '64px',
        }}
      >
        <Slide in direction="right" timeout={600}>
          <Box sx={{ height: '100%' }}>
            {children}
          </Box>
        </Slide>
      </Box>

      {isMobile && (
        <Button
          className="neural-btn"
          onClick={() => navigate('/revolutionary')}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            minWidth: 'auto',
            width: 56,
            height: 56,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #0ea5e9, #a855f7)',
            zIndex: 1000,
            '&:hover': {
              background: 'linear-gradient(135deg, #0284c7, #9333ea)',
              transform: 'scale(1.1)',
            }
          }}
        >
          <Psychology />
        </Button>
      )}
    </Box>
  );
};

export default EnhancedLayout;
