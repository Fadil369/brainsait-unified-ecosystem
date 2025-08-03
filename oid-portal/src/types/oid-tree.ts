/**
 * BrainSAIT Healthcare OID Tree Types
 * TypeScript interfaces for healthcare-specific OID management
 */

export interface OidNode {
  id: string;
  name: string;
  oid: string;
  description?: string;
  children?: OidNode[];
  
  // Healthcare-specific properties
  healthcareCategory?: HealthcareCategory;
  badgeType?: BadgeType;
  status?: BadgeStatus;
  owner?: string;
  organization?: string;
  country?: string;
  registrationAuthority?: string;
  contact?: string;
  registrationDate?: string;
  roleType?: RoleType;
  specialization?: string;
  priority?: Priority;
  platform?: string;
  
  // Compliance flags
  nphiesCompliant?: boolean;
  fhirCompliant?: boolean;
  hipaaCompliant?: boolean;
  aiEnabled?: boolean;
  voiceEnabled?: boolean;
}

export type HealthcareCategory = 
  | 'medical' 
  | 'administrative' 
  | 'patient' 
  | 'department' 
  | 'service' 
  | 'security' 
  | 'enterprise';

export type BadgeType = 
  | 'service' 
  | 'department' 
  | 'credential' 
  | 'security' 
  | 'platform' 
  | 'identifier' 
  | 'geographic';

export type BadgeStatus = 
  | 'active' 
  | 'pending' 
  | 'revoked' 
  | 'expired';

export type RoleType = 
  | 'doctor' 
  | 'nurse' 
  | 'patient' 
  | 'admin' 
  | 'technician';

export type Priority = 
  | 'critical' 
  | 'high' 
  | 'medium' 
  | 'low';

export interface TreeState {
  treeData: OidNode | null;
  expandedNodes: Record<string, boolean>;
  selectedNode: OidNode | null;
  searchQuery: string;
  healthcareFilter: HealthcareCategory | 'all';
  isLoading: boolean;
  error: string | null;
}

export interface TreeActions {
  setTreeData: (data: OidNode) => void;
  toggleNode: (nodeId: string) => void;
  selectNode: (node: OidNode | null) => void;
  setSearchQuery: (query: string) => void;
  setHealthcareFilter: (filter: HealthcareCategory | 'all') => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  expandNode: (nodeId: string) => void;
  collapseNode: (nodeId: string) => void;
  expandAll: () => void;
  collapseAll: () => void;
}

export interface HealthcareFilter {
  value: HealthcareCategory | 'all';
  label: string;
}

export interface VirtualizedTreeProps {
  node: OidNode;
  level: number;
  searchQuery: string;
  healthcareFilter: HealthcareCategory | 'all';
  expandedNodes: Record<string, boolean>;
  selectedNode: OidNode | null;
  onToggleNode: (nodeId: string) => void;
  onSelectNode: (node: OidNode) => void;
  isRTL: boolean;
  currentLanguage: string;
}

export interface FHIRSyncPayload {
  node: OidNode;
  action: 'create' | 'update' | 'delete';
  timestamp: string;
}

export interface HealthcareActivityPayload {
  action: string;
  nodeId?: string;
  nodeOid?: string;
  healthcareCategory?: HealthcareCategory;
  userRole?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}