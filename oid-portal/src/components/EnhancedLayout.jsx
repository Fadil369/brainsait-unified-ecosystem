/**
 * Enhanced Layout Component for Revolutionary Healthcare Design System
 * Integrates the neural glass-morphism system with existing Material-UI components
 * Provides seamless transitions and mobile-first responsive design
 */

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

  // Update time every second
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
      {/* Drawer Header */}
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

      {/* Navigation Menu */}
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
      {/* Enhanced App Bar */}
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

          {/* Time Display */}
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
          </Typography>\n\n          {/* Language Toggle */}\n          <IconButton \n            color=\"inherit\" \n            className=\"neural-btn\"\n            sx={{ mr: 1 }}\n          >\n            <Language />\n          </IconButton>\n\n          {/* Notifications */}\n          <IconButton \n            color=\"inherit\" \n            className=\"neural-btn\"\n            sx={{ mr: 1, position: 'relative' }}\n          >\n            <Notifications />\n            {notificationCount > 0 && (\n              <Chip \n                label={notificationCount} \n                size=\"small\" \n                color=\"error\"\n                sx={{ \n                  position: 'absolute', \n                  top: 0, \n                  right: 0,\n                  minWidth: 20,\n                  height: 20,\n                  fontSize: '0.7rem',\n                  background: 'linear-gradient(135deg, #ef4444, #dc2626)',\n                  animation: 'neural-pulse 2s ease-in-out infinite'\n                }}\n              />\n            )}\n          </IconButton>\n\n          {/* User Menu */}\n          <IconButton\n            color=\"inherit\"\n            onClick={handleUserMenuOpen}\n            className=\"neural-btn\"\n          >\n            <Avatar \n              sx={{ \n                width: 32, \n                height: 32,\n                background: 'linear-gradient(135deg, #0ea5e9, #a855f7)',\n                border: '2px solid rgba(255, 255, 255, 0.2)',\n                fontSize: '1rem',\n                fontWeight: 600\n              }}\n            >\n              د\n            </Avatar>\n          </IconButton>\n\n          <Menu\n            anchorEl={userMenuAnchor}\n            open={Boolean(userMenuAnchor)}\n            onClose={handleUserMenuClose}\n            PaperProps={{\n              className: \"neural-glass-secondary\",\n              sx: {\n                mt: 2,\n                minWidth: 200,\n                background: 'transparent',\n                backdropFilter: 'blur(20px)',\n                border: '1px solid rgba(255, 255, 255, 0.1)',\n              }\n            }}\n          >\n            <MenuItem onClick={handleUserMenuClose} className=\"neural-nav-item\">\n              <AccountCircle sx={{ mr: 2, color: '#0ea5e9' }} />\n              Profile Settings\n            </MenuItem>\n            <MenuItem onClick={handleUserMenuClose} className=\"neural-nav-item\">\n              <Logout sx={{ mr: 2, color: '#ef4444' }} />\n              Sign Out\n            </MenuItem>\n          </Menu>\n        </Toolbar>\n      </AppBar>\n\n      {/* Navigation Drawer */}\n      <Drawer\n        variant={isMobile ? 'temporary' : 'persistent'}\n        open={isMobile ? drawerOpen : true}\n        onClose={handleDrawerToggle}\n        ModalProps={{\n          keepMounted: true, // Better mobile performance\n        }}\n        PaperProps={{\n          sx: {\n            background: 'transparent',\n            border: 'none',\n          }\n        }}\n      >\n        {drawer}\n      </Drawer>\n\n      {/* Main Content Area */}\n      <Box\n        component=\"main\"\n        sx={{\n          flexGrow: 1,\n          minHeight: '100vh',\n          transition: theme.transitions.create('margin', {\n            easing: theme.transitions.easing.sharp,\n            duration: theme.transitions.duration.leavingScreen,\n          }),\n          marginLeft: isMobile ? 0 : '280px',\n          paddingTop: '64px', // AppBar height\n        }}\n      >\n        <Slide in direction=\"right\" timeout={600}>\n          <Box sx={{ height: '100%' }}>\n            {children}\n          </Box>\n        </Slide>\n      </Box>\n\n      {/* Quick Action Button for Mobile */}\n      {isMobile && (\n        <Button\n          className=\"neural-btn\"\n          onClick={() => navigate('/revolutionary')}\n          sx={{\n            position: 'fixed',\n            bottom: 24,\n            right: 24,\n            minWidth: 'auto',\n            width: 56,\n            height: 56,\n            borderRadius: '50%',\n            background: 'linear-gradient(135deg, #0ea5e9, #a855f7)',\n            zIndex: 1000,\n            '&:hover': {\n              background: 'linear-gradient(135deg, #0284c7, #9333ea)',\n              transform: 'scale(1.1)',\n            }\n          }}\n        >\n          <Psychology />\n        </Button>\n      )}\n    </Box>\n  );\n};\n\nexport default EnhancedLayout;
