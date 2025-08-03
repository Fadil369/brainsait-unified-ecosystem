/**
 * Dashboard Components Index
 * Centralized exports for all dashboard modules
 */

import { lazy } from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { useLanguage } from '../../hooks/useLanguage';

// Real components
export { default as RealTimeMetrics } from './RealTimeMetrics';
export { default as HealthcareIdentityManagement } from './HealthcareIdentityManagement';

// Placeholder component for not-yet-implemented modules
const DashboardPlaceholder = ({ title, description, icon: Icon }) => {
  const { currentLanguage } = useLanguage();
  
  return (
    <Card>
      <CardContent>
        <Box display="flex" flexDirection="column" alignItems="center" py={4}>
          {Icon && <Icon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />}
          <Typography variant="h5" fontWeight="bold" mb={1}>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            {description || (currentLanguage === 'ar' 
              ? 'هذا القسم قيد التطوير وسيكون متاحاً قريباً'
              : 'This section is under development and will be available soon'
            )}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

// Lazy-loaded placeholder components (to be implemented)
export const NPHIESIntegration = lazy(() => 
  Promise.resolve({
    default: (props) => (
      <DashboardPlaceholder 
        title="NPHIES Integration"
        description="Saudi NPHIES platform integration and claims management"
        {...props}
      />
    )
  })
);

export const RCMAnalytics = lazy(() => 
  Promise.resolve({
    default: (props) => (
      <DashboardPlaceholder 
        title="Revenue Cycle Management"
        description="Healthcare revenue cycle analytics and optimization"
        {...props}
      />
    )
  })
);

export const TrainingPlatform = lazy(() => 
  Promise.resolve({
    default: (props) => (
      <DashboardPlaceholder 
        title="Training Platform"
        description="Medical coding certification and training programs"
        {...props}
      />
    )
  })
);

export const BOTProjects = lazy(() => 
  Promise.resolve({
    default: (props) => (
      <DashboardPlaceholder 
        title="BOT Projects"
        description="Build-Operate-Transfer project management"
        {...props}
      />
    )
  })
);

export const OperationsCenter = lazy(() => 
  Promise.resolve({
    default: (props) => (
      <DashboardPlaceholder 
        title="Operations Center"
        description="24/7 healthcare operations monitoring"
        {...props}
      />
    )
  })
);

export const AIAnalytics = lazy(() => 
  Promise.resolve({
    default: (props) => (
      <DashboardPlaceholder 
        title="AI Analytics"
        description="Artificial intelligence powered healthcare analytics"
        {...props}
      />
    )
  })
);