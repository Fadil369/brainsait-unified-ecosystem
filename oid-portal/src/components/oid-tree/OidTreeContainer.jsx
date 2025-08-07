/**
 * OidTreeContainer Component
 * Main container for the refactored OID Tree with modular architecture
 * Replaces the monolithic 1,126-line OidTree.jsx component
 */

import { useEffect, memo, Suspense } from 'react';
import { useLanguage } from '../../hooks/useLanguage';
import { useUnifiedHealthcare } from '../../contexts/UnifiedHealthcareContext';
import { useFHIR } from '../../hooks/useFHIR';
import { useOidTreeStore } from '../../stores/oid-tree-store';
import { createHealthcareOidTreeData } from '../../constants/healthcare-data';

// Lazy load components for better performance
const TreeControls = React.lazy(() => import('./TreeControls'));
const VirtualizedTreeNode = React.lazy(() => import('./VirtualizedTreeNode'));
const NodeDetailsPanel = React.lazy(() => import('./NodeDetailsPanel'));

// Loading component for lazy-loaded components
const ComponentLoader = memo(() => (
  <div className="animate-pulse p-4">
    <div className="h-8 bg-darker-bg rounded mb-4"></div>
    <div className="space-y-2">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="h-6 bg-darker-bg rounded"></div>
      ))}
    </div>
  </div>
));

ComponentLoader.displayName = 'ComponentLoader';

// FHIR Integration Status Component
const FHIRStatus = memo(({ fhirLoading, fhirError, currentLanguage }) => (
  <div className="mt-2 flex items-center gap-2">
    <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
      FHIR R4 {currentLanguage === 'ar' ? 'متكامل' : 'Integrated'}
    </span>
    {fhirLoading && (
      <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded animate-pulse">
        {currentLanguage === 'ar' ? 'مزامنة FHIR جارية...' : 'FHIR Syncing...'}
      </span>
    )}
    {fhirError && (
      <span className="text-xs px-2 py-1 bg-red-100 text-red-800 rounded">
        {currentLanguage === 'ar' ? 'خطأ FHIR' : 'FHIR Error'}
      </span>
    )}
  </div>
));

FHIRStatus.displayName = 'FHIRStatus';

// Main OID Tree Container
const OidTreeContainer = memo(() => {
  const { currentLanguage, isRTL } = useLanguage();
  const { 
    getCurrentUserRole, 
    trackHealthcareActivity 
  } = useUnifiedHealthcare();
  
  const { 
    isLoading: fhirLoading,
    error: fhirError 
  } = useFHIR();
  
  const {
    treeData,
    selectedNode,
    searchQuery,
    healthcareFilter,
    isLoading,
    error,
    setTreeData,
    setLoading,
    setError,
    selectNode,
    trackHealthcareActivity: storeTrackActivity
  } = useOidTreeStore();

  // Initialize healthcare context and load tree data
  useEffect(() => {
    const initializeOidTree = async () => {
      try {
        setLoading(true);
        
        // Initialize healthcare context and user role
        const role = await getCurrentUserRole();
        
        // Track healthcare activity
        await trackHealthcareActivity('oid_tree_accessed', {
          userRole: role,
          language: currentLanguage,
          timestamp: new Date().toISOString()
        });

        // Load tree data from backend API
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/oid-tree?language=${currentLanguage}`);
        
        if (response.ok) {
          const data = await response.json();
          setTreeData(data.tree_data);
        } else {
          // Fallback to static data if API fails
          console.warn('API unavailable, using static data');
          const healthcareTreeData = createHealthcareOidTreeData(currentLanguage);
          setTreeData(healthcareTreeData);
        }
        
      } catch (error) {
        console.error('Failed to initialize OID tree:', error);
        // Fallback to static data on any error
        const healthcareTreeData = createHealthcareOidTreeData(currentLanguage);
        setTreeData(healthcareTreeData);
      } finally {
        setLoading(false);
      }
    };

    initializeOidTree();
  }, [currentLanguage, getCurrentUserRole, trackHealthcareActivity, setTreeData, setLoading, setError]);

  // Enhanced node selection with FHIR sync
  const handleNodeSelect = async (node) => {
    selectNode(node);
    
    // Track healthcare node selection
    try {
      await storeTrackActivity('oid_node_selected', {
        nodeId: node.id,
        nodeOid: node.oid,
        healthcareCategory: node.healthcareCategory,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to track node selection:', error);
    }
  };

  // Error boundary fallback
  if (error) {
    return (
      <div className={`${isRTL ? 'rtl' : 'ltr'} p-6`} dir={isRTL ? 'rtl' : 'ltr'}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <h3 className="text-sm font-medium text-red-800">
              {currentLanguage === 'ar' ? 'خطأ في تحميل شجرة OID' : 'OID Tree Loading Error'}
            </h3>
          </div>
          <div className="mt-2">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${isRTL ? 'rtl' : 'ltr'} min-h-screen`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header Section */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-text-primary">
          {currentLanguage === 'ar' ? 'شجرة OID الصحية الموحدة' : 'Unified Healthcare OID Tree'}
        </h1>
        <p className="text-sm text-text-secondary mt-1">
          {currentLanguage === 'ar' 
            ? 'تصفح الهيكل الهرمي لمعرفات الكائنات المسجلة (OIDs) - منصة BrainSAIT الصحية الموحدة'
            : 'Browse the hierarchical structure of registered Object Identifiers (OIDs) - BrainSAIT Unified Healthcare Platform'
          }
          <span className="text-primary font-medium">
            {currentLanguage === 'ar' ? ' رقم المؤسسة 61026 (BrainSAIT المحدودة)' : ' Enterprise Number 61026 (Brainsait Ltd)'}
          </span>
        </p>
        
        {/* FHIR Integration Status */}
        <FHIRStatus 
          fhirLoading={fhirLoading} 
          fhirError={fhirError} 
          currentLanguage={currentLanguage} 
        />
        
        <div className="mt-2 text-xs text-text-secondary">
          {currentLanguage === 'ar' 
            ? 'يستند إلى بيانات سجل IANA الرسمية • آخر تحديث: أكتوبر 2023'
            : 'Based on official IANA registry data • Last updated: October 2023'
          }
        </div>
      </div>
      
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Tree Container - 2/3 width */}
        <div className="md:col-span-2">
          <div className="card overflow-hidden">
            {/* Tree Controls */}
            <Suspense fallback={<ComponentLoader />}>
              <TreeControls />
            </Suspense>
            
            {/* Virtualized Tree */}
            <div className="relative">
              {isLoading ? (
                <div className="p-4 animate-pulse space-y-4">
                  <div className={`text-center text-text-secondary ${currentLanguage === 'ar' ? 'text-right' : 'text-left'}`}>
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p>{currentLanguage === 'ar' ? 'جاري تحميل شجرة OID...' : 'Loading OID Tree...'}</p>
                  </div>
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <div className={`w-5 h-5 bg-darker-bg rounded ${isRTL ? 'ml-2' : 'mr-2'}`}></div>
                      <div className="flex-1">
                        <div className="h-4 bg-darker-bg rounded w-2/3 mb-1"></div>
                        <div className="h-3 bg-darker-bg rounded w-1/3"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <Suspense fallback={<ComponentLoader />}>
                  <VirtualizedTreeNode
                    treeData={treeData}
                    height={600}
                    itemHeight={80}
                    searchQuery={searchQuery}
                    healthcareFilter={healthcareFilter}
                    onNodeSelect={handleNodeSelect}
                  />
                </Suspense>
              )}
            </div>
          </div>
        </div>
        
        {/* Node Details Panel - 1/3 width */}
        <div className="md:col-span-1">
          <Suspense fallback={<ComponentLoader />}>
            <NodeDetailsPanel selectedNode={selectedNode} />
          </Suspense>
        </div>
      </div>
    </div>
  );
});

OidTreeContainer.displayName = 'OidTreeContainer';

export default OidTreeContainer;