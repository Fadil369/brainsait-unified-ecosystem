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
} from '@mui/icons-material';
import {
    Alert,
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
    Paper,
    TextField,
    Tooltip,
    Typography,
} from '@mui/material';
import { useState } from 'react';
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
    switch (type) {
      case 'root':
        return <AccountTree color="primary" />;
      case 'provider':
        return <LocalHospital color="secondary" />;
      case 'organization':
        return <Business color="info" />;
      case 'device_category':
      case 'device':
        return <DeviceHub color="warning" />;
      case 'person':
        return <Person color="success" />;
      case 'system':
      case 'ai_services':
        return <Security color="error" />;
      default:
        return <Assignment />;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'root': return 'primary';
      case 'provider': return 'secondary';
      case 'organization': return 'info';
      case 'device_category':
      case 'device': return 'warning';
      case 'person': return 'success';
      case 'system':
      case 'ai_services': return 'error';
      default: return 'default';
    }
  };

  const renderOidNode = (node, level = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const hasChildren = node.children && node.children.length > 0;

    return (
      <Box key={node.id}>
        <Card 
          sx={{ 
            mb: 1, 
            ml: level * 2,
            bgcolor: selectedOid?.id === node.id ? 'action.selected' : 'background.paper',
            border: selectedOid?.id === node.id ? 2 : 1,
            borderColor: selectedOid?.id === node.id ? 'primary.main' : 'divider'
          }}
        >
          <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
            <Box display="flex" alignItems="center" gap={1}>
              {hasChildren && (
                <IconButton 
                  size="small" 
                  onClick={() => toggleExpand(node.id)}
                >
                  {isExpanded ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              )}
              
              {getTypeIcon(node.type)}
              
              <Box flexGrow={1} onClick={() => setSelectedOid(node)} sx={{ cursor: 'pointer' }}>
                <Typography variant="body1" fontWeight={500}>
                  {node.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {node.id}
                </Typography>
              </Box>
              
              <Chip 
                label={node.type} 
                size="small" 
                color={getTypeColor(node.type)}
                variant="outlined"
              />
              
              {node.status && (
                <Chip 
                  label={node.status} 
                  size="small" 
                  color={node.status === 'active' ? 'success' : 'default'}
                />
              )}
            </Box>
          </CardContent>
        </Card>

        {hasChildren && isExpanded && (
          <Box>
            {node.children.map(child => renderOidNode(child, level + 1))}
          </Box>
        )}
      </Box>
    );
  };

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
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            {isRTL ? 'شجرة المعرفات الطبية (OID)' : 'Healthcare OID Tree'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {isRTL ? 'إدارة وتنظيم معرفات النظام الصحي السعودي' : 'Manage Saudi Healthcare System Identifiers'}
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Tooltip title={isRTL ? 'تحديث' : 'Refresh'}>
            <IconButton onClick={handleRefresh} disabled={loading}>
              {loading ? <CircularProgress size={20} /> : <Refresh />}
            </IconButton>
          </Tooltip>
          
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddOid}
          >
            {isRTL ? 'إضافة معرف جديد' : 'Add New OID'}
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* OID Tree */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '70vh', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              {isRTL ? 'هيكل المعرفات' : 'OID Structure'}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {renderOidNode(oidTree)}
          </Paper>
        </Grid>

        {/* Details Panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '70vh' }}>
            <Typography variant="h6" gutterBottom>
              {isRTL ? 'تفاصيل المعرف' : 'OID Details'}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {selectedOid ? (
              <Box>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Assignment />
                    </ListItemIcon>
                    <ListItemText
                      primary={isRTL ? 'الاسم' : 'Name'}
                      secondary={selectedOid.name}
                    />
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon>
                      <Info />
                    </ListItemIcon>
                    <ListItemText
                      primary={isRTL ? 'المعرف' : 'Identifier'}
                      secondary={selectedOid.id}
                    />
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon>
                      {getTypeIcon(selectedOid.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={isRTL ? 'النوع' : 'Type'}
                      secondary={selectedOid.type}
                    />
                  </ListItem>
                  
                  <ListItem>
                    <ListItemText
                      primary={isRTL ? 'الوصف' : 'Description'}
                      secondary={selectedOid.description}
                    />
                  </ListItem>
                </List>
                
                <Box mt={2} display="flex" gap={1}>
                  <Button
                    variant="outlined"
                    startIcon={<Edit />}
                    size="small"
                    fullWidth
                  >
                    {isRTL ? 'تعديل' : 'Edit'}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<Delete />}
                    size="small"
                    fullWidth
                  >
                    {isRTL ? 'حذف' : 'Delete'}
                  </Button>
                </Box>
              </Box>
            ) : (
              <Alert severity="info">
                {isRTL ? 'اختر معرف لعرض التفاصيل' : 'Select an OID to view details'}
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Add OID Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {isRTL ? 'إضافة معرف جديد' : 'Add New OID'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label={isRTL ? 'الاسم' : 'Name'}
            fullWidth
            variant="outlined"
            value={newOidData.name}
            onChange={(e) => setNewOidData({ ...newOidData, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label={isRTL ? 'الوصف' : 'Description'}
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={newOidData.description}
            onChange={(e) => setNewOidData({ ...newOidData, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            {isRTL ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button onClick={handleSaveOid} variant="contained">
            {isRTL ? 'حفظ' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OidTree;
