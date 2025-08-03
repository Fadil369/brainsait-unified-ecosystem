/**
 * BrainSAIT Healthcare OID Tree Store
 * Zustand store for managing OID tree state with healthcare-specific optimizations
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { OidNode, TreeState, TreeActions, HealthcareCategory } from '../types/oid-tree';

// Communication types
interface CommunicationStatus {
  [patientId: string]: {
    [channel: string]: {
      status: string;
      lastUpdate: Date;
      messageCount?: number;
    }
  }
}

interface ActiveConnection {
  id: string;
  patientId: string;
  channel: string;
  status: string;
  startTime: Date;
  metadata?: any;
}

interface CommunicationPreferences {
  [patientId: string]: {
    preferred_language: string;
    consent_sms: boolean;
    consent_voice: boolean;
    consent_video: boolean;
    consent_email: boolean;
    consent_whatsapp: boolean;
    available_from?: string;
    available_until?: string;
    timezone?: string;
    emergency_contact_phone?: string;
    emergency_contact_name?: string;
  }
}

interface EmergencyAlert {
  id: string;
  patientId?: string;
  level: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  description_ar?: string;
  timestamp: Date;
  resolved: boolean;
}

interface OidTreeStore extends TreeState, TreeActions {
  // Performance optimizations
  flattenedNodes: Record<string, OidNode>;
  nodeDepthMap: Record<string, number>;
  searchableText: string;
  
  // Communication state
  communicationStatus: CommunicationStatus;
  activeConnections: Map<string, ActiveConnection>;
  communicationPreferences: CommunicationPreferences;
  emergencyAlerts: EmergencyAlert[];
  isWebSocketConnected: boolean;
  
  // Healthcare-specific actions
  syncWithFHIR: (node: OidNode) => Promise<void>;
  trackHealthcareActivity: (action: string, metadata?: any) => Promise<void>;
  filterByCompliance: (complianceType: string) => OidNode[];
  
  // Communication actions
  updateCommunicationStatus: (patientId: string, channel: string, status: string) => void;
  addActiveConnection: (connection: ActiveConnection) => void;
  removeActiveConnection: (connectionId: string) => void;
  updateCommunicationPreferences: (patientId: string, preferences: any) => void;
  addEmergencyAlert: (alert: EmergencyAlert) => void;
  resolveEmergencyAlert: (alertId: string) => void;
  setWebSocketConnected: (connected: boolean) => void;
  getPatientCommunicationData: (nodeId: string) => any;
  getNodesWithActiveEmergencies: () => OidNode[];
  
  // Performance actions
  buildFlatMap: () => void;
  buildSearchIndex: () => void;
  getVisibleNodes: () => OidNode[];
}

// Healthcare-specific constants
const HEALTHCARE_FILTERS = [
  { value: 'all' as const, label: { en: 'All', ar: 'الكل' } },
  { value: 'medical' as const, label: { en: 'Medical', ar: 'طبي' } },
  { value: 'administrative' as const, label: { en: 'Administrative', ar: 'إداري' } },
  { value: 'patient' as const, label: { en: 'Patient', ar: 'مريض' } },
  { value: 'department' as const, label: { en: 'Department', ar: 'قسم' } },
  { value: 'service' as const, label: { en: 'Service', ar: 'خدمة' } },
  { value: 'security' as const, label: { en: 'Security', ar: 'أمان' } }
];

// Utility functions for tree operations
const flattenTreeNodes = (node: OidNode, depth = 0): Record<string, OidNode> => {
  const flattened: Record<string, OidNode> = { [node.id]: { ...node, children: undefined } };
  
  if (node.children) {
    node.children.forEach(child => {
      Object.assign(flattened, flattenTreeNodes(child, depth + 1));
    });
  }
  
  return flattened;
};

const buildDepthMap = (node: OidNode, depth = 0): Record<string, number> => {
  const depthMap: Record<string, number> = { [node.id]: depth };
  
  if (node.children) {
    node.children.forEach(child => {
      Object.assign(depthMap, buildDepthMap(child, depth + 1));
    });
  }
  
  return depthMap;
};

const buildSearchableText = (node: OidNode): string => {
  let text = `${node.name} ${node.oid} ${node.description || ''} ${node.healthcareCategory || ''} ${node.organization || ''}`;
  
  if (node.children) {
    text += ' ' + node.children.map(buildSearchableText).join(' ');
  }
  
  return text.toLowerCase();
};

const filterTreeBySearch = (node: OidNode, query: string): boolean => {
  const searchText = buildSearchableText(node);
  return searchText.includes(query.toLowerCase());
};

const filterByHealthcareCategory = (node: OidNode, category: HealthcareCategory | 'all'): boolean => {
  if (category === 'all') return true;
  
  if (node.healthcareCategory === category) return true;
  
  if (node.children) {
    return node.children.some(child => filterByHealthcareCategory(child, category));
  }
  
  return false;
};

// Main Zustand store with performance optimizations
export const useOidTreeStore = create<OidTreeStore>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state
        treeData: null,
        expandedNodes: {},
        selectedNode: null,
        searchQuery: '',
        healthcareFilter: 'all',
        isLoading: false,
        error: null,
        flattenedNodes: {},
        nodeDepthMap: {},
        searchableText: '',
        
        // Communication state
        communicationStatus: {},
        activeConnections: new Map(),
        communicationPreferences: {},
        emergencyAlerts: [],
        isWebSocketConnected: false,

        // Basic actions
        setTreeData: (data: OidNode) => {
          set(state => {
            state.treeData = data;
            state.isLoading = false;
            state.error = null;
            
            // Build performance maps
            state.flattenedNodes = flattenTreeNodes(data);
            state.nodeDepthMap = buildDepthMap(data);
            state.searchableText = buildSearchableText(data);
            
            // Auto-expand critical healthcare nodes
            const criticalNodes = [
              'root', 'internet', 'dod', 'internet-directory', 'private', 
              'enterprise', 'brainsait-ltd', 'places', 'healthcare-services', 
              'medical-departments'
            ];
            
            criticalNodes.forEach(nodeId => {
              state.expandedNodes[nodeId] = true;
            });
          });
        },

        toggleNode: (nodeId: string) => {
          set(state => {
            state.expandedNodes[nodeId] = !state.expandedNodes[nodeId];
          });
        },

        selectNode: (node: OidNode | null) => {
          set(state => {
            state.selectedNode = node;
          });
          
          // Track healthcare activity
          if (node) {
            get().trackHealthcareActivity('oid_node_selected', {
              nodeId: node.id,
              nodeOid: node.oid,
              healthcareCategory: node.healthcareCategory
            });
          }
        },

        setSearchQuery: (query: string) => {
          set(state => {
            state.searchQuery = query;
          });
        },

        setHealthcareFilter: (filter: HealthcareCategory | 'all') => {
          set(state => {
            state.healthcareFilter = filter;
          });
        },

        setLoading: (loading: boolean) => {
          set(state => {
            state.isLoading = loading;
          });
        },

        setError: (error: string | null) => {
          set(state => {
            state.error = error;
          });
        },

        expandNode: (nodeId: string) => {
          set(state => {
            state.expandedNodes[nodeId] = true;
          });
        },

        collapseNode: (nodeId: string) => {
          set(state => {
            state.expandedNodes[nodeId] = false;
          });
        },

        expandAll: () => {
          const { flattenedNodes } = get();
          set(state => {
            Object.keys(flattenedNodes).forEach(nodeId => {
              state.expandedNodes[nodeId] = true;
            });
          });
        },

        collapseAll: () => {
          set(state => {
            state.expandedNodes = {};
          });
        },

        // Performance optimization methods
        buildFlatMap: () => {
          const { treeData } = get();
          if (treeData) {
            set(state => {
              state.flattenedNodes = flattenTreeNodes(treeData);
              state.nodeDepthMap = buildDepthMap(treeData);
            });
          }
        },

        buildSearchIndex: () => {
          const { treeData } = get();
          if (treeData) {
            set(state => {
              state.searchableText = buildSearchableText(treeData);
            });
          }
        },

        getVisibleNodes: () => {
          const { treeData, searchQuery, healthcareFilter } = get();
          if (!treeData) return [];

          const filterNode = (node: OidNode): OidNode | null => {
            // Apply search filter
            if (searchQuery && !filterTreeBySearch(node, searchQuery)) {
              return null;
            }

            // Apply healthcare category filter
            if (!filterByHealthcareCategory(node, healthcareFilter)) {
              return null;
            }

            // Recursively filter children
            const filteredChildren = node.children
              ?.map(child => filterNode(child))
              .filter(Boolean) as OidNode[] | undefined;

            return {
              ...node,
              children: filteredChildren
            };
          };

          const filteredTree = filterNode(treeData);
          return filteredTree ? [filteredTree] : [];
        },

        // Healthcare-specific methods
        syncWithFHIR: async (node: OidNode) => {
          try {
            // FHIR synchronization logic would go here
            // This is a placeholder for the actual FHIR integration
            console.log(`Syncing node ${node.oid} with FHIR`);
            
            await get().trackHealthcareActivity('fhir_sync', {
              nodeId: node.id,
              nodeOid: node.oid,
              syncType: 'organization'
            });
          } catch (error) {
            console.error('FHIR sync failed:', error);
            set(state => {
              state.error = `FHIR sync failed: ${error.message}`;
            });
          }
        },

        trackHealthcareActivity: async (action: string, metadata: any = {}) => {
          try {
            // Healthcare activity tracking logic
            const payload = {
              action,
              timestamp: new Date().toISOString(),
              ...metadata
            };
            
            console.log('Healthcare activity tracked:', payload);
            // In real implementation, this would send to analytics service
          } catch (error) {
            console.error('Failed to track healthcare activity:', error);
          }
        },

        filterByCompliance: (complianceType: string) => {
          const { flattenedNodes } = get();
          return Object.values(flattenedNodes).filter(node => {
            switch (complianceType) {
              case 'nphies':
                return node.nphiesCompliant;
              case 'fhir':
                return node.fhirCompliant;
              case 'hipaa':
                return node.hipaaCompliant;
              case 'ai':
                return node.aiEnabled;
              default:
                return false;
            }
          });
        },
        
        // Communication actions
        updateCommunicationStatus: (patientId: string, channel: string, status: string) => {
          set(state => {
            if (!state.communicationStatus[patientId]) {
              state.communicationStatus[patientId] = {};
            }
            state.communicationStatus[patientId][channel] = {
              status,
              lastUpdate: new Date(),
              messageCount: (state.communicationStatus[patientId][channel]?.messageCount || 0) + 1
            };
          });
        },
        
        addActiveConnection: (connection: ActiveConnection) => {
          set(state => {
            state.activeConnections.set(connection.id, connection);
          });
        },
        
        removeActiveConnection: (connectionId: string) => {
          set(state => {
            state.activeConnections.delete(connectionId);
          });
        },
        
        updateCommunicationPreferences: (patientId: string, preferences: any) => {
          set(state => {
            state.communicationPreferences[patientId] = {
              ...state.communicationPreferences[patientId],
              ...preferences
            };
          });
        },
        
        addEmergencyAlert: (alert: EmergencyAlert) => {
          set(state => {
            state.emergencyAlerts.unshift(alert);
            // Keep only last 50 alerts
            if (state.emergencyAlerts.length > 50) {
              state.emergencyAlerts = state.emergencyAlerts.slice(0, 50);
            }
          });
        },
        
        resolveEmergencyAlert: (alertId: string) => {
          set(state => {
            const alert = state.emergencyAlerts.find(a => a.id === alertId);
            if (alert) {
              alert.resolved = true;
            }
          });
        },
        
        setWebSocketConnected: (connected: boolean) => {
          set(state => {
            state.isWebSocketConnected = connected;
          });
        },
        
        getPatientCommunicationData: (nodeId: string) => {
          const { flattenedNodes, communicationStatus, communicationPreferences, activeConnections } = get();
          const node = flattenedNodes[nodeId];
          
          if (!node) return null;
          
          const patientId = node.patient_id || node.national_id || node.nphies_id;
          if (!patientId) return null;
          
          return {
            node,
            status: communicationStatus[patientId] || {},
            preferences: communicationPreferences[patientId] || {},
            activeConnections: Array.from(activeConnections.values()).filter(
              conn => conn.patientId === patientId
            )
          };
        },
        
        getNodesWithActiveEmergencies: () => {
          const { flattenedNodes, emergencyAlerts } = get();
          const activeEmergencies = emergencyAlerts.filter(alert => !alert.resolved);
          
          return Object.values(flattenedNodes).filter(node => {
            const patientId = node.patient_id || node.national_id || node.nphies_id;
            return activeEmergencies.some(alert => alert.patientId === patientId);
          });
        }
      })),
      {
        name: 'oid-tree-store',
        partialize: (state) => ({
          expandedNodes: state.expandedNodes,
          selectedNode: state.selectedNode,
          healthcareFilter: state.healthcareFilter,
          communicationPreferences: state.communicationPreferences
        })
      }
    ),
    { name: 'OID Tree Store' }
  )
);

// Export healthcare filters for use in components
export { HEALTHCARE_FILTERS };