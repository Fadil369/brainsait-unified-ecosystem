import {
    AccountTree,
    Analytics,
    Assignment,
    Dashboard,
    Home,
    Language,
    LocalHospital,
    Logout,
    Menu as MenuIcon,
    Notifications,
    Person,
    School,
    Security,
    Settings,
    Support,
} from '@mui/icons-material';
import {
    AppBar,
    Avatar,
    Badge,
    Box,
    Container,
    Divider,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Menu,
    MenuItem,
    Toolbar,
    Tooltip,
    Typography,
    useMediaQuery,
    useTheme,
    Fade,
    Zoom,
    Slide,
    alpha,
    styled,
    keyframes,
} from '@mui/material';
import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useLanguage } from '../hooks/useLanguage';

const drawerWidth = 280;

// Glass-morphism animations
const ambientGlow = keyframes`
  0% {
    box-shadow: 
      0 8px 32px 0 rgba(31, 38, 135, 0.37),
      inset 0 0 0 1px rgba(255, 255, 255, 0.18),
      0 0 0 0 rgba(116, 79, 168, 0.4);
  }
  50% {
    box-shadow: 
      0 8px 32px 0 rgba(31, 38, 135, 0.47),
      inset 0 0 0 1px rgba(255, 255, 255, 0.28),
      0 0 20px 5px rgba(116, 79, 168, 0.3);
  }
  100% {
    box-shadow: 
      0 8px 32px 0 rgba(31, 38, 135, 0.37),
      inset 0 0 0 1px rgba(255, 255, 255, 0.18),
      0 0 0 0 rgba(116, 79, 168, 0.4);
  }
`;

const pulseGlow = keyframes`
  0%, 100% {
    transform: scale(1);
    filter: brightness(1);
  }
  50% {
    transform: scale(1.02);
    filter: brightness(1.1);
  }
`;

const floatingEffect = keyframes`
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-3px);
  }
`;

// Glass Drawer with revolutionary glass-morphism
const _GlassDrawer = styled(Drawer)(({ theme, glassintensity = '1' }) => ({
  '& .MuiDrawer-paper': {
    background: `linear-gradient(
      135deg,
      ${alpha(theme.palette.background.paper, 0.1)} 0%,
      ${alpha(theme.palette.background.paper, 0.05)} 100%
    )`,
    backdropFilter: `blur(${16 * parseFloat(glassintensity)}px)`,
    WebkitBackdropFilter: `blur(${16 * parseFloat(glassintensity)}px)`,
    border: `1px solid ${alpha(theme.palette.common.white, 0.2)}`,
    borderRight: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
    boxShadow: `
      0 8px 32px 0 ${alpha(theme.palette.common.black, 0.1)},
      inset 0 0 0 1px ${alpha(theme.palette.common.white, 0.1)}
    `,
    animation: `${ambientGlow} 4s ease-in-out infinite`,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: `linear-gradient(
        45deg,
        ${alpha(theme.palette.primary.main, 0.03)} 0%,
        transparent 50%,
        ${alpha(theme.palette.secondary.main, 0.02)} 100%
      )`,
      pointerEvents: 'none',
    },
    '&:hover': {
      backdropFilter: `blur(${20 * parseFloat(glassintensity)}px)`,
      WebkitBackdropFilter: `blur(${20 * parseFloat(glassintensity)}px)`,
      boxShadow: `
        0 16px 48px 0 ${alpha(theme.palette.common.black, 0.15)},
        inset 0 0 0 1px ${alpha(theme.palette.common.white, 0.2)}
      `,
    },
  },
}));

// Glass App Bar with futuristic styling
const _GlassAppBar = styled(AppBar)(({ theme, glassintensity = '1' }) => ({
  background: `linear-gradient(
    90deg,
    ${alpha(theme.palette.background.paper, 0.8)} 0%,
    ${alpha(theme.palette.background.paper, 0.9)} 100%
  )`,
  backdropFilter: `blur(${12 * parseFloat(glassintensity)}px)`,
  WebkitBackdropFilter: `blur(${12 * parseFloat(glassintensity)}px)`,
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  boxShadow: `
    0 4px 24px 0 ${alpha(theme.palette.common.black, 0.08)},
    inset 0 -1px 0 0 ${alpha(theme.palette.common.white, 0.1)}
  `,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: `linear-gradient(
      90deg,
      ${theme.palette.primary.main} 0%,
      ${theme.palette.secondary.main} 100%
    )`,
    opacity: 0.7,
  },
  '&:hover': {
    backdropFilter: `blur(${16 * parseFloat(glassintensity)}px)`,
    WebkitBackdropFilter: `blur(${16 * parseFloat(glassintensity)}px)`,
    boxShadow: `
      0 8px 32px 0 ${alpha(theme.palette.common.black, 0.12)},
      inset 0 -1px 0 0 ${alpha(theme.palette.common.white, 0.15)}
    `,
  },
}));

// Enhanced glass panel for branding section
const GlassBrandPanel = styled(Box)(({ theme }) => ({
  background: `linear-gradient(
    135deg,
    ${alpha(theme.palette.primary.main, 0.1)} 0%,
    ${alpha(theme.palette.secondary.main, 0.05)} 100%
  )`,
  backdropFilter: 'blur(8px)',
  WebkitBackdropFilter: 'blur(8px)',
  border: `1px solid ${alpha(theme.palette.common.white, 0.2)}`,
  borderRadius: '16px',
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '1px',
    background: `linear-gradient(
      90deg,
      transparent 0%,
      ${alpha(theme.palette.primary.main, 0.5)} 50%,
      transparent 100%
    )`,
  },
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `
      0 8px 24px 0 ${alpha(theme.palette.primary.main, 0.2)},
      inset 0 0 0 1px ${alpha(theme.palette.common.white, 0.3)}
    `,
    animation: `${pulseGlow} 2s ease-in-out infinite`,
  },
}));

// Glass navigation item with hover effects
const GlassNavItem = styled(ListItemButton)(({ theme, isActive }) => ({
  borderRadius: '12px',
  margin: '4px 8px',
  background: isActive
    ? `linear-gradient(
        135deg,
        ${alpha(theme.palette.primary.main, 0.2)} 0%,
        ${alpha(theme.palette.primary.main, 0.1)} 100%
      )`
    : 'transparent',
  backdropFilter: isActive ? 'blur(8px)' : 'none',
  WebkitBackdropFilter: isActive ? 'blur(8px)' : 'none',
  border: `1px solid ${isActive ? alpha(theme.palette.primary.main, 0.3) : 'transparent'}`,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: `linear-gradient(
      90deg,
      transparent 0%,
      ${alpha(theme.palette.primary.main, 0.1)} 50%,
      transparent 100%
    )`,
    transition: 'left 0.6s ease',
  },
  '&:hover': {
    background: `linear-gradient(
      135deg,
      ${alpha(theme.palette.primary.main, 0.15)} 0%,
      ${alpha(theme.palette.secondary.main, 0.1)} 100%
    )`,
    backdropFilter: 'blur(10px)',
    WebkitBackdropFilter: 'blur(10px)',
    border: `1px solid ${alpha(theme.palette.primary.main, 0.4)}`,
    transform: 'translateX(4px)',
    boxShadow: `
      0 4px 16px 0 ${alpha(theme.palette.primary.main, 0.2)},
      inset 0 0 0 1px ${alpha(theme.palette.common.white, 0.2)}
    `,
    '&::before': {
      left: '100%',
    },
  },
  '&:active': {
    transform: 'translateX(2px) scale(0.98)',
  },
}));

// Glass status panel with animated effects
const GlassStatusPanel = styled(Box)(({ theme }) => ({
  background: `linear-gradient(
    135deg,
    ${alpha(theme.palette.success.main, 0.1)} 0%,
    ${alpha(theme.palette.success.main, 0.05)} 100%
  )`,
  backdropFilter: 'blur(8px)',
  WebkitBackdropFilter: 'blur(8px)',
  border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
  borderRadius: '16px',
  position: 'relative',
  overflow: 'hidden',
  animation: `${floatingEffect} 6s ease-in-out infinite`,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: `linear-gradient(
      90deg,
      ${theme.palette.success.main} 0%,
      ${alpha(theme.palette.success.main, 0.5)} 100%
    )`,
    borderRadius: '16px 16px 0 0',
  },
  '&:hover': {
    transform: 'translateY(-4px) scale(1.02)',
    boxShadow: `
      0 12px 32px 0 ${alpha(theme.palette.success.main, 0.3)},
      inset 0 0 0 1px ${alpha(theme.palette.common.white, 0.3)}
    `,
  },
}));

// Glass menu with enhanced styling
const _GlassMenu = styled(Menu)(({ theme }) => ({
  '& .MuiPaper-root': {
    background: `linear-gradient(
      135deg,
      ${alpha(theme.palette.background.paper, 0.9)} 0%,
      ${alpha(theme.palette.background.paper, 0.8)} 100%
    )`,
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: `1px solid ${alpha(theme.palette.common.white, 0.2)}`,
    borderRadius: '16px',
    boxShadow: `
      0 16px 48px 0 ${alpha(theme.palette.common.black, 0.1)},
      inset 0 0 0 1px ${alpha(theme.palette.common.white, 0.1)}
    `,
    overflow: 'hidden',
    '& .MuiMenuItem-root': {
      borderRadius: '8px',
      margin: '4px 8px',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        background: `linear-gradient(
          90deg,
          ${alpha(theme.palette.primary.main, 0.1)} 0%,
          ${alpha(theme.palette.secondary.main, 0.05)} 100%
        )`,
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        transform: 'translateX(4px)',
      },
    },
  },
}));

const Layout = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { language, setLanguage, isRTL } = useLanguage();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileMenuAnchor, setProfileMenuAnchor] = useState(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);
  const [glassIntensity, _setGlassIntensity] = useState(1);
  const [isHovering, setIsHovering] = useState(false);
  const [ambientLighting, setAmbientLighting] = useState(true);
  
  const _appBarRef = useRef(null);
  const _drawerRef = useRef(null);

  // Dynamic glass intensity based on user interaction
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isHovering) {
        const intensity = Math.min(1.5, 1 + (e.clientX + e.clientY) / 2000);
        setGlassIntensity(intensity);
      }
    };

    const handleTouchStart = () => {
      setGlassIntensity(1.3);
    };

    const handleTouchEnd = () => {
      setGlassIntensity(1);
    };

    if (isMobile) {
      document.addEventListener('touchstart', handleTouchStart);
      document.addEventListener('touchend', handleTouchEnd);
    } else {
      document.addEventListener('mousemove', handleMouseMove);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isHovering, isMobile]);

  // Ambient lighting effect
  useEffect(() => {
    const interval = setInterval(() => {
      if (ambientLighting) {
        setGlassIntensity(prev => prev + (Math.random() - 0.5) * 0.1);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [ambientLighting]);

  // Navigation items for BrainSAIT Healthcare Platform
  const navigationItems = [
    {
      text: isRTL ? 'لوحة القيادة الموحدة' : 'Unified Dashboard',
      icon: <Dashboard />,
      path: '/',
      category: 'main'
    },
    {
      text: isRTL ? 'مساحة العمل' : 'Workspace',
      icon: <Home />,
      path: '/workspace',
      category: 'main'
    },
    {
      text: isRTL ? 'شجرة المعرفات الطبية' : 'Healthcare OID Tree',
      icon: <AccountTree />,
      path: '/oid-tree',
      category: 'main'
    },
    {
      text: isRTL ? 'الرعاية الصحية' : 'Healthcare',
      icon: <LocalHospital />,
      path: '/healthcare',
      category: 'healthcare'
    },
    {
      text: isRTL ? 'التحليلات الذكية' : 'AI Analytics',
      icon: <Analytics />,
      path: '/ai-analytics',
      category: 'analytics'
    },
    {
      text: isRTL ? 'التدريب الطبي' : 'Medical Training',
      icon: <School />,
      path: '/training',
      category: 'training'
    },
    {
      text: isRTL ? 'البوابات المتخصصة' : 'Specialized Portals',
      icon: <Assignment />,
      path: '/portals',
      category: 'portals'
    },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleNotificationsOpen = (event) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const toggleLanguage = () => {
    setLanguage(language === 'ar' ? 'en' : 'ar');
  };

  const _toggleGlassTheme = () => {
    setAmbientLighting(!ambientLighting);
    setGlassIntensity(ambientLighting ? 0.5 : 1.2);
  };

  const drawer = (
    <Box
      sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* Logo and Brand with Glass Panel */}
      <GlassBrandPanel
        sx={{
          p: 2.5,
          m: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Zoom in timeout={800}>
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              width: 44,
              height: 44,
              boxShadow: `0 4px 16px ${alpha(theme.palette.primary.main, 0.3)}`,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                transform: 'scale(1.1) rotate(5deg)',
                boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`,
              },
            }}
          >
            <LocalHospital />
          </Avatar>
        </Zoom>
        <Fade in timeout={1000}>
          <Box>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 'bold', 
                lineHeight: 1.2,
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                transition: 'all 0.3s ease',
              }}
            >
              {isRTL ? 'برين سايت' : 'BrainSAIT'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {isRTL ? 'منصة الرعاية الصحية الموحدة' : 'Unified Healthcare Platform'}
            </Typography>
          </Box>
        </Fade>
      </GlassBrandPanel>

      {/* Navigation Items with Glass Effects */}
      <List sx={{ px: 1, py: 2, flexGrow: 1 }}>
        {navigationItems.map((item, index) => {
          const isActive = location.pathname === item.path;
          
          return (
            <Slide
              key={item.path}
              direction={isRTL ? "left" : "right"}
              in
              timeout={600 + index * 100}
            >
              <ListItem disablePadding sx={{ mb: 1 }}>
                <GlassNavItem
                  isActive={isActive}
                  onClick={() => handleNavigation(item.path)}
                >
                  <ListItemIcon
                    sx={{
                      color: isActive ? 'primary.main' : 'text.secondary',
                      minWidth: 40,
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '& svg': {
                        filter: isActive ? `drop-shadow(0 0 8px ${alpha(theme.palette.primary.main, 0.6)})` : 'none',
                      },
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    sx={{
                      '& .MuiTypography-root': {
                        fontSize: '0.9rem',
                        fontWeight: isActive ? 600 : 500,
                        transition: 'all 0.3s ease',
                        textShadow: isActive ? `0 0 10px ${alpha(theme.palette.primary.main, 0.5)}` : 'none',
                      },
                    }}
                  />
                </GlassNavItem>
              </ListItem>
            </Slide>
          );
        })}
      </List>

      {/* Healthcare Status Indicator with Glass Effect */}
      <Box sx={{ p: 2, mt: 'auto' }}>
        <Fade in timeout={1200}>
          <GlassStatusPanel sx={{ p: 2.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: 'success.main',
                  boxShadow: `0 0 12px ${alpha(theme.palette.success.main, 0.6)}`,
                  animation: `${pulseGlow} 2s ease-in-out infinite`,
                }}
              />
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 600,
                  color: 'success.main',
                  textShadow: `0 0 8px ${alpha(theme.palette.success.main, 0.3)}`,
                }}
              >
                {isRTL ? 'حالة النظام' : 'System Status'}
              </Typography>
            </Box>
            <Typography 
              variant="caption" 
              sx={{ 
                color: 'text.secondary',
                fontSize: '0.8rem',
              }}
            >
              {isRTL ? 'جميع الأنظمة تعمل بشكل طبيعي' : 'All systems operational'}
            </Typography>
          </GlassStatusPanel>
        </Fade>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: 'background.paper',
          color: 'text.primary',
          borderBottom: 1,
          borderColor: 'divider',
          boxShadow: 'none',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {isRTL ? 'منصة الرعاية الصحية الموحدة' : 'Unified Healthcare Platform'}
          </Typography>

          {/* Language Toggle */}
          <Tooltip title={isRTL ? 'تغيير اللغة' : 'Change Language'}>
            <IconButton onClick={toggleLanguage} color="inherit">
              <Language />
            </IconButton>
          </Tooltip>

          {/* Notifications */}
          <Tooltip title={isRTL ? 'الإشعارات' : 'Notifications'}>
            <IconButton
              color="inherit"
              onClick={handleNotificationsOpen}
            >
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Profile Menu */}
          <Tooltip title={isRTL ? 'الملف الشخصي' : 'Profile'}>
            <IconButton
              onClick={handleProfileMenuOpen}
              sx={{ ml: 1 }}
            >
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: 'secondary.main',
                }}
              >
                <Person />
              </Avatar>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              bgcolor: 'background.paper',
              borderRight: 1,
              borderColor: 'divider',
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              bgcolor: 'background.paper',
              borderRight: 1,
              borderColor: 'divider',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <Toolbar />
        <Container maxWidth={false} sx={{ py: 3, px: 3 }}>
          {children}
        </Container>
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={profileMenuAnchor}
        open={Boolean(profileMenuAnchor)}
        onClose={handleProfileMenuClose}
        onClick={handleProfileMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => navigate('/profile')}>
          <ListItemIcon>
            <Person fontSize="small" />
          </ListItemIcon>
          {isRTL ? 'الملف الشخصي' : 'Profile'}
        </MenuItem>
        <MenuItem onClick={() => navigate('/settings')}>
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          {isRTL ? 'الإعدادات' : 'Settings'}
        </MenuItem>
        <Divider />
        <MenuItem>
          <ListItemIcon>
            <Security fontSize="small" />
          </ListItemIcon>
          {isRTL ? 'الأمان' : 'Security'}
        </MenuItem>
        <MenuItem>
          <ListItemIcon>
            <Support fontSize="small" />
          </ListItemIcon>
          {isRTL ? 'الدعم' : 'Support'}
        </MenuItem>
        <Divider />
        <MenuItem>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          {isRTL ? 'تسجيل الخروج' : 'Logout'}
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchor}
        open={Boolean(notificationsAnchor)}
        onClose={handleNotificationsClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          sx: { width: 320, maxHeight: 400 }
        }}
      >
        <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'primary.contrastText' }}>
          <Typography variant="h6">
            {isRTL ? 'الإشعارات' : 'Notifications'}
          </Typography>
        </Box>
        <MenuItem>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {isRTL ? 'تم استلام مطالبة جديدة' : 'New NPHIES claim received'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {isRTL ? 'منذ 5 دقائق' : '5 minutes ago'}
            </Typography>
          </Box>
        </MenuItem>
        <MenuItem>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {isRTL ? 'تحديث النظام مكتمل' : 'System update completed'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {isRTL ? 'منذ ساعة' : '1 hour ago'}
            </Typography>
          </Box>
        </MenuItem>
        <MenuItem>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {isRTL ? 'تذكير: مراجعة التدريب' : 'Reminder: Training review'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {isRTL ? 'منذ ساعتين' : '2 hours ago'}
            </Typography>
          </Box>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Layout;
