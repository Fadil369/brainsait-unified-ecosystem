/**
 * NodeDetailsPanel Component
 * Detailed information panel for selected OID nodes with healthcare-specific data
 */

import { memo, useMemo, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../hooks/useLanguage';
import { useUnifiedHealthcare } from '../../contexts/UnifiedHealthcareContext';
import { useCommunication } from '../../hooks/useCommunication';
import CommunicationStatusIndicator from '../communication/CommunicationStatusIndicator';
import CommunicationPreferencesManager from '../communication/CommunicationPreferencesManager';
import CommunicationActionMenu from '../communication/CommunicationActionMenu';

const DetailField = memo(({ label, value, isRTL, dir }) => {
  if (!value) return null;
  
  return (
    <div>
      <h4 className="text-xs uppercase text-text-secondary mb-1">
        {label}
      </h4>
      <p className={`text-sm text-text-primary ${isRTL ? 'text-right' : 'text-left'}`} dir={dir}>
        {value}
      </p>
    </div>
  );
});

DetailField.displayName = 'DetailField';

const ComplianceIndicators = memo(({ node, currentLanguage }) => {
  const indicators = useMemo(() => {
    const items = [];
    
    if (node.nphiesCompliant) {
      items.push({
        key: 'nphies',
        label: currentLanguage === 'ar' ? 'متوافق مع نفيس' : 'NPHIES Compliant',
        className: 'bg-green-100 text-green-800'
      });
    }
    
    if (node.fhirCompliant) {
      items.push({
        key: 'fhir',
        label: currentLanguage === 'ar' ? 'متوافق مع FHIR' : 'FHIR Compliant',
        className: 'bg-blue-100 text-blue-800'
      });
    }
    
    if (node.hipaaCompliant) {
      items.push({
        key: 'hipaa',
        label: currentLanguage === 'ar' ? 'متوافق مع HIPAA' : 'HIPAA Compliant',
        className: 'bg-purple-100 text-purple-800'
      });
    }
    
    return items;
  }, [node, currentLanguage]);

  if (indicators.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {indicators.map((indicator) => (
        <span key={indicator.key} className={`text-xs px-2 py-1 rounded ${indicator.className}`}>
          {indicator.label}
        </span>
      ))}
    </div>
  );
});

ComplianceIndicators.displayName = 'ComplianceIndicators';

const BadgeInformation = memo(({ node, currentLanguage, isRTL }) => {
  const badgeFields = useMemo(() => [
    {
      label: currentLanguage === 'ar' ? 'نوع الكيان' : 'Entity Type',
      value: node.entityType ? (currentLanguage === 'ar' ? node.entityType_ar : node.entityType) : null
    },
    {
      label: currentLanguage === 'ar' ? 'المنظمة' : 'Organization',
      value: node.organization ? (currentLanguage === 'ar' ? node.organization_ar : node.organization) : null
    },
    {
      label: currentLanguage === 'ar' ? 'القسم' : 'Department', 
      value: node.department ? (currentLanguage === 'ar' ? node.department_ar : node.department) : null
    },
    {
      label: currentLanguage === 'ar' ? 'الدور' : 'Role',
      value: node.role ? (currentLanguage === 'ar' ? node.role_ar : node.role) : null
    },
    {
      label: currentLanguage === 'ar' ? 'مستوى الوصول' : 'Access Level',
      value: node.accessLevel
    },
    {
      label: currentLanguage === 'ar' ? 'الهوية الوطنية' : 'National ID',
      value: node.nationalId
    },
    {
      label: currentLanguage === 'ar' ? 'معرف نفيس' : 'NPHIES ID',
      value: node.nphiesId
    }
  ], [node, currentLanguage]);

  return (
    <div className="space-y-3 mb-4">
      <h3 className="text-sm font-semibold text-text-primary border-b border-darker-bg pb-1">
        {currentLanguage === 'ar' ? 'معلومات الشارة' : 'Badge Information'}
      </h3>
      <div className="grid gap-3">
        {badgeFields.map((field, index) => (
          <DetailField
            key={index}
            label={field.label}
            value={field.value}
            isRTL={isRTL}
            dir={currentLanguage === 'ar' ? 'rtl' : 'ltr'}
          />
        ))}
      </div>
    </div>
  );
});

BadgeInformation.displayName = 'BadgeInformation';

const ExternalLinks = memo(({ node, currentLanguage }) => {
  const links = useMemo(() => {
    const linkArray = [];
    
    if (node.oid) {
      linkArray.push({
        url: `https://oid-info.com/get/${node.oid}`,
        label: currentLanguage === 'ar' ? 'معلومات OID الرسمية' : 'Official OID Info',
        external: true
      });
    }
    
    if (node.fhirResource) {
      linkArray.push({
        url: node.fhirResource,
        label: currentLanguage === 'ar' ? 'مورد FHIR' : 'FHIR Resource',
        external: true
      });
    }
    
    return linkArray;
  }, [node, currentLanguage]);

  if (links.length === 0) return null;

  return (
    <div className="mb-4">
      <h3 className="text-sm font-semibold text-text-primary border-b border-darker-bg pb-1 mb-2">
        {currentLanguage === 'ar' ? 'روابط خارجية' : 'External Links'}
      </h3>
      <div className="space-y-2">
        {links.map((link, index) => (
          <div key={index}>
            {link.external ? (
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:text-primary-light text-sm underline"
              >
                {link.label} ↗
              </a>
            ) : (
              <Link
                to={link.url}
                className="text-primary hover:text-primary-light text-sm underline"
              >
                {link.label}
              </Link>
            )}
          </div>
        ))}
      </div>
    </div>
  );
});

ExternalLinks.displayName = 'ExternalLinks';

const ActionButtons = memo(({ node, currentLanguage, checkHealthcarePermissions }) => {
  const canEdit = useMemo(() => checkHealthcarePermissions?.('edit', node.entityType), [checkHealthcarePermissions, node.entityType]);
  const canDelete = useMemo(() => checkHealthcarePermissions?.('delete', node.entityType), [checkHealthcarePermissions, node.entityType]);

  if (!canEdit && !canDelete) return null;

  return (
    <div className="flex gap-2 pt-4 border-t border-darker-bg">
      {canEdit && (
        <button className="px-3 py-1 bg-primary text-white text-xs rounded hover:bg-primary-dark transition-colors">
          {currentLanguage === 'ar' ? 'تحرير' : 'Edit'}
        </button>
      )}
      {canDelete && (
        <button className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors">
          {currentLanguage === 'ar' ? 'حذف' : 'Delete'}
        </button>
      )}
    </div>
  );
});

ActionButtons.displayName = 'ActionButtons';

const EmptyState = memo(({ currentLanguage }) => (
  <div className="text-center py-8">
    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-darker-bg flex items-center justify-center">
      <svg className="w-8 h-8 text-text-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <h3 className="text-lg font-medium text-text-primary mb-2">
      {currentLanguage === 'ar' ? 'لم يتم تحديد عقدة' : 'No Node Selected'}
    </h3>
    <p className="text-text-secondary text-sm">
      {currentLanguage === 'ar' 
        ? 'اختر عقدة من الشجرة لعرض تفاصيلها الطبية' 
        : 'Select a node from the tree to view its healthcare details'
      }
    </p>
  </div>
));

EmptyState.displayName = 'EmptyState';

const NodeDetailsPanel = memo(({ selectedNode }) => {
  const { currentLanguage, isRTL } = useLanguage();
  const { checkHealthcarePermissions } = useUnifiedHealthcare();
  const {
    connectionStatus,
    activeConnections,
    getCommunicationPreferences,
    getCommunicationHistory,
    sendMessage,
    initiateVoiceCall,
    initiateVideoConsultation
  } = useCommunication();
  
  // Communication state
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [communicationPreferences, setCommunicationPreferences] = useState(null);
  const [communicationHistory, setCommunicationHistory] = useState([]);
  const [isLoadingComm, setIsLoadingComm] = useState(false);

  // Load communication data when node changes
  const loadCommunicationData = useCallback(async () => {
    if (!selectedNode || !hasPatientData(selectedNode)) return;
    
    setIsLoadingComm(true);
    try {
      const patientId = selectedNode.patient_id || selectedNode.national_id || selectedNode.nphies_id;
      
      // Load preferences and history in parallel
      const [prefs, history] = await Promise.allSettled([
        getCommunicationPreferences(patientId),
        getCommunicationHistory(patientId, 10)
      ]);
      
      if (prefs.status === 'fulfilled') {
        setCommunicationPreferences(prefs.value);
      }
      
      if (history.status === 'fulfilled') {
        setCommunicationHistory(history.value.communications || []);
      }
    } catch (error) {
      console.warn('Failed to load communication data:', error);
    } finally {
      setIsLoadingComm(false);
    }
  }, [selectedNode, getCommunicationPreferences, getCommunicationHistory]);
  
  // Check if node has patient data
  const hasPatientData = useCallback((node) => {
    return node && (
      node.patient_id || 
      node.national_id || 
      node.nphies_id ||
      node.phone_number ||
      node.healthcareCategory === 'patient' ||
      node.entityType === 'provider'
    );
  }, []);
  
  // Handle communication actions
  const handleCommunicationAction = useCallback((actionData) => {
    switch (actionData.action) {
      case 'manage_preferences':
        loadCommunicationData();
        setPreferencesOpen(true);
        break;
      case 'view_history':
        loadCommunicationData();
        setHistoryOpen(true);
        break;
      default:
        console.log('Communication action:', actionData);
    }
  }, [loadCommunicationData]);
  
  if (!selectedNode) {
    return (
      <div className="card">
        <EmptyState currentLanguage={currentLanguage} />
      </div>
    );
  }

  return (
    <div className="card">
      <div className="p-4">
        {/* Header Section */}
        <div className="mb-4">
          <h2 className={`text-lg font-bold text-text-primary mb-1 ${isRTL ? 'text-right' : 'text-left'}`} dir={isRTL ? 'rtl' : 'ltr'}>
            {currentLanguage === 'ar' ? selectedNode.name_ar || selectedNode.name : selectedNode.name}
          </h2>
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <span className="font-mono bg-darker-bg px-2 py-1 rounded">
              {selectedNode.oid}
            </span>
            {selectedNode.status && (
              <span className={`px-2 py-1 rounded ${
                selectedNode.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {selectedNode.status}
              </span>
            )}
          </div>
          
          {/* Description */}
          {selectedNode.description && (
            <p className={`text-sm text-text-secondary mt-2 ${isRTL ? 'text-right' : 'text-left'}`} dir={isRTL ? 'rtl' : 'ltr'}>
              {currentLanguage === 'ar' ? selectedNode.description_ar || selectedNode.description : selectedNode.description}
            </p>
          )}
        </div>

        {/* Compliance Indicators */}
        <ComplianceIndicators node={selectedNode} currentLanguage={currentLanguage} />

        {/* Badge Information */}
        <BadgeInformation node={selectedNode} currentLanguage={currentLanguage} isRTL={isRTL} />

        {/* External Links */}
        <ExternalLinks node={selectedNode} currentLanguage={currentLanguage} />

        {/* Communication Section */}
        {hasPatientData(selectedNode) && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-text-primary border-b border-darker-bg pb-1 mb-3">
              {currentLanguage === 'ar' ? 'التواصل' : 'Communication'}
            </h3>
            
            {/* Communication Status */}
            <div className="mb-3">
              <CommunicationStatusIndicator
                nodeData={selectedNode}
                communicationStatus={connectionStatus}
                activeConnections={Array.from(activeConnections.values())}
                preferences={communicationPreferences}
                onCommunicationAction={handleCommunicationAction}
                compact={false}
                showPreferences={true}
              />
            </div>
            
            {/* Communication Actions */}
            <div className="grid grid-cols-2 gap-2">
              <button 
                className="px-3 py-2 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                onClick={() => handleCommunicationAction({ action: 'manage_preferences', nodeData: selectedNode })}
                disabled={isLoadingComm}
              >
                {currentLanguage === 'ar' ? 'إدارة التفضيلات' : 'Manage Preferences'}
              </button>
              
              <button 
                className="px-3 py-2 bg-green-600 text-white text-xs rounded hover:bg-green-700 transition-colors"
                onClick={() => handleCommunicationAction({ action: 'view_history', nodeData: selectedNode })}
                disabled={isLoadingComm}
              >
                {currentLanguage === 'ar' ? 'تاريخ التواصل' : 'Communication History'}
              </button>
            </div>
            
            {/* Recent Communication Activity */}
            {communicationHistory.length > 0 && (
              <div className="mt-3">
                <h4 className="text-xs font-medium text-text-secondary mb-2">
                  {currentLanguage === 'ar' ? 'النشاط الأخير' : 'Recent Activity'}
                </h4>
                <div className="space-y-1">
                  {communicationHistory.slice(0, 3).map((comm, index) => (
                    <div key={index} className="flex items-center justify-between text-xs bg-darker-bg p-2 rounded">
                      <span className="text-text-primary">
                        {comm.channel} - {comm.status}
                      </span>
                      <span className="text-text-secondary">
                        {new Date(comm.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Action Buttons */}
        <ActionButtons 
          node={selectedNode} 
          currentLanguage={currentLanguage} 
          checkHealthcarePermissions={checkHealthcarePermissions} 
        />

        {/* Performance & Status Indicators */}
        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <div className="performance-excellent" title={currentLanguage === 'ar' ? 'متصل ومتزامن' : 'Connected & Synced'}></div>
          <span className="text-xs text-clinical-text-tertiary">
            {currentLanguage === 'ar' ? 'آخر تحديث:' : 'Last updated:'} {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
      
      {/* Communication Preferences Dialog */}
      {hasPatientData(selectedNode) && (
        <CommunicationPreferencesManager
          open={preferencesOpen}
          onClose={() => setPreferencesOpen(false)}
          nodeData={selectedNode}
          initialPreferences={communicationPreferences || {}}
        />
      )}
    </div>
  );
});

NodeDetailsPanel.displayName = 'NodeDetailsPanel';

export default NodeDetailsPanel;