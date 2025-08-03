/**
 * VirtualizedTreeNode Component
 * High-performance virtualized tree node for handling 10,000+ healthcare OID nodes
 */

import { memo, useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import { useOidTreeStore } from '../../stores/oid-tree-store';
import { TreeNodeRenderer } from './TreeNodeRenderer';

// Flattened node structure for virtualization
const flattenNodesForVirtualization = (node, level = 0, expandedNodes = {}) => {
  const flatNodes = [];
  
  const addNode = (currentNode, currentLevel) => {
    flatNodes.push({
      ...currentNode,
      level: currentLevel,
      hasChildren: currentNode.children && currentNode.children.length > 0,
      isExpanded: expandedNodes[currentNode.id] || false
    });
    
    // Add children if node is expanded
    if (currentNode.children && expandedNodes[currentNode.id]) {
      currentNode.children.forEach(child => {
        addNode(child, currentLevel + 1);
      });
    }
  };
  
  addNode(node, level);
  return flatNodes;
};

// Memoized row renderer for optimal performance
const Row = memo(({ index, style, data }) => {
  const { nodes, ...props } = data;
  const node = nodes[index];
  
  if (!node) return null;
  
  return (
    <div style={style}>
      <TreeNodeRenderer
        node={node}
        level={node.level}
        hasChildren={node.hasChildren}
        isExpanded={node.isExpanded}
        {...props}
      />
    </div>
  );
});

Row.displayName = 'VirtualizedTreeRow';

const VirtualizedTreeNode = ({ 
  treeData, 
  height = 600,
  itemHeight = 60,
  searchQuery = '',
  healthcareFilter = 'all'
}) => {
  const {
    expandedNodes,
    selectedNode,
    toggleNode,
    selectNode
  } = useOidTreeStore();

  // Memoized flat nodes calculation
  const flatNodes = useMemo(() => {
    if (!treeData) return [];
    
    const nodes = flattenNodesForVirtualization(treeData, 0, expandedNodes);
    
    // Apply filters
    return nodes.filter(node => {
      // Search filter
      if (searchQuery) {
        const searchableText = `${node.name} ${node.oid} ${node.description || ''} ${node.healthcareCategory || ''}`.toLowerCase();
        if (!searchableText.includes(searchQuery.toLowerCase())) {
          return false;
        }
      }
      
      // Healthcare category filter
      if (healthcareFilter !== 'all') {
        if (node.healthcareCategory !== healthcareFilter) {
          // Check if any children match the category
          const hasMatchingChildren = node.children?.some(child => 
            child.healthcareCategory === healthcareFilter
          );
          if (!hasMatchingChildren) {
            return false;
          }
        }
      }
      
      return true;
    });
  }, [treeData, expandedNodes, searchQuery, healthcareFilter]);

  // Row data for virtualization
  const rowData = useMemo(() => ({
    nodes: flatNodes,
    selectedNode,
    onToggleNode: toggleNode,
    onSelectNode: selectNode
  }), [flatNodes, selectedNode, toggleNode, selectNode]);

  if (!treeData || flatNodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        <div className="text-center">
          <div className="animate-pulse rounded-full bg-darker-bg h-8 w-8 mx-auto mb-2"></div>
          <p>No matching nodes found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="virtualized-tree">
      <List
        height={height}
        itemCount={flatNodes.length}
        itemSize={itemHeight}
        itemData={rowData}
        overscanCount={5} // Render 5 extra items for smooth scrolling
        className="tree-list"
      >
        {Row}
      </List>
      
      {/* Performance indicator */}
      <div className="text-xs text-text-secondary p-2 border-t border-border-color bg-darker-bg">
        Showing {flatNodes.length} nodes (Virtualized for performance)
      </div>
    </div>
  );
};

export default memo(VirtualizedTreeNode);