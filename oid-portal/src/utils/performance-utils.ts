/**
 * Performance Optimization Utilities
 * Healthcare-specific performance optimizations for handling large datasets
 */

import { useMemo, useCallback, useRef, useEffect } from 'react';
import type { OidNode } from '../types/oid-tree';

// Debounce utility for search and filtering
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Throttle utility for scroll events
export const useThrottle = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T => {
  const lastRun = useRef(Date.now());

  return useCallback(
    ((...args) => {
      if (Date.now() - lastRun.current >= delay) {
        callback(...args);
        lastRun.current = Date.now();
      }
    }) as T,
    [callback, delay]
  );
};

// Memory optimization for large tree structures
export const createMemoizedTreeFlattener = () => {
  const cache = new Map<string, any>();

  return {
    flattenTree: (node: OidNode, expanded: Record<string, boolean>) => {
      const cacheKey = `${node.id}-${JSON.stringify(expanded)}`;
      
      if (cache.has(cacheKey)) {
        return cache.get(cacheKey);
      }

      const flatten = (currentNode: OidNode, level: number = 0): any[] => {
        const result = [{
          ...currentNode,
          level,
          hasChildren: currentNode.children && currentNode.children.length > 0,
          isExpanded: expanded[currentNode.id] || false
        }];

        if (currentNode.children && expanded[currentNode.id]) {
          currentNode.children.forEach(child => {
            result.push(...flatten(child, level + 1));
          });
        }

        return result;
      };

      const flattened = flatten(node);
      cache.set(cacheKey, flattened);
      
      // Cleanup cache if it gets too large (> 100 entries)
      if (cache.size > 100) {
        const firstKey = cache.keys().next().value;
        cache.delete(firstKey);
      }
      
      return flattened;
    },
    
    clearCache: () => cache.clear()
  };
};

// Optimized search utilities
export const createOptimizedSearch = () => {
  const searchIndex = new Map<string, OidNode[]>();
  
  return {
    buildSearchIndex: (nodes: OidNode[]) => {
      searchIndex.clear();
      
      const addToIndex = (node: OidNode) => {
        const searchableText = [
          node.name,
          node.oid,
          node.description,
          node.healthcareCategory,
          node.organization,
          node.owner
        ].filter(Boolean).join(' ').toLowerCase();
        
        // Create n-grams for better search
        const words = searchableText.split(' ');
        words.forEach(word => {
          for (let i = 0; i < word.length - 1; i++) {
            const ngram = word.substring(i, i + 3);
            if (!searchIndex.has(ngram)) {
              searchIndex.set(ngram, []);
            }
            searchIndex.get(ngram)!.push(node);
          }
        });
        
        if (node.children) {
          node.children.forEach(addToIndex);
        }
      };
      
      nodes.forEach(addToIndex);
    },
    
    search: (query: string): OidNode[] => {
      if (!query || query.length < 2) return [];
      
      const queryLower = query.toLowerCase();
      const results = new Set<OidNode>();
      
      // Use n-gram index for fast initial filtering
      for (let i = 0; i < queryLower.length - 2; i++) {
        const ngram = queryLower.substring(i, i + 3);
        const nodes = searchIndex.get(ngram) || [];
        nodes.forEach(node => results.add(node));
      }
      
      // Filter results for exact matches
      return Array.from(results).filter(node => {
        const searchableText = [
          node.name,
          node.oid,
          node.description,
          node.healthcareCategory,
          node.organization,
          node.owner
        ].filter(Boolean).join(' ').toLowerCase();
        
        return searchableText.includes(queryLower);
      });
    }
  };
};

// Virtual scrolling optimization
export const useVirtualScrolling = (
  itemCount: number,
  itemHeight: number,
  containerHeight: number
) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  
  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const end = Math.min(start + visibleCount + 5, itemCount); // +5 for buffer
    
    return { start: Math.max(0, start - 5), end }; // -5 for buffer
  }, [scrollTop, itemHeight, containerHeight, itemCount]);
  
  const totalHeight = itemCount * itemHeight;
  const offsetY = visibleRange.start * itemHeight;
  
  return {
    visibleRange,
    totalHeight,
    offsetY,
    onScroll: (e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop);
    }
  };
};

// Healthcare-specific performance optimizations
export const healthcarePerformanceUtils = {
  // Batch process large healthcare datasets
  batchProcess: async <T, R>(
    items: T[],
    processor: (batch: T[]) => Promise<R[]>,
    batchSize: number = 100
  ): Promise<R[]> => {
    const results: R[] = [];
    
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const batchResults = await processor(batch);
      results.push(...batchResults);
      
      // Allow other tasks to run
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    
    return results;
  },
  
  // Optimize healthcare data structures
  optimizeHealthcareNode: (node: OidNode): OidNode => {
    // Remove unnecessary data for virtualization
    const optimized = { ...node };
    
    // Keep only essential properties for rendering
    if (!node.badgeType) {
      delete optimized.owner;
      delete optimized.status;
      delete optimized.registrationDate;
    }
    
    // Optimize children recursively
    if (optimized.children) {
      optimized.children = optimized.children.map(healthcarePerformanceUtils.optimizeHealthcareNode);
    }
    
    return optimized;
  },
  
  // Memory-efficient compliance checking
  createComplianceChecker: () => {
    const complianceCache = new WeakMap<OidNode, Record<string, boolean>>();
    
    return {
      checkCompliance: (node: OidNode): Record<string, boolean> => {
        if (complianceCache.has(node)) {
          return complianceCache.get(node)!;
        }
        
        const compliance = {
          nphies: node.nphiesCompliant || false,
          fhir: node.fhirCompliant || false,
          hipaa: node.hipaaCompliant || false,
          ai: node.aiEnabled || false,
          voice: node.voiceEnabled || false
        };
        
        complianceCache.set(node, compliance);
        return compliance;
      }
    };
  }
};

// Image and asset optimization
export const assetOptimizationUtils = {
  // Lazy load images with intersection observer
  useLazyImage: (src: string, fallback: string = '') => {
    const [imageSrc, setImageSrc] = React.useState(fallback);
    const [isLoaded, setIsLoaded] = React.useState(false);
    const imgRef = useRef<HTMLImageElement>(null);
    
    useEffect(() => {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting && !isLoaded) {
            setImageSrc(src);
            setIsLoaded(true);
            observer.disconnect();
          }
        },
        { threshold: 0.1 }
      );
      
      if (imgRef.current) {
        observer.observe(imgRef.current);
      }
      
      return () => observer.disconnect();
    }, [src, isLoaded]);
    
    return { imageSrc, imgRef };
  },
  
  // Preload critical assets
  preloadAssets: (assets: string[]) => {
    assets.forEach(asset => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = asset;
      link.as = asset.endsWith('.css') ? 'style' : 'script';
      document.head.appendChild(link);
    });
  }
};

// Bundle optimization utilities
export const bundleOptimizationUtils = {
  // Dynamic imports for code splitting
  createLazyComponent: <T extends React.ComponentType<any>>(
    importFn: () => Promise<{ default: T }>
  ) => {
    return React.lazy(importFn);
  },
  
  // Service worker registration for caching
  registerServiceWorker: async (swPath: string = '/sw.js') => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register(swPath);
        console.log('SW registered: ', registration);
        return registration;
      } catch (error) {
        console.log('SW registration failed: ', error);
        return null;
      }
    }
    return null;
  }
};

// Performance monitoring
export const performanceMonitoring = {
  // Measure component render times
  useRenderTimer: (componentName: string) => {
    useEffect(() => {
      const startTime = performance.now();
      
      return () => {
        const endTime = performance.now();
        console.log(`${componentName} render time: ${endTime - startTime}ms`);
      };
    });
  },
  
  // Memory usage monitoring
  useMemoryMonitor: () => {
    const [memoryInfo, setMemoryInfo] = React.useState<any>(null);
    
    useEffect(() => {
      const updateMemoryInfo = () => {
        if ('memory' in performance) {
          setMemoryInfo((performance as any).memory);
        }
      };
      
      updateMemoryInfo();
      const interval = setInterval(updateMemoryInfo, 5000);
      
      return () => clearInterval(interval);
    }, []);
    
    return memoryInfo;
  }
};

// Export all utilities
export default {
  useDebounce,
  useThrottle,
  createMemoizedTreeFlattener,
  createOptimizedSearch,
  useVirtualScrolling,
  healthcarePerformanceUtils,
  assetOptimizationUtils,
  bundleOptimizationUtils,
  performanceMonitoring
};