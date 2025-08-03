import {
    AccountTree,
    Add,
    Assignment,
    Business,
    Delete,
    DeviceHub,
    Edit,
    ExpandLess,
    ExpandMore,
    Info,
    LocalHospital,
    Person,
    Refresh,
    Security,
    Visibility,
    ViewInAr,
    TrendingUp,
    NetworkCheck,
    Psychology,
    Science,
    MonitorHeart,
    Emergency,
    HealthAndSafety,
} from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    Grid,
    IconButton,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    TextField,
    Tooltip,
    Typography,
    Slider,
    Switch,
    FormControlLabel,
    Badge,
    Avatar,
    SpeedDial,
    SpeedDialIcon,
    SpeedDialAction,
    Collapse,
    LinearProgress,
} from '@mui/material';
import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useLanguage } from '../hooks/useLanguage';

const OidTree = () => {
  const { isRTL } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState(new Set(['root']));
  const [selectedOid, setSelectedOid] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newOidData, setNewOidData] = useState({
    name: '',
    description: '',
    type: 'organization',
  });
  
  // Revolutionary 3D and Neural Network Features
  const [viewMode, setViewMode] = useState('3d'); // '2d', '3d', 'neural'
  const [neuralIntensity, setNeuralIntensity] = useState(0.8);
  const [realTimeSync, setRealTimeSync] = useState(true);
  const [particleEffects, setParticleEffects] = useState(true);
  const [nphiesStatus, setNphiesStatus] = useState('connected');
  const [searchQuery, setSearchQuery] = useState('');
  const [hoveredNode, setHoveredNode] = useState(null);
  const [nodeMetrics, setNodeMetrics] = useState(new Map());
  const containerRef = useRef(null);
  const animationRef = useRef(null);
  
  // Performance optimization with useMemo for large trees
  const filteredNodes = useMemo(() => {
    if (!searchQuery) return oidTree;
    // Implement deep search logic here
    return oidTree;
  }, [searchQuery]);
  
  // Real-time NPHIES status simulation
  useEffect(() => {
    if (!realTimeSync) return;
    
    const interval = setInterval(() => {
      setNphiesStatus(prev => {
        const statuses = ['connected', 'processing', 'syncing', 'error'];
        const currentIndex = statuses.indexOf(prev);
        return statuses[(currentIndex + 1) % statuses.length];
      });
    }, 5000);
    
    return () => clearInterval(interval);
  }, [realTimeSync]);
  
  // Neural network pulse animation
  useEffect(() => {
    if (viewMode !== 'neural' || !particleEffects) return;
    
    const animate = () => {
      // Neural pulse animation logic
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [viewMode, particleEffects]);
  
  // Generate node metrics for performance analytics
  useEffect(() => {
    const generateMetrics = (node) => {
      const metrics = {
        performance: Math.random() * 100,
        uptime: 95 + Math.random() * 5,
        connections: Math.floor(Math.random() * 1000),
        lastSync: Date.now() - Math.random() * 300000
      };
      setNodeMetrics(prev => new Map(prev.set(node.id, metrics)));
      
      if (node.children) {
        node.children.forEach(generateMetrics);
      }
    };
    
    generateMetrics(oidTree);
  }, []);

  // Mock OID tree data - represents the Saudi Healthcare OID structure
  const [oidTree] = useState({
    id: '1.2.840.114494.100.1',
    name: isRTL ? 'النظام الصحي السعودي' : 'Saudi Healthcare System',
    description: isRTL ? 'الجذر الرئيسي للنظام الصحي السعودي' : 'Root of Saudi Healthcare System',
    type: 'root',
    children: [
      {
        id: '1.2.840.114494.100.1.1',
        name: isRTL ? 'مقدمي الخدمات الصحية' : 'Healthcare Providers',
        description: isRTL ? 'جميع مقدمي الخدمات الصحية' : 'All healthcare providers',
        type: 'category',
        children: [
          {
            id: '1.2.840.114494.100.1.1.1',
            name: isRTL ? 'مستشفى الملك فيصل التخصصي' : 'King Faisal Specialist Hospital',
            description: isRTL ? 'مستشفى تخصصي رائد' : 'Leading specialized hospital',
            type: 'provider',
            status: 'active',
            children: []
          },
          {
            id: '1.2.840.114494.100.1.1.2',
            name: isRTL ? 'مجمع الملك عبدالله الطبي' : 'King Abdullah Medical Complex',
            description: isRTL ? 'مجمع طبي شامل' : 'Comprehensive medical complex',
            type: 'provider',
            status: 'active',
            children: []
          }
        ]
      },
      {
        id: '1.2.840.114494.100.1.2',
        name: isRTL ? 'الأجهزة الطبية' : 'Medical Devices',
        description: isRTL ? 'جميع الأجهزة الطبية المعتمدة' : 'All certified medical devices',
        type: 'category',
        children: [
          {
            id: '1.2.840.114494.100.1.2.1',
            name: isRTL ? 'أجهزة التصوير الطبي' : 'Medical Imaging Devices',
            description: isRTL ? 'أجهزة الأشعة والتصوير' : 'Radiology and imaging equipment',
            type: 'device_category',
            children: []
          }
        ]
      },
      {
        id: '1.2.840.114494.100.1.3',
        name: isRTL ? 'نفيس NPHIES' : 'NPHIES Integration',
        description: isRTL ? 'تكامل مع نظام نفيس' : 'Integration with NPHIES system',
        type: 'system',
        children: [
          {
            id: '1.2.840.114494.100.1.3.1',
            name: isRTL ? 'مطالبات التأمين' : 'Insurance Claims',
            description: isRTL ? 'معرفات مطالبات التأمين' : 'Insurance claim identifiers',
            type: 'claims',
            children: []
          }
        ]
      },
      {
        id: '1.2.840.114494.100.1.4',
        name: isRTL ? 'الذكاء الاصطناعي الطبي' : 'Medical AI Services',
        description: isRTL ? 'خدمات الذكاء الاصطناعي الطبية' : 'Medical artificial intelligence services',
        type: 'ai_services',
        children: []
      }
    ]
  });

  const toggleExpand = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  const getTypeIcon = (type) => {
    const iconStyle = { color: getTypeColor(type) };
    switch (type) {
      case 'root':
        return <AccountTree sx={iconStyle} />;
      case 'provider':
        return <LocalHospital sx={iconStyle} />;
      case 'organization':
        return <Business sx={iconStyle} />;
      case 'device_category':
      case 'device':
        return <DeviceHub sx={iconStyle} />;
      case 'person':
        return <Person sx={iconStyle} />;
      case 'system':
        return <Security sx={iconStyle} />;
      case 'ai_services':
        return <Psychology sx={iconStyle} />;
      case 'claims':
        return <Assignment sx={iconStyle} />;
      default:
        return <Assignment sx={iconStyle} />;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'root': return '#0ea5e9';
      case 'provider': return '#6366f1';
      case 'organization': return '#06b6d4';
      case 'device_category':
      case 'device': return '#f59e0b';
      case 'person': return '#10b981';
      case 'system': return '#ef4444';
      case 'ai_services': return '#a855f7';
      case 'claims': return '#ec4899';
      default: return '#64748b';
    }
  };

  // Revolutionary 3D Node Renderer with Neural Network Effects
  const renderOidNode = useCallback((node, level = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const hasChildren = node.children && node.children.length > 0;
    const isSelected = selectedOid?.id === node.id;
    const isHovered = hoveredNode === node.id;
    const metrics = nodeMetrics.get(node.id) || {};
    
    // Dynamic styling based on view mode
    const getNodeClassName = () => {
      const baseClass = viewMode === '3d' ? 'neural-oid-node-3d' : 'neural-card';
      const activeClass = isSelected ? ' active' : '';
      const hoveredClass = isHovered ? ' hovered' : '';
      return `${baseClass}${activeClass}${hoveredClass}`;
    };
    
    // Neural network status indicator
    const getNeuralStatusColor = () => {
      if (metrics.performance > 90) return '#00e676';
      if (metrics.performance > 70) return '#ffa726';
      if (metrics.performance > 50) return '#ff9800';
      return '#f44336';
    };

    return (
      <Box 
        key={node.id}
        sx={{
          transform: viewMode === '3d' ? `translateX(${level * 20}px) translateZ(${level * 5}px)` : `translateX(${level * 20}px)`,
          perspective: '1000px',
          transformStyle: 'preserve-3d',
          transition: 'all 0.4s cubic-bezier(0.23, 1, 0.32, 1)',
          position: 'relative',
          zIndex: isHovered ? 10 : 1,
        }}
        onMouseEnter={() => setHoveredNode(node.id)}
        onMouseLeave={() => setHoveredNode(null)}
      >
        {/* Neural Connection Line */}
        {level > 0 && viewMode === 'neural' && (
          <Box
            className="neural-oid-connection"
            sx={{
              position: 'absolute',
              top: '50%',
              left: '-20px',
              width: '20px',
              height: '2px',
              background: `linear-gradient(90deg, 
                rgba(14, 165, 233, 0.8) 0%,
                rgba(99, 102, 241, 0.6) 50%,
                ${getNeuralStatusColor()} 100%)`,
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.8) 50%, transparent 100%)',
                animation: 'neural-flow 2s linear infinite'
              }
            }}
          />
        )}
        
        <Card 
          className={getNodeClassName()}
          sx={{ 
            mb: 1.5,
            cursor: 'pointer',
            bgcolor: isSelected ? 'action.selected' : 'transparent',
            border: isSelected ? '2px solid' : '1px solid',
            borderColor: isSelected ? 'primary.main' : 'rgba(255, 255, 255, 0.15)',
            backdropFilter: `blur(${8 + neuralIntensity * 16}px) saturate(${150 + neuralIntensity * 100}%)`,
            background: viewMode === 'neural' 
              ? `linear-gradient(135deg, 
                  rgba(14, 165, 233, ${0.1 + neuralIntensity * 0.1}) 0%,
                  rgba(99, 102, 241, ${0.08 + neuralIntensity * 0.08}) 45%,
                  rgba(168, 85, 247, ${0.06 + neuralIntensity * 0.06}) 100%)`
              : 'rgba(255, 255, 255, 0.05)',
            transform: isHovered && viewMode === '3d' 
              ? 'translateZ(20px) rotateX(5deg) rotateY(5deg) scale(1.02)' 
              : 'translateZ(0)',
            boxShadow: isHovered 
              ? `0 20px 40px rgba(14, 165, 233, 0.3), 0 0 0 2px rgba(14, 165, 233, 0.2)` 
              : '0 4px 20px rgba(14, 165, 233, 0.15)',
            '&:hover': {
              borderColor: 'primary.main',
              '& .node-metrics': {
                opacity: 1,
                transform: 'translateY(0)'
              }
            }
          }}
          onClick={() => setSelectedOid(node)}
        >
          <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
            <Box display="flex" alignItems="center" gap={1.5}>
              {/* Expansion Control */}
              {hasChildren && (
                <IconButton 
                  size="small" 
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleExpand(node.id);
                  }}
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.2)',
                      transform: 'scale(1.1)'
                    }
                  }}
                >
                  {isExpanded ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              )}
              
              {/* Node Type Icon with Neural Glow */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 40,
                  height: 40,
                  borderRadius: '12px',
                  background: viewMode === 'neural' 
                    ? `radial-gradient(circle, ${getNeuralStatusColor()}20 0%, transparent 70%)`
                    : 'rgba(255, 255, 255, 0.1)',
                  border: `1px solid ${getNeuralStatusColor()}40`,
                  animation: viewMode === 'neural' ? 'neural-pulse 2s ease-in-out infinite' : 'none'
                }}
              >
                {getTypeIcon(node.type)}
              </Box>
              
              {/* Node Information */}
              <Box flexGrow={1}>
                <Typography 
                  variant="body1" 
                  fontWeight={600}
                  sx={{
                    color: 'rgba(255, 255, 255, 0.95)',
                    fontSize: '1rem',
                    lineHeight: 1.3,
                    fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
                  }}
                >
                  {node.name}
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{
                    color: 'rgba(255, 255, 255, 0.6)',
                    fontFamily: 'monospace',
                    fontSize: '0.75rem'
                  }}
                >
                  {node.id}
                </Typography>
                
                {/* Real-time Metrics */}
                {viewMode === 'neural' && metrics.performance && (
                  <Box 
                    className="node-metrics"
                    sx={{
                      opacity: 0,
                      transform: 'translateY(10px)',
                      transition: 'all 0.3s ease',
                      mt: 0.5
                    }}
                  >
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Performance:
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={metrics.performance}
                        sx={{
                          width: 60,
                          height: 4,
                          borderRadius: 2,
                          backgroundColor: 'rgba(255, 255, 255, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getNeuralStatusColor(),
                            borderRadius: 2
                          }
                        }}
                      />
                      <Typography variant="caption" sx={{ color: getNeuralStatusColor() }}>
                        {Math.round(metrics.performance)}%
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Box>
              
              {/* Status Chips */}
              <Box display="flex" flexDirection="column" gap={0.5} alignItems="flex-end">
                <Chip 
                  label={node.type} 
                  size="small" 
                  sx={{
                    backgroundColor: `${getTypeColor(node.type)}20`,
                    border: `1px solid ${getTypeColor(node.type)}40`,
                    color: getTypeColor(node.type),
                    fontWeight: 500,
                    fontSize: '0.7rem'
                  }}
                />
                
                {node.status && (
                  <Chip 
                    label={node.status}
                    size="small"
                    sx={{
                      backgroundColor: node.status === 'active' ? 'rgba(0, 230, 118, 0.2)' : 'rgba(158, 158, 158, 0.2)',
                      border: node.status === 'active' ? '1px solid rgba(0, 230, 118, 0.4)' : '1px solid rgba(158, 158, 158, 0.4)',
                      color: node.status === 'active' ? '#00e676' : '#9e9e9e',
                      fontWeight: 500,
                      fontSize: '0.7rem'
                    }}
                  />
                )}
                
                {/* Real-time NPHIES Status */}
                {node.type === 'system' && (
                  <Chip
                    className={`neural-nphies-status ${nphiesStatus}`}
                    label={nphiesStatus.toUpperCase()}
                    size="small"
                    sx={{
                      fontSize: '0.65rem',
                      height: 20,
                      animation: realTimeSync ? 'neural-nphies-sync 4s ease-in-out infinite' : 'none'
                    }}
                  />
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Recursive Children Rendering */}
        {hasChildren && isExpanded && (
          <Collapse in={isExpanded} timeout="auto">
            <Box
              sx={{
                position: 'relative',
                '&::before': viewMode === 'neural' ? {
                  content: '""',
                  position: 'absolute',
                  left: '10px',
                  top: 0,
                  bottom: 0,
                  width: '2px',
                  background: `linear-gradient(180deg, 
                    ${getNeuralStatusColor()} 0%,
                    rgba(99, 102, 241, 0.6) 50%,
                    transparent 100%)`,
                  animation: 'neural-vertical-flow 3s ease-in-out infinite'
                } : {}
              }}
            >
              {node.children.map(child => renderOidNode(child, level + 1))}
            </Box>
          </Collapse>
        )}
      </Box>
    );
  }, [expandedNodes, selectedOid, hoveredNode, viewMode, neuralIntensity, nphiesStatus, realTimeSync, nodeMetrics, isRTL]);

  const handleAddOid = () => {
    setDialogOpen(true);
  };

  const handleSaveOid = () => {
    // Here you would typically save to backend
    console.log('Saving OID:', newOidData);
    setDialogOpen(false);
    setNewOidData({ name: '', description: '', type: 'organization' });
  };

  return (
    <Box 
      ref={containerRef}
      sx={{
        minHeight: '100vh',
        background: viewMode === 'neural' 
          ? `radial-gradient(circle at 30% 30%, rgba(14, 165, 233, 0.05) 0%, transparent 50%),
             radial-gradient(circle at 70% 70%, rgba(99, 102, 241, 0.03) 0%, transparent 50%),
             linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)`
          : 'linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Neural Particle Effects Background */}
      {viewMode === 'neural' && particleEffects && (
        <Box
          className="glass-particle-field"
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            pointerEvents: 'none',
            opacity: neuralIntensity,
            zIndex: 0
          }}
        />
      )}
      
      {/* Revolutionary Header with 3D Controls */}
      <Box 
        className="neural-card"
        sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 3,
          p: 3,
          position: 'relative',
          zIndex: 2
        }}
      >
        <Box>
          <Typography 
            variant="h3" 
            gutterBottom
            sx={{
              background: 'linear-gradient(135deg, #00e676 0%, #00b4d8 50%, #6c5ce7 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
              fontWeight: 700,
              fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
              fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
            }}
          >
            {isRTL ? 'شجرة المعرفات الطبية الذكية' : 'Intelligent Healthcare OID Tree'}
          </Typography>
          <Typography 
            variant="body1" 
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)',
              fontSize: '1rem'
            }}
          >
            {isRTL 
              ? 'إدارة وتنظيم معرفات النظام الصحي السعودي بتقنية الذكاء الاصطناعي'
              : 'AI-Powered Saudi Healthcare System Identity Management'}
          </Typography>
          
          {/* Real-time System Status */}
          <Box display="flex" alignItems="center" gap={2} mt={2}>
            <Badge 
              badgeContent={nodeMetrics.size}
              color="primary"
              sx={{
                '& .MuiBadge-badge': {
                  backgroundColor: '#00e676',
                  color: '#000'
                }
              }}
            >
              <Chip 
                icon={<NetworkCheck />}
                label={isRTL ? 'متصل' : 'Connected'}
                size="small"
                className="neural-nphies-status"
              />
            </Badge>
            
            <Chip 
              icon={<Psychology />}
              label={`Neural: ${Math.round(neuralIntensity * 100)}%`}
              size="small"
              sx={{
                backgroundColor: 'rgba(156, 136, 255, 0.2)',
                border: '1px solid rgba(156, 136, 255, 0.4)',
                color: '#9c88ff'
              }}
            />
            
            <Chip 
              icon={<MonitorHeart />}
              label={`${Math.round(95 + Math.random() * 5)}% Uptime`}
              size="small"
              className="neural-biometric-monitor"
            />
          </Box>
        </Box>
        
        {/* Advanced Control Panel */}
        <Box display="flex" flexDirection="column" gap={2} alignItems="flex-end">
          {/* View Mode Controls */}
          <Box display="flex" gap={1}>
            <Tooltip title={isRTL ? 'عرض ثنائي الأبعاد' : '2D View'}>
              <IconButton
                onClick={() => setViewMode('2d')}
                sx={{
                  backgroundColor: viewMode === '2d' ? 'rgba(14, 165, 233, 0.3)' : 'rgba(255, 255, 255, 0.1)',
                  border: `1px solid ${viewMode === '2d' ? 'rgba(14, 165, 233, 0.5)' : 'rgba(255, 255, 255, 0.2)'}`,
                  '&:hover': { backgroundColor: 'rgba(14, 165, 233, 0.2)' }
                }}
              >
                <Visibility />
              </IconButton>
            </Tooltip>
            
            <Tooltip title={isRTL ? 'عرض ثلاثي الأبعاد' : '3D View'}>
              <IconButton
                onClick={() => setViewMode('3d')}
                sx={{
                  backgroundColor: viewMode === '3d' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.1)',
                  border: `1px solid ${viewMode === '3d' ? 'rgba(99, 102, 241, 0.5)' : 'rgba(255, 255, 255, 0.2)'}`,
                  '&:hover': { backgroundColor: 'rgba(99, 102, 241, 0.2)' }
                }}
              >
                <ViewInAr />
              </IconButton>
            </Tooltip>
            
            <Tooltip title={isRTL ? 'الشبكة العصبية' : 'Neural Network'}>
              <IconButton
                onClick={() => setViewMode('neural')}
                sx={{
                  backgroundColor: viewMode === 'neural' ? 'rgba(168, 85, 247, 0.3)' : 'rgba(255, 255, 255, 0.1)',
                  border: `1px solid ${viewMode === 'neural' ? 'rgba(168, 85, 247, 0.5)' : 'rgba(255, 255, 255, 0.2)'}`,
                  '&:hover': { backgroundColor: 'rgba(168, 85, 247, 0.2)' },
                  animation: viewMode === 'neural' ? 'neural-pulse 2s ease-in-out infinite' : 'none'
                }}
              >
                <Psychology />
              </IconButton>
            </Tooltip>
          </Box>
          
          {/* Neural Intensity Slider */}
          {viewMode === 'neural' && (
            <Box width={150}>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {isRTL ? 'كثافة الشبكة العصبية' : 'Neural Intensity'}
              </Typography>
              <Slider
                value={neuralIntensity}
                onChange={(_, value) => setNeuralIntensity(value)}
                min={0.1}
                max={2.0}
                step={0.1}
                size="small"
                sx={{
                  color: '#9c88ff',
                  '& .MuiSlider-thumb': {
                    backgroundColor: '#9c88ff',
                    boxShadow: '0 0 10px rgba(156, 136, 255, 0.5)'
                  },
                  '& .MuiSlider-track': {
                    backgroundColor: '#9c88ff'
                  }
                }}
              />
            </Box>
          )}
          
          {/* Real-time Controls */}
          <Box display="flex" gap={1}>
            <FormControlLabel
              control={
                <Switch
                  checked={realTimeSync}
                  onChange={(e) => setRealTimeSync(e.target.checked)}
                  size="small"
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#00e676'
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#00e676'
                    }
                  }}
                />
              }
              label={
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {isRTL ? 'مزامنة فورية' : 'Real-time'}
                </Typography>
              }
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={particleEffects}
                  onChange={(e) => setParticleEffects(e.target.checked)}
                  size="small"
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#9c88ff'
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#9c88ff'
                    }
                  }}
                />
              }
              label={
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {isRTL ? 'التأثيرات' : 'Effects'}
                </Typography>
              }
            />
          </Box>
          
          {/* Action Buttons */}
          <Box display="flex" gap={1}>
            <Tooltip title={isRTL ? 'تحديث' : 'Refresh'}>
              <IconButton 
                onClick={handleRefresh} 
                disabled={loading}
                className="neural-btn-clinical"
                sx={{ minWidth: 48, minHeight: 48 }}
              >
                {loading ? <CircularProgress size={20} /> : <Refresh />}
              </IconButton>
            </Tooltip>
            
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddOid}
              className="neural-btn"
              sx={{
                minHeight: 48,
                background: 'var(--gradient-neural-primary)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                '&:hover': {
                  background: 'var(--gradient-neural-secondary)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 32px rgba(14, 165, 233, 0.3)'
                }
              }}
            >
              {isRTL ? 'إضافة معرف جديد' : 'Add New OID'}
            </Button>
          </Box>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ position: 'relative', zIndex: 2 }}>
        {/* Revolutionary OID Tree Visualization */}
        <Grid item xs={12} md={8}>
          <Box 
            className="neural-card"
            sx={{ 
              p: 3, 
              height: '75vh', 
              overflow: 'auto',
              position: 'relative',
              background: viewMode === 'neural' 
                ? 'var(--gradient-neural-healthcare)'
                : 'var(--gradient-neural-primary)',
              backdropFilter: `blur(${16 + neuralIntensity * 8}px) saturate(${150 + neuralIntensity * 50}%)`,
              border: '1px solid rgba(255, 255, 255, 0.15)',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '4px'
              },
              '&::-webkit-scrollbar-thumb': {
                background: 'rgba(14, 165, 233, 0.5)',
                borderRadius: '4px',
                '&:hover': {
                  background: 'rgba(14, 165, 233, 0.7)'
                }
              }
            }}
          >
            {/* Enhanced Header with Search */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography 
                variant="h5" 
                sx={{
                  color: 'rgba(255, 255, 255, 0.95)',
                  fontWeight: 600,
                  fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
                }}
              >
                {isRTL ? 'هيكل المعرفات الذكي' : 'Intelligent OID Structure'}
              </Typography>
              
              <TextField
                size="small"
                placeholder={isRTL ? 'البحث في الشجرة...' : 'Search tree...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="neural-input"
                sx={{
                  width: 250,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    '&:hover': {
                      border: '1px solid rgba(14, 165, 233, 0.3)'
                    },
                    '&.Mui-focused': {
                      border: '1px solid rgba(14, 165, 233, 0.5)',
                      boxShadow: '0 0 0 2px rgba(14, 165, 233, 0.2)'
                    }
                  },
                  '& .MuiOutlinedInput-input': {
                    color: 'rgba(255, 255, 255, 0.9)',
                    fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
                  }
                }}
              />
            </Box>
            
            <Divider sx={{ mb: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
            
            {/* Neural Network Tree Visualization */}
            <Box
              sx={{
                position: 'relative',
                transform: viewMode === '3d' ? 'perspective(1000px)' : 'none',
                transformStyle: 'preserve-3d'
              }}
            >
              {renderOidNode(filteredNodes)}
            </Box>
          </Box>
        </Grid>

        {/* Revolutionary Details Panel */}
        <Grid item xs={12} md={4}>
          <Box 
            className="neural-card"
            sx={{ 
              p: 3, 
              height: '75vh',
              background: selectedOid 
                ? 'var(--gradient-neural-healthcare)'
                : 'var(--gradient-neural-secondary)',
              backdropFilter: `blur(${16 + neuralIntensity * 8}px) saturate(${150 + neuralIntensity * 50}%)`,
              border: selectedOid 
                ? '2px solid rgba(0, 168, 107, 0.4)'
                : '1px solid rgba(255, 255, 255, 0.15)',
              animation: selectedOid ? 'neural-node-active 3s ease-in-out infinite' : 'none'
            }}
          >
            <Typography 
              variant="h5" 
              gutterBottom
              sx={{
                color: 'rgba(255, 255, 255, 0.95)',
                fontWeight: 600,
                fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
              }}
            >
              {isRTL ? 'تفاصيل المعرف المتقدمة' : 'Advanced OID Details'}
            </Typography>
            <Divider sx={{ mb: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
            
            {selectedOid ? (
              <Box>
                {/* Node Avatar and Basic Info */}
                <Box display="flex" alignItems="center" gap={2} mb={3}>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      background: viewMode === 'neural'
                        ? `radial-gradient(circle, rgba(14, 165, 233, 0.3) 0%, rgba(99, 102, 241, 0.2) 50%, transparent 100%)`
                        : 'var(--gradient-neural-primary)',
                      border: '2px solid rgba(14, 165, 233, 0.4)',
                      fontSize: '2rem'
                    }}
                  >
                    {getTypeIcon(selectedOid.type)}
                  </Avatar>
                  
                  <Box>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        color: 'rgba(255, 255, 255, 0.95)',
                        fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)',
                        fontWeight: 600
                      }}
                    >
                      {selectedOid.name}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: 'rgba(255, 255, 255, 0.6)',
                        fontFamily: 'monospace',
                        fontSize: '0.8rem'
                      }}
                    >
                      {selectedOid.id}
                    </Typography>
                  </Box>
                </Box>
                
                {/* Enhanced Information List */}
                <List sx={{ '& .MuiListItem-root': { px: 0 } }}>
                  <ListItem>
                    <ListItemIcon sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      <Assignment />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500 }}>
                          {isRTL ? 'الاسم' : 'Name'}
                        </Typography>
                      }
                      secondary={
                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          {selectedOid.name}
                        </Typography>
                      }
                    />
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      <Info />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500 }}>
                          {isRTL ? 'المعرف' : 'Identifier'}
                        </Typography>
                      }
                      secondary={
                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', fontFamily: 'monospace' }}>
                          {selectedOid.id}
                        </Typography>
                      }
                    />
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      {getTypeIcon(selectedOid.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500 }}>
                          {isRTL ? 'النوع' : 'Type'}
                        </Typography>
                      }
                      secondary={
                        <Chip
                          label={selectedOid.type}
                          size="small"
                          sx={{
                            backgroundColor: `${getTypeColor(selectedOid.type)}20`,
                            border: `1px solid ${getTypeColor(selectedOid.type)}40`,
                            color: getTypeColor(selectedOid.type),
                            mt: 0.5
                          }}
                        />
                      }
                    />
                  </ListItem>
                  
                  <ListItem>
                    <ListItemText
                      primary={
                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500 }}>
                          {isRTL ? 'الوصف' : 'Description'}
                        </Typography>
                      }
                      secondary={
                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: 1.6, mt: 1 }}>
                          {selectedOid.description}
                        </Typography>
                      }
                    />
                  </ListItem>
                  
                  {/* Real-time Performance Metrics */}
                  {viewMode === 'neural' && nodeMetrics.get(selectedOid.id) && (
                    <>
                      <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
                      <ListItem>
                        <ListItemIcon sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          <TrendingUp />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 500 }}>
                              {isRTL ? 'مقاييس الأداء' : 'Performance Metrics'}
                            </Typography>
                          }
                          secondary={
                            <Box mt={1}>
                              <Box display="flex" justifyContent="space-between" mb={1}>
                                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                                  {isRTL ? 'الأداء' : 'Performance'}
                                </Typography>
                                <Typography variant="caption" sx={{ color: '#00e676' }}>
                                  {Math.round(nodeMetrics.get(selectedOid.id).performance)}%
                                </Typography>
                              </Box>
                              <LinearProgress 
                                variant="determinate" 
                                value={nodeMetrics.get(selectedOid.id).performance}
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                  '& .MuiLinearProgress-bar': {
                                    backgroundColor: '#00e676',
                                    borderRadius: 3
                                  }
                                }}
                              />
                              
                              <Box display="flex" justifyContent="space-between" mt={2} mb={1}>
                                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                                  {isRTL ? 'وقت التشغيل' : 'Uptime'}
                                </Typography>
                                <Typography variant="caption" sx={{ color: '#00b4d8' }}>
                                  {Math.round(nodeMetrics.get(selectedOid.id).uptime)}%
                                </Typography>
                              </Box>
                              <LinearProgress 
                                variant="determinate" 
                                value={nodeMetrics.get(selectedOid.id).uptime}
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                  '& .MuiLinearProgress-bar': {
                                    backgroundColor: '#00b4d8',
                                    borderRadius: 3
                                  }
                                }}
                              />
                              
                              <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                                  {isRTL ? 'الاتصالات' : 'Connections'}
                                </Typography>
                                <Chip
                                  label={nodeMetrics.get(selectedOid.id).connections}
                                  size="small"
                                  sx={{
                                    backgroundColor: 'rgba(108, 92, 231, 0.2)',
                                    border: '1px solid rgba(108, 92, 231, 0.4)',
                                    color: '#6c5ce7',
                                    fontSize: '0.7rem'
                                  }}
                                />
                              </Box>
                            </Box>
                          }
                        />
                      </ListItem>
                    </>
                  )}
                </List>
                
                {/* Enhanced Action Buttons */}
                <Box mt={3} display="flex" gap={1.5}>
                  <Button
                    variant="outlined"
                    startIcon={<Edit />}
                    fullWidth
                    className="neural-btn"
                    sx={{
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      color: 'rgba(255, 255, 255, 0.9)',
                      '&:hover': {
                        backgroundColor: 'rgba(99, 102, 241, 0.2)',
                        border: '1px solid rgba(99, 102, 241, 0.4)',
                        transform: 'translateY(-1px)'
                      }
                    }}
                  >
                    {isRTL ? 'تعديل' : 'Edit'}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    startIcon={<Delete />}
                    fullWidth
                    className="neural-btn"
                    sx={{
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#ef4444',
                      '&:hover': {
                        backgroundColor: 'rgba(239, 68, 68, 0.2)',
                        border: '1px solid rgba(239, 68, 68, 0.5)',
                        transform: 'translateY(-1px)'
                      }
                    }}
                  >
                    {isRTL ? 'حذف' : 'Delete'}
                  </Button>
                </Box>
                
                {/* Emergency Actions for Critical Nodes */}
                {selectedOid.type === 'system' && (
                  <Box mt={2}>
                    <Button
                      variant="contained"
                      startIcon={<Emergency />}
                      fullWidth
                      className="neural-emergency-alert"
                      sx={{
                        background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.3) 0%, rgba(220, 38, 127, 0.2) 100%)',
                        border: '2px solid rgba(239, 68, 68, 0.5)',
                        color: '#ffffff',
                        fontWeight: 600,
                        '&:hover': {
                          background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.4) 0%, rgba(220, 38, 127, 0.3) 100%)',
                          transform: 'scale(1.02)'
                        }
                      }}
                    >
                      {isRTL ? 'وضع الطوارئ' : 'Emergency Mode'}
                    </Button>
                  </Box>
                )}
              </Box>
            ) : (
              <Box 
                display="flex" 
                flexDirection="column" 
                alignItems="center" 
                justifyContent="center" 
                height="60%"
                sx={{ opacity: 0.7 }}
              >
                <Psychology sx={{ fontSize: 64, color: 'rgba(255, 255, 255, 0.3)', mb: 2 }} />
                <Typography 
                  variant="h6" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.6)',
                    fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)',
                    textAlign: 'center',
                    mb: 1
                  }}
                >
                  {isRTL ? 'اختر معرف لعرض التفاصيل' : 'Select an OID to view details'}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.5)',
                    textAlign: 'center',
                    maxWidth: 250
                  }}
                >
                  {isRTL 
                    ? 'انقر على أي عقدة في الشجرة لعرض تفاصيلها ومقاييس الأداء'
                    : 'Click on any node in the tree to view its details and performance metrics'}
                </Typography>
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>
      
      {/* Floating Speed Dial for Quick Actions */}
      <SpeedDial
        ariaLabel="Neural OID Actions"
        sx={{ 
          position: 'fixed', 
          bottom: 24, 
          right: isRTL ? 'auto' : 24,
          left: isRTL ? 24 : 'auto',
          zIndex: 1000
        }}
        icon={<SpeedDialIcon />}
        FabProps={{
          sx: {
            background: 'var(--gradient-neural-primary)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            '&:hover': {
              background: 'var(--gradient-neural-secondary)',
              transform: 'scale(1.1)'
            }
          }
        }}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle={isRTL ? 'إضافة معرف' : 'Add OID'}
          onClick={handleAddOid}
          FabProps={{
            sx: {
              backgroundColor: 'rgba(0, 230, 118, 0.2)',
              border: '1px solid rgba(0, 230, 118, 0.4)',
              color: '#00e676',
              backdropFilter: 'blur(8px)'
            }
          }}
        />
        <SpeedDialAction
          icon={<Refresh />}
          tooltipTitle={isRTL ? 'تحديث' : 'Refresh'}
          onClick={handleRefresh}
          FabProps={{
            sx: {
              backgroundColor: 'rgba(14, 165, 233, 0.2)',
              border: '1px solid rgba(14, 165, 233, 0.4)',
              color: '#0ea5e9',
              backdropFilter: 'blur(8px)'
            }
          }}
        />
        <SpeedDialAction
          icon={<Science />}
          tooltipTitle={isRTL ? 'تحليل الشبكة' : 'Network Analysis'}
          onClick={() => setViewMode('neural')}
          FabProps={{
            sx: {
              backgroundColor: 'rgba(156, 136, 255, 0.2)',
              border: '1px solid rgba(156, 136, 255, 0.4)',
              color: '#9c88ff',
              backdropFilter: 'blur(8px)'
            }
          }}
        />
        <SpeedDialAction
          icon={<HealthAndSafety />}
          tooltipTitle={isRTL ? 'فحص الصحة' : 'Health Check'}
          onClick={() => {
            // Implement health check functionality
            console.log('Health check triggered');
          }}
          FabProps={{
            sx: {
              backgroundColor: 'rgba(245, 158, 11, 0.2)',
              border: '1px solid rgba(245, 158, 11, 0.4)',
              color: '#f59e0b',
              backdropFilter: 'blur(8px)'
            }
          }}
        />
      </SpeedDial>

      {/* Revolutionary Add OID Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          className: 'neural-glass-immersive',
          sx: {
            background: 'var(--gradient-neural-primary)',
            backdropFilter: 'blur(32px) saturate(150%)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '24px'
          }
        }}
      >
        <DialogTitle
          sx={{
            color: 'rgba(255, 255, 255, 0.95)',
            fontWeight: 600,
            fontSize: '1.5rem',
            fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)',
            textAlign: isRTL ? 'right' : 'left'
          }}
        >
          {isRTL ? 'إضافة معرف ذكي جديد' : 'Add New Intelligent OID'}
        </DialogTitle>
        <DialogContent sx={{ p: 3 }}>
          <Box display="flex" flexDirection="column" gap={3}>
            <TextField
              autoFocus
              label={isRTL ? 'الاسم' : 'Name'}
              fullWidth
              variant="outlined"
              value={newOidData.name}
              onChange={(e) => setNewOidData({ ...newOidData, name: e.target.value })}
              className="neural-input"
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '12px',
                  '&:hover': {
                    border: '1px solid rgba(14, 165, 233, 0.3)'
                  },
                  '&.Mui-focused': {
                    border: '1px solid rgba(14, 165, 233, 0.5)',
                    boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.2)'
                  }
                },
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
                },
                '& .MuiOutlinedInput-input': {
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
                }
              }}
            />
            
            <TextField
              label={isRTL ? 'الوصف' : 'Description'}
              fullWidth
              variant="outlined"
              multiline
              rows={4}
              value={newOidData.description}
              onChange={(e) => setNewOidData({ ...newOidData, description: e.target.value })}
              className="neural-input"
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '12px',
                  '&:hover': {
                    border: '1px solid rgba(14, 165, 233, 0.3)'
                  },
                  '&.Mui-focused': {
                    border: '1px solid rgba(14, 165, 233, 0.5)',
                    boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.2)'
                  }
                },
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)'
                },
                '& .MuiOutlinedInput-input': {
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)',
                  lineHeight: 1.6
                }
              }}
            />
            
            {/* Advanced Neural Analysis Preview */}
            {viewMode === 'neural' && newOidData.name && (
              <Box 
                className="neural-biometric-monitor"
                sx={{ p: 2, borderRadius: '12px' }}
              >
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}
                >
                  {isRTL ? 'تحليل الشبكة العصبية' : 'Neural Network Analysis'}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" mt={1}>
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                    {isRTL ? 'التوافق المتوقع' : 'Predicted Compatibility'}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#00e676' }}>
                    {Math.round(85 + Math.random() * 10)}%
                  </Typography>
                </Box>
                
                <LinearProgress 
                  variant="determinate" 
                  value={85 + Math.random() * 10}
                  sx={{
                    mt: 1,
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#00e676',
                      borderRadius: 2
                    }
                  }}
                />
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, gap: 1 }}>
          <Button 
            onClick={() => setDialogOpen(false)}
            className="neural-btn"
            sx={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              color: 'rgba(255, 255, 255, 0.8)',
              fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)'
              }
            }}
          >
            {isRTL ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button 
            onClick={handleSaveOid} 
            variant="contained"
            className="neural-btn"
            sx={{
              background: 'var(--gradient-neural-healthcare)',
              border: '1px solid rgba(0, 168, 107, 0.4)',
              color: '#ffffff',
              fontWeight: 600,
              fontFamily: isRTL ? 'var(--font-arabic)' : 'var(--font-english)',
              '&:hover': {
                background: 'linear-gradient(135deg, rgba(0, 168, 107, 0.3) 0%, rgba(0, 200, 150, 0.25) 100%)',
                transform: 'translateY(-1px)',
                boxShadow: '0 8px 24px rgba(0, 168, 107, 0.3)'
              }
            }}
          >
            {isRTL ? 'حفظ وتحليل' : 'Save & Analyze'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OidTree;
