import {
    Alert,
    Box,
    CircularProgress,
    Paper,
    Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useLanguage } from '../hooks/useLanguage';

const EditBadge = () => {
  const { isRTL } = useLanguage();
  const { oid } = useParams();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {isRTL ? 'تعديل المعرف' : 'Edit Identity'}
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={4}>
        {isRTL ? `تعديل المعرف: ${oid}` : `Editing identifier: ${oid}`}
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Alert severity="info">
          {isRTL ? 'صفحة التعديل قيد التطوير' : 'Edit page under development'}
        </Alert>
      </Paper>
    </Box>
  );
};

export default EditBadge;
