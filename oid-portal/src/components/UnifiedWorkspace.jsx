/**
 * Unified Workspace - ULTRATHINK CONSOLIDATION
 * Single entry point for all healthcare dashboard functionality
 * Replaces multiple competing workspace implementations
 * 
 * This component serves as the main workspace that routes users to the
 * appropriate dashboard context based on their role and navigation
 */

import UnifiedHealthcareDashboard from './UnifiedHealthcareDashboard';

const UnifiedWorkspace = () => {
  return <UnifiedHealthcareDashboard />;
};

export default UnifiedWorkspace;