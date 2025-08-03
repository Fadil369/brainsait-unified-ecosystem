/**
 * TreeNodeRenderer Component
 * Optimized renderer for individual tree nodes with healthcare-specific features
 */

import { memo, useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../hooks/useLanguage';
import { useUnifiedHealthcare } from '../../contexts/UnifiedHealthcareContext';
import { useCommunication } from '../../hooks/useCommunication';
import CommunicationStatusIndicator from '../communication/CommunicationStatusIndicator';
import CommunicationActionMenu from '../communication/CommunicationActionMenu';

// Enhanced Healthcare category icons with improved medical symbolism
const HealthcareCategoryIcon = memo(({ category, priority = 'normal', isActive = false }) => {
  const iconClass = `h-4 w-4 transition-all duration-200 ${isActive ? 'scale-110' : ''}`;
  const glowClass = priority === 'critical' ? 'drop-shadow-sm' : '';
  
  switch (category) {
    case 'medical':
      return (
        <svg className={`${iconClass} ${glowClass} text-red-500 hover:text-red-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C13.1 2 14 2.9 14 4V6H16C17.1 6 18 6.9 18 8V10C18 11.1 17.1 12 16 12H14V14C14 15.1 13.1 16 12 16C10.9 16 10 15.1 10 14V12H8C6.9 12 6 11.1 6 10V8C6 6.9 6.9 6 8 6H10V4C10 2.9 10.9 2 12 2Z" />
          <circle cx="12" cy="19" r="3" fill="currentColor" opacity="0.6" />
        </svg>
      );
    case 'administrative':
      return (
        <svg className={`${iconClass} ${glowClass} text-blue-500 hover:text-blue-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M4 4C4 2.9 4.9 2 6 2H18C19.1 2 20 2.9 20 4V20C20 21.1 19.1 22 18 22H6C4.9 22 4 21.1 4 20V4ZM6 4V20H18V4H6ZM8 6H16V8H8V6ZM8 10H16V12H8V10ZM8 14H13V16H8V14Z" />
          <circle cx="19" cy="5" r="2" fill="var(--healthcare-info)" opacity="0.8" />
        </svg>
      );
    case 'patient':
      return (
        <svg className={`${iconClass} ${glowClass} text-green-500 hover:text-green-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 4.5C14.8 4.4 14.6 4.4 14.4 4.5L9 7V9C9 9.6 9.4 10 10 10S11 9.6 11 9V8.5L12 8L13 8.5V9C13 9.6 13.4 10 14 10S15 9.6 15 9ZM12 7C12.6 7 13 7.4 13 8S12.6 9 12 9S11 8.6 11 8S11.4 7 12 7Z" />
          <path d="M12 10C15.87 10 19 13.13 19 17V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V17C5 13.13 8.13 10 12 10Z" opacity="0.7" />
          <circle cx="18" cy="7" r="1.5" fill="var(--healthcare-success)" />
        </svg>
      );
    case 'security':
      return (
        <svg className={`${iconClass} text-red-600`} fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    case 'department':
      return (
        <svg className={`${iconClass} ${glowClass} text-purple-500 hover:text-purple-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2L2 7L12 12L22 7L12 2ZM2 17L12 22L22 17M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="20" cy="5" r="2" fill="var(--healthcare-secondary)" opacity="0.9" />
        </svg>
      );
    case 'service':
      return (
        <svg className={`${iconClass} ${glowClass} text-indigo-500 hover:text-indigo-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM18.4 7.6C19.2 8.4 19.2 9.6 18.4 10.4L17 9L15.6 10.4C14.8 9.6 14.8 8.4 15.6 7.6C16.4 6.8 17.6 6.8 18.4 7.6ZM8.4 7.6C9.2 6.8 10.4 6.8 11.2 7.6C12 8.4 12 9.6 11.2 10.4L9.8 9L8.4 10.4C7.6 9.6 7.6 8.4 8.4 7.6Z" />
          <circle cx="12" cy="16" r="4" stroke="currentColor" strokeWidth="2" fill="none" />
          <path d="M10 16L12 18L14 16" stroke="currentColor" strokeWidth="2" fill="none" />
        </svg>
      );
    default:
      return (
        <svg className={`${iconClass} text-gray-500`} fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
        </svg>
      );
  }
});

HealthcareCategoryIcon.displayName = 'HealthcareCategoryIcon';

// Badge type color mapping
const getBadgeTypeColor = (badgeType) => {
  const colorMap = {
    service: 'bg-blue-500',
    department: 'bg-green-500',
    credential: 'bg-purple-500',
    security: 'bg-red-500',
    platform: 'bg-indigo-500',
    identifier: 'bg-orange-500',
    geographic: 'bg-teal-500'
  };
  return colorMap[badgeType] || 'bg-gray-500';
};

// Badge status color mapping
const getBadgeStatusColor = (status) => {
  const statusMap = {
    active: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    revoked: 'bg-red-100 text-red-800',
    expired: 'bg-gray-100 text-gray-800'
  };
  return statusMap[status] || 'bg-blue-100 text-blue-800';
};

// Compliance badges component
const ComplianceBadges = memo(({ node, currentLanguage }) => (
  <div className="flex items-center gap-1 mt-1 flex-wrap">
    {node.nphiesCompliant && (
      <span className="px-1 py-0.5 text-xs bg-green-100 text-green-800 rounded">
        {currentLanguage === 'ar' ? 'نفيس' : 'NPHIES'}
      </span>
    )}
    {node.fhirCompliant && (
      <span className="px-1 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">
        FHIR
      </span>
    )}
    {node.aiEnabled && (
      <span className="px-1 py-0.5 text-xs bg-purple-100 text-purple-800 rounded">
        {currentLanguage === 'ar' ? 'ذكي' : 'AI'}
      </span>
    )}
    {node.voiceEnabled && (
      <span className="px-1 py-0.5 text-xs bg-indigo-100 text-indigo-800 rounded">
        {currentLanguage === 'ar' ? 'صوتي' : 'Voice'}
      </span>
    )}
    {node.hipaaCompliant && (
      <span className="px-1 py-0.5 text-xs bg-red-100 text-red-800 rounded">
        HIPAA
      </span>
    )}
  </div>
));

ComplianceBadges.displayName = 'ComplianceBadges';

export const TreeNodeRenderer = memo(({ 
  node, 
  level, 
  hasChildren,
  isExpanded,
  selectedNode,
  onToggleNode,
  onSelectNode
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const { checkHealthcarePermissions } = useUnifiedHealthcare();
  const { 
    connectionStatus, 
    activeConnections, 
    getCommunicationPreferences 
  } = useCommunication();
  
  const isSelected = selectedNode && selectedNode.id === node.id;
  const isLeaf = !hasChildren;
  
  // Communication menu state
  const [contextMenuAnchor, setContextMenuAnchor] = useState(null);
  const [communicationPreferences, setCommunicationPreferences] = useState(null);
  
  // Memoized click handlers
  const handleToggle = useCallback((e) => {
    e.stopPropagation();
    if (hasChildren) {
      onToggleNode(node.id);
    }
  }, [hasChildren, onToggleNode, node.id]);
  
  const handleSelect = useCallback(() => {
    onSelectNode(node);
  }, [onSelectNode, node]);
  
  // Handle right-click for communication menu
  const handleContextMenu = useCallback((e) => {
    // Only show communication menu for patient/provider nodes
    if (node.healthcareCategory === 'patient' || 
        node.entityType === 'provider' ||
        node.patient_id ||
        node.phone_number) {
      e.preventDefault();
      setContextMenuAnchor(e.currentTarget);
      
      // Load communication preferences if available
      if (node.patient_id || node.national_id) {
        getCommunicationPreferences(node.patient_id || node.national_id)
          .then(prefs => setCommunicationPreferences(prefs))
          .catch(err => console.warn('Failed to load communication preferences:', err));
      }
    }
  }, [node, getCommunicationPreferences]);
  
  // Handle communication actions
  const handleCommunicationAction = useCallback((actionData) => {
    console.log('Communication action triggered:', actionData);
    // This could be expanded to handle specific actions
  }, []);
  
  // Close context menu
  const handleContextMenuClose = useCallback(() => {
    setContextMenuAnchor(null);
  }, []);
  
  // Get active connections for this node
  const nodeActiveConnections = Array.from(activeConnections.values()).filter(
    conn => conn.patientId === node.patient_id || 
            conn.patientId === node.national_id ||
            conn.patientId === node.nphies_id
  );
  
  // Get communication status for this node
  const nodeCommStatus = connectionStatus[node.patient_id] || 
                        connectionStatus[node.national_id] || 
                        connectionStatus[node.nphies_id] || 
                        {};
  
  return (
    <div className="tree-node">
      <div 
        className={`flex items-center py-2 px-3 rounded-md transition-colors hover:bg-content-bg cursor-pointer ${
          isSelected ? 'bg-primary bg-opacity-20' : ''
        } ${isRTL ? 'flex-row-reverse' : ''}`}
        style={{ 
          [isRTL ? 'paddingRight' : 'paddingLeft']: `${(level * 20) + 8}px` 
        }}
        onClick={handleSelect}
        onContextMenu={handleContextMenu}
      >
        {/* Expand/Collapse Toggle */}
        {hasChildren ? (
          <button 
            onClick={handleToggle}
            className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'} flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors`}
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? (
              <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </button>
        ) : (
          <div className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'}`} />
        )}
        
        {/* Node Icon */}
        <div className={`flex items-center ${isRTL ? 'ml-2' : 'mr-2'}`}>
          {isLeaf ? (
            <div className={`h-3 w-3 rounded-full ${getBadgeTypeColor(node.badgeType)}`} />
          ) : (
            <div className="flex items-center">
              {node.healthcareCategory && <HealthcareCategoryIcon category={node.healthcareCategory} />}
              <div className={`h-3 w-3 rounded-sm ml-1 ${
                node.id === 'brainsait-ltd' ? 'bg-gradient-to-r from-blue-500 to-purple-500' :
                node.oid?.startsWith('1.3.6.1.4.1.61026') ? 'bg-blue-600' :
                'bg-gray-500'
              }`} />
            </div>
          )}
        </div>
        
        {/* Node Content */}
        <div className={`flex-1 min-w-0 ${isRTL ? 'text-right' : 'text-left'}`}>
          <div className="text-sm font-medium text-text-primary truncate" dir={isRTL ? 'rtl' : 'ltr'}>
            {node.name}
          </div>
          <div className="text-xs text-text-secondary">{node.oid}</div>
          {node.description && (
            <div className="text-xs text-text-secondary italic mt-0.5 truncate" dir={isRTL ? 'rtl' : 'ltr'}>
              {node.description}
            </div>
          )}
          
          {/* Compliance Badges */}
          <ComplianceBadges node={node} currentLanguage={currentLanguage} />
          
          {/* Communication Status Indicators */}
          {(node.healthcareCategory === 'patient' || node.entityType === 'provider' || node.patient_id || node.phone_number) && (
            <CommunicationStatusIndicator
              nodeData={node}
              communicationStatus={nodeCommStatus}
              activeConnections={nodeActiveConnections}
              preferences={communicationPreferences}
              onCommunicationAction={handleCommunicationAction}
              compact={true}
              showPreferences={isSelected}
            />
          )}
        </div>
        
        {/* Organization Badge */}
        {node.organization && (
          <div className={`${isRTL ? 'mr-3' : 'ml-3'} flex-shrink-0`}>
            <span className="bg-blue-100 text-blue-800 px-1.5 py-0.5 text-xs rounded">
              {node.organization}
            </span>
          </div>
        )}
        
        {/* Status Badge */}
        {node.status && (
          <div className={`${isRTL ? 'mr-3' : 'ml-3'} flex-shrink-0`}>
            <span className={`px-2 py-0.5 text-xs rounded-full ${getBadgeStatusColor(node.status)}`}>
              {node.status}
            </span>
          </div>
        )}
        
        {/* Edit Link */}
        {node.badgeType && checkHealthcarePermissions && checkHealthcarePermissions('edit_badges') && (
          <Link 
            to={`/edit/${node.oid}`} 
            className={`${isRTL ? 'mr-3' : 'ml-3'} text-primary hover:text-primary-light text-sm flex-shrink-0`}
            onClick={(e) => e.stopPropagation()}
          >
            {currentLanguage === 'ar' ? 'تحرير' : 'Edit'}
          </Link>
        )}
      </div>
      
      {/* Communication Context Menu */}
      <CommunicationActionMenu
        anchorEl={contextMenuAnchor}
        open={Boolean(contextMenuAnchor)}
        onClose={handleContextMenuClose}
        nodeData={node}
        onCommunicationAction={handleCommunicationAction}
      />
    </div>
  );
});

TreeNodeRenderer.displayName = 'TreeNodeRenderer';