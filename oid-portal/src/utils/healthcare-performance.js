/**
 * Healthcare Performance Optimization Utilities
 * Specialized for BrainSAIT Healthcare Platform
 */

import { useCallback, useMemo, useRef, useEffect, useState } from 'react';

/**
 * Debounce hook for search inputs (optimized for Arabic and English)
 */
export const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Healthcare data memoization hook
 * Optimized for FHIR resource comparisons
 */
export const useHealthcareDataMemo = (data, dependencies = []) => {
  return useMemo(() => {
    if (!data) return null;
    
    // Deep comparison for healthcare data structures
    const processHealthcareData = (item) => {
      if (Array.isArray(item)) {
        return item.map(processHealthcareData);
      }
      
      if (item && typeof item === 'object') {
        // FHIR resource optimization
        if (item.resourceType) {
          return {
            id: item.id,
            resourceType: item.resourceType,
            lastUpdated: item.meta?.lastUpdated,
            ...item
          };
        }
        
        const processed = {};
        Object.keys(item).forEach(key => {
          processed[key] = processHealthcareData(item[key]);
        });
        return processed;
      }
      
      return item;
    };
    
    return processHealthcareData(data);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, ...dependencies]);
};

/**
 * Virtual scrolling hook for large healthcare datasets
 */
export const useVirtualScroll = (items, itemHeight, containerHeight) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );
    
    return {
      startIndex,
      endIndex,
      items: items.slice(startIndex, endIndex),
      totalHeight: items.length * itemHeight,
      offsetY: startIndex * itemHeight
    };
  }, [items, itemHeight, containerHeight, scrollTop]);
  
  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);
  
  return { visibleItems, handleScroll };
};

/**
 * Performance monitoring hook for healthcare operations
 */
export const useHealthcarePerformanceMonitor = (operationName) => {
  const startTime = useRef(null);
  const measurements = useRef([]);
  
  const startMeasurement = useCallback(() => {
    startTime.current = performance.now();
  }, []);
  
  const endMeasurement = useCallback(() => {
    if (startTime.current) {
      const duration = performance.now() - startTime.current;
      measurements.current.push({
        operation: operationName,
        duration,
        timestamp: new Date().toISOString()
      });
      
      // Keep only last 10 measurements
      if (measurements.current.length > 10) {
        measurements.current = measurements.current.slice(-10);
      }
      
      // Log slow operations (>2 seconds for healthcare operations)
      if (duration > 2000) {
        console.warn(`Slow healthcare operation detected: ${operationName} took ${duration.toFixed(2)}ms`);
      }
      
      startTime.current = null;
      return duration;
    }
  }, [operationName]);
  
  const getAverageTime = useCallback(() => {
    if (measurements.current.length === 0) return 0;
    const total = measurements.current.reduce((sum, m) => sum + m.duration, 0);
    return total / measurements.current.length;
  }, []);
  
  return { startMeasurement, endMeasurement, getAverageTime, measurements: measurements.current };
};

/**
 * Healthcare data validation and sanitization
 */
export const sanitizeHealthcareData = (data, type = 'general') => {
  if (!data) return null;
  
  const sanitizers = {
    patient: (patient) => ({
      id: patient.id,
      name: patient.name,
      nameAr: patient.nameAr,
      birthDate: patient.birthDate,
      gender: patient.gender,
      // Remove sensitive fields
      resourceType: patient.resourceType
    }),
    
    appointment: (appointment) => ({
      id: appointment.id,
      status: appointment.status,
      start: appointment.start,
      end: appointment.end,
      serviceType: appointment.serviceType,
      participant: appointment.participant?.map(p => ({
        actor: { display: p.actor?.display },
        status: p.status
      }))
    }),
    
    general: (item) => {
      if (typeof item === 'string') {
        // Basic XSS protection
        return item.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
      }
      return item;
    }
  };
  
  const sanitizer = sanitizers[type] || sanitizers.general;
  
  if (Array.isArray(data)) {
    return data.map(sanitizer);
  }
  
  return sanitizer(data);
};

/**
 * Healthcare-specific error boundary helper
 */
export const createHealthcareErrorHandler = (context) => {
  return (error, _errorInfo) => {
    const errorDetails = {
      context,
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    
    // Healthcare-specific error categories
    if (error.message.includes('FHIR')) {
      errorDetails.category = 'fhir_error';
    } else if (error.message.includes('NPHIES')) {
      errorDetails.category = 'nphies_error';
    } else if (error.message.includes('Network')) {
      errorDetails.category = 'network_error';
    } else {
      errorDetails.category = 'application_error';
    }
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Healthcare Error:', errorDetails);
    }
    
    // In production, send to monitoring service
    if (process.env.NODE_ENV === 'production') {
      // Send to error tracking service
      console.log('Would send error to monitoring service:', errorDetails);
    }
    
    return errorDetails;
  };
};

/**
 * Optimized Arabic text processing
 */
export const processArabicText = (text) => {
  if (!text || typeof text !== 'string') return text;
  
  // Basic Arabic text processing
  return text
    .trim()
    .replace(/\u200C/g, '') // Remove zero-width non-joiner
    .replace(/\u200D/g, '') // Remove zero-width joiner
    .replace(/[\u0640]/g, '') // Remove Arabic tatweel
    .normalize('NFC'); // Normalize Unicode
};

/**
 * Healthcare data caching utilities
 */
export class HealthcareCache {
  constructor(ttl = 300000) { // 5 minutes default
    this.cache = new Map();
    this.ttl = ttl;
  }
  
  set(key, value, customTTL = null) {
    const expiryTime = Date.now() + (customTTL || this.ttl);
    this.cache.set(key, { value, expiryTime });
  }
  
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expiryTime) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
  
  clear() {
    this.cache.clear();
  }
  
  size() {
    return this.cache.size;
  }
}

// Global healthcare cache instance
export const healthcareCache = new HealthcareCache();

export default {
  useDebounce,
  useHealthcareDataMemo,
  useVirtualScroll,
  useHealthcarePerformanceMonitor,
  sanitizeHealthcareData,
  createHealthcareErrorHandler,
  processArabicText,
  HealthcareCache,
  healthcareCache
};