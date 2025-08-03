/**
 * UnifiedAPIClient.js
 * 
 * BRAINSAIT UNIFIED API CLIENT
 * Centralized API client following the backend's modular architecture
 * 
 * FEATURES:
 * - Unified endpoint management
 * - Automatic retry logic with exponential backoff
 * - Request/response interceptors
 * - Performance monitoring
 * - Error handling and recovery
 * - Caching strategies
 * - Authentication management
 * - Arabic language support
 * - Real-time WebSocket integration
 * - Offline mode support
 */

import axios from 'axios';

// API Configuration
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  CACHE_TTL: 300000, // 5 minutes
  MAX_CACHE_SIZE: 100
};

// API Endpoints Configuration
const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    PROFILE: '/api/auth/profile'
  },

  // Healthcare Management
  HEALTHCARE: {
    IDENTITIES: '/api/healthcare-identities',
    ORGANIZATIONS: '/api/healthcare-organizations',
    PROVIDERS: '/api/healthcare-providers',
    PATIENTS: '/api/patients'
  },

  // NPHIES Integration
  NPHIES: {
    BASE: '/api/nphies',
    ELIGIBILITY: '/api/nphies/eligibility',
    CLAIMS: '/api/nphies/claims',
    PREAUTH: '/api/nphies/preauth',
    STATUS: '/api/nphies/status'
  },

  // Revenue Cycle Management
  RCM: {
    BASE: '/api/rcm',
    METRICS: '/api/rcm/metrics',
    CLAIMS: '/api/rcm/claims',
    DENIALS: '/api/rcm/denials',
    REVENUE: '/api/rcm/revenue'
  },

  // Training Platform
  TRAINING: {
    BASE: '/api/training',
    PROGRAMS: '/api/training/programs',
    ENROLLMENTS: '/api/training/enrollments',
    PROGRESS: '/api/training/progress',
    CERTIFICATES: '/api/training/certificates'
  },

  // BOT Management
  BOT: {
    BASE: '/api/bot',
    PROJECTS: '/api/bot/projects',
    MILESTONES: '/api/bot/milestones',
    TRANSFERS: '/api/bot/knowledge-transfers'
  },

  // Operations Center
  OPERATIONS: {
    BASE: '/api/operations',
    CENTERS: '/api/operations/centers',
    SHIFTS: '/api/operations/shifts',
    METRICS: '/api/operations/metrics',
    ALERTS: '/api/operations/alerts'
  },

  // AI Analytics
  AI: {
    BASE: '/api/ai',
    ANALYTICS: '/api/ai/analytics',
    INSIGHTS: '/api/ai/insights',
    MODELS: '/api/ai/models',
    PREDICTIONS: '/api/ai/predictions'
  },

  // OID Tree Management
  OID: {
    BASE: '/api/oid',
    TREE: '/api/oid/tree',
    NODES: '/api/oid/nodes',
    SEARCH: '/api/oid/search'
  },

  // System Management
  SYSTEM: {
    STATUS: '/api/system/status',
    HEALTH: '/api/system/health',
    METRICS: '/api/system/metrics',
    LOGS: '/api/system/logs'
  },

  // Unified Data Access
  UNIFIED: {
    DATA: '/api/unified/data',
    CONTEXT: (context) => `/api/unified/data/${context}`,
    OPERATION: (context, operation) => `/api/unified/${context}/${operation}`
  }
};

// Request Priority Levels
const REQUEST_PRIORITY = {
  CRITICAL: 1,    // Authentication, emergency alerts
  HIGH: 2,        // Real-time operations, NPHIES
  NORMAL: 3,      // Standard data operations
  LOW: 4,         // Background tasks, analytics
  BACKGROUND: 5   // Non-urgent operations
};

// Cache Strategy Types
const CACHE_STRATEGY = {
  NO_CACHE: 'no_cache',
  MEMORY_ONLY: 'memory_only',
  PERSISTENT: 'persistent',
  AGGRESSIVE: 'aggressive'
};

/**
 * Enhanced Cache Manager
 */
class CacheManager {
  constructor() {
    this.memoryCache = new Map();
    this.persistentCache = this.initializePersistentCache();
    this.cacheStats = {
      hits: 0,
      misses: 0,
      evictions: 0
    };
  }

  initializePersistentCache() {
    try {
      const stored = localStorage.getItem('brainsait_api_cache');
      return stored ? new Map(JSON.parse(stored)) : new Map();
    } catch (error) {
      console.warn('Failed to initialize persistent cache:', error);
      return new Map();
    }
  }

  generateKey(url, params, headers) {
    const keyData = { url, params, headers: headers || {} };
    return btoa(JSON.stringify(keyData)).replace(/[^a-zA-Z0-9]/g, '');
  }

  get(key, strategy = CACHE_STRATEGY.MEMORY_ONLY) {
    let cached = null;

    // Check memory cache first
    if (this.memoryCache.has(key)) {
      cached = this.memoryCache.get(key);
    } else if (strategy === CACHE_STRATEGY.PERSISTENT || strategy === CACHE_STRATEGY.AGGRESSIVE) {
      // Check persistent cache
      cached = this.persistentCache.get(key);
      if (cached) {
        // Promote to memory cache
        this.memoryCache.set(key, cached);
      }
    }

    if (cached) {
      const isExpired = Date.now() - cached.timestamp > cached.ttl;
      if (isExpired) {
        this.delete(key);
        this.cacheStats.misses++;
        return null;
      }
      
      this.cacheStats.hits++;
      return cached.data;
    }

    this.cacheStats.misses++;
    return null;
  }

  set(key, data, ttl = API_CONFIG.CACHE_TTL, strategy = CACHE_STRATEGY.MEMORY_ONLY) {
    const cached = {
      data,
      timestamp: Date.now(),
      ttl
    };

    // Always store in memory cache
    this.memoryCache.set(key, cached);

    // Store in persistent cache if strategy requires it
    if (strategy === CACHE_STRATEGY.PERSISTENT || strategy === CACHE_STRATEGY.AGGRESSIVE) {
      this.persistentCache.set(key, cached);
      this.savePersistentCache();
    }

    // Cleanup if cache is too large
    this.cleanup();
  }

  delete(key) {
    this.memoryCache.delete(key);
    this.persistentCache.delete(key);
    this.savePersistentCache();
  }

  clear() {
    this.memoryCache.clear();
    this.persistentCache.clear();
    localStorage.removeItem('brainsait_api_cache');
  }

  cleanup() {
    if (this.memoryCache.size > API_CONFIG.MAX_CACHE_SIZE) {
      const entries = Array.from(this.memoryCache.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      
      // Remove oldest 20% of entries
      const toRemove = Math.floor(entries.length * 0.2);
      for (let i = 0; i < toRemove; i++) {
        this.memoryCache.delete(entries[i][0]);
        this.cacheStats.evictions++;
      }
    }
  }

  savePersistentCache() {
    try {
      const data = JSON.stringify(Array.from(this.persistentCache.entries()));
      localStorage.setItem('brainsait_api_cache', data);
    } catch (error) {
      console.warn('Failed to save persistent cache:', error);
    }
  }

  getStats() {
    return {
      ...this.cacheStats,
      memorySize: this.memoryCache.size,
      persistentSize: this.persistentCache.size,
      hitRate: this.cacheStats.hits / (this.cacheStats.hits + this.cacheStats.misses) || 0
    };
  }
}

/**
 * Request Queue Manager
 */
class RequestQueueManager {
  constructor() {
    this.queues = {
      [REQUEST_PRIORITY.CRITICAL]: [],
      [REQUEST_PRIORITY.HIGH]: [],
      [REQUEST_PRIORITY.NORMAL]: [],
      [REQUEST_PRIORITY.LOW]: [],
      [REQUEST_PRIORITY.BACKGROUND]: []
    };
    this.processing = false;
    this.maxConcurrent = 5;
    this.activeRequests = 0;
  }

  enqueue(request, priority = REQUEST_PRIORITY.NORMAL) {
    this.queues[priority].push(request);
    this.processQueue();
  }

  async processQueue() {
    if (this.processing || this.activeRequests >= this.maxConcurrent) {
      return;
    }

    this.processing = true;

    try {
      // Process queues in priority order
      for (let priority = REQUEST_PRIORITY.CRITICAL; priority <= REQUEST_PRIORITY.BACKGROUND; priority++) {
        const queue = this.queues[priority];
        
        while (queue.length > 0 && this.activeRequests < this.maxConcurrent) {
          const request = queue.shift();
          this.executeRequest(request);
        }
      }
    } finally {
      this.processing = false;
    }
  }

  async executeRequest(request) {
    this.activeRequests++;
    
    try {
      const result = await request.execute();
      request.resolve(result);
    } catch (error) {
      request.reject(error);
    } finally {
      this.activeRequests--;
      // Continue processing if there are more requests
      if (this.hasQueuedRequests()) {
        setTimeout(() => this.processQueue(), 10);
      }
    }
  }

  hasQueuedRequests() {
    return Object.values(this.queues).some(queue => queue.length > 0);
  }

  getQueueStats() {
    return {
      queues: Object.keys(this.queues).reduce((acc, priority) => ({
        ...acc,
        [priority]: this.queues[priority].length
      }), {}),
      activeRequests: this.activeRequests,
      totalQueued: Object.values(this.queues).reduce((sum, queue) => sum + queue.length, 0)
    };
  }
}

/**
 * Performance Monitor
 */
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      totalResponseTime: 0,
      slowRequests: 0,
      networkErrors: 0,
      serverErrors: 0,
      clientErrors: 0
    };
    this.responseTimeHistory = [];
    this.maxHistorySize = 100;
  }

  recordRequest(startTime, success, status, error = null) {
    const responseTime = Date.now() - startTime;
    
    this.metrics.totalRequests++;
    this.metrics.totalResponseTime += responseTime;
    
    if (success) {
      this.metrics.successfulRequests++;
    } else {
      this.metrics.failedRequests++;
      
      if (status >= 500) {
        this.metrics.serverErrors++;
      } else if (status >= 400) {
        this.metrics.clientErrors++;
      } else {
        this.metrics.networkErrors++;
      }
    }

    if (responseTime > 5000) {
      this.metrics.slowRequests++;
    }

    // Store response time history
    this.responseTimeHistory.push(responseTime);
    if (this.responseTimeHistory.length > this.maxHistorySize) {
      this.responseTimeHistory.shift();
    }
  }

  getMetrics() {
    const avgResponseTime = this.metrics.totalRequests > 0 
      ? this.metrics.totalResponseTime / this.metrics.totalRequests 
      : 0;

    const successRate = this.metrics.totalRequests > 0 
      ? (this.metrics.successfulRequests / this.metrics.totalRequests) * 100 
      : 0;

    return {
      ...this.metrics,
      averageResponseTime: avgResponseTime,
      successRate,
      recentResponseTimes: [...this.responseTimeHistory]
    };
  }

  reset() {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      totalResponseTime: 0,
      slowRequests: 0,
      networkErrors: 0,
      serverErrors: 0,
      clientErrors: 0
    };
    this.responseTimeHistory = [];
  }
}

/**
 * Main Unified API Client Class
 */
class UnifiedAPIClient {
  constructor() {
    this.cacheManager = new CacheManager();
    this.queueManager = new RequestQueueManager();
    this.performanceMonitor = new PerformanceMonitor();
    this.retryCount = new Map();
    this.authToken = null;
    this.refreshToken = null;
    this.isRefreshing = false;
    this.failedRequestsQueue = [];

    this.initializeAxiosClient();
    this.setupInterceptors();
  }

  initializeAxiosClient() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Client': 'BrainSAIT-Frontend',
        'X-Version': '1.0.0'
      }
    });
  }

  setupInterceptors() {
    // Request Interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add authentication token
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }

        // Add request timestamp for performance monitoring
        config.startTime = Date.now();

        // Add request ID for tracking
        config.requestId = this.generateRequestId();

        // Add language preference
        config.headers['Accept-Language'] = this.getLanguagePreference();

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response Interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Record performance metrics
        this.performanceMonitor.recordRequest(
          response.config.startTime,
          true,
          response.status
        );

        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Record performance metrics
        this.performanceMonitor.recordRequest(
          originalRequest.startTime,
          false,
          error.response?.status || 0,
          error
        );

        // Handle token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Queue failed requests during token refresh
            return new Promise((resolve, reject) => {
              this.failedRequestsQueue.push({ resolve, reject, config: originalRequest });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const newToken = await this.refreshAccessToken();
            this.authToken = newToken;
            originalRequest.headers.Authorization = `Bearer ${newToken}`;

            // Retry failed requests
            this.processFailedRequestsQueue(newToken);

            return this.client(originalRequest);
          } catch (refreshError) {
            this.handleAuthenticationFailure();
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        // Handle retry logic for network errors
        if (this.shouldRetry(error, originalRequest)) {
          return this.retryRequest(originalRequest);
        }

        return Promise.reject(error);
      }
    );
  }

  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getLanguagePreference() {
    // Get from localStorage or default to Arabic for BrainSAIT
    const userLanguage = localStorage.getItem('user_language') || 'ar';
    return userLanguage === 'ar' ? 'ar-SA,ar;q=0.9,en;q=0.8' : 'en-US,en;q=0.9,ar;q=0.8';
  }

  shouldRetry(error, config) {
    const retryCount = this.retryCount.get(config.requestId) || 0;
    
    // Don't retry if max attempts reached
    if (retryCount >= API_CONFIG.RETRY_ATTEMPTS) {
      return false;
    }

    // Don't retry for certain error types
    const nonRetryableErrors = [400, 401, 403, 404, 422];
    if (error.response && nonRetryableErrors.includes(error.response.status)) {
      return false;
    }

    // Don't retry POST requests by default (unless explicitly allowed)
    if (config.method === 'post' && !config.retryPost) {
      return false;
    }

    return true;
  }

  async retryRequest(config) {
    const retryCount = this.retryCount.get(config.requestId) || 0;
    const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, retryCount); // Exponential backoff

    this.retryCount.set(config.requestId, retryCount + 1);

    await new Promise(resolve => setTimeout(resolve, delay));
    
    return this.client(config);
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`, {
      refresh_token: this.refreshToken
    });

    const { access_token, refresh_token } = response.data;
    this.setTokens(access_token, refresh_token);
    
    return access_token;
  }

  processFailedRequestsQueue(token) {
    this.failedRequestsQueue.forEach(({ resolve, reject, config }) => {
      config.headers.Authorization = `Bearer ${token}`;
      this.client(config).then(resolve).catch(reject);
    });
    
    this.failedRequestsQueue = [];
  }

  handleAuthenticationFailure() {
    this.authToken = null;
    this.refreshToken = null;
    
    // Emit authentication failure event
    window.dispatchEvent(new CustomEvent('auth-failure'));
  }

  setTokens(accessToken, refreshToken) {
    this.authToken = accessToken;
    this.refreshToken = refreshToken;
    
    // Store in localStorage for persistence
    if (accessToken) {
      localStorage.setItem('access_token', accessToken);
    }
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  loadTokensFromStorage() {
    this.authToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  clearTokens() {
    this.authToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Core API Methods
  async request(method, url, data = null, options = {}) {
    const {
      priority = REQUEST_PRIORITY.NORMAL,
      cacheStrategy = CACHE_STRATEGY.MEMORY_ONLY,
      cacheTTL = API_CONFIG.CACHE_TTL,
      bypassCache = false,
      ...axiosOptions
    } = options;

    // Generate cache key
    const cacheKey = this.cacheManager.generateKey(url, data, axiosOptions.headers);

    // Check cache first (for GET requests)
    if (method === 'GET' && !bypassCache) {
      const cachedData = this.cacheManager.get(cacheKey, cacheStrategy);
      if (cachedData) {
        return { data: cachedData, fromCache: true };
      }
    }

    // Create request promise
    const requestPromise = new Promise((resolve, reject) => {
      const requestConfig = {
        method,
        url,
        data,
        ...axiosOptions
      };

      const request = {
        execute: () => this.client(requestConfig),
        resolve,
        reject
      };

      this.queueManager.enqueue(request, priority);
    });

    try {
      const response = await requestPromise;
      
      // Cache successful GET responses
      if (method === 'GET' && response.data) {
        this.cacheManager.set(cacheKey, response.data, cacheTTL, cacheStrategy);
      }

      return response;
    } catch (error) {
      throw this.normalizeError(error);
    }
  }

  normalizeError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        type: 'API_ERROR',
        status: error.response.status,
        message: error.response.data?.message || error.message,
        data: error.response.data,
        code: error.response.data?.code
      };
    } else if (error.request) {
      // Network error
      return {
        type: 'NETWORK_ERROR',
        message: 'Network connection failed',
        originalError: error
      };
    } else {
      // Request setup error
      return {
        type: 'REQUEST_ERROR',
        message: error.message,
        originalError: error
      };
    }
  }

  // Convenience methods
  async get(url, options = {}) {
    return this.request('GET', url, null, options);
  }

  async post(url, data, options = {}) {
    return this.request('POST', url, data, options);
  }

  async put(url, data, options = {}) {
    return this.request('PUT', url, data, options);
  }

  async patch(url, data, options = {}) {
    return this.request('PATCH', url, data, options);
  }

  async delete(url, options = {}) {
    return this.request('DELETE', url, null, options);
  }

  // Healthcare-specific API methods
  async getHealthcareIdentities(filters = {}, options = {}) {
    const params = new URLSearchParams(filters).toString();
    const url = `${API_ENDPOINTS.HEALTHCARE.IDENTITIES}${params ? `?${params}` : ''}`;
    return this.get(url, { cacheStrategy: CACHE_STRATEGY.AGGRESSIVE, ...options });
  }

  async createHealthcareIdentity(identityData, options = {}) {
    return this.post(API_ENDPOINTS.HEALTHCARE.IDENTITIES, identityData, {
      priority: REQUEST_PRIORITY.HIGH,
      ...options
    });
  }

  async updateHealthcareIdentity(id, updateData, options = {}) {
    return this.put(`${API_ENDPOINTS.HEALTHCARE.IDENTITIES}/${id}`, updateData, {
      priority: REQUEST_PRIORITY.HIGH,
      ...options
    });
  }

  // NPHIES API methods
  async checkEligibility(eligibilityData, options = {}) {
    return this.post(API_ENDPOINTS.NPHIES.ELIGIBILITY, eligibilityData, {
      priority: REQUEST_PRIORITY.CRITICAL,
      retryPost: true,
      ...options
    });
  }

  async submitClaim(claimData, options = {}) {
    return this.post(API_ENDPOINTS.NPHIES.CLAIMS, claimData, {
      priority: REQUEST_PRIORITY.CRITICAL,
      retryPost: true,
      ...options
    });
  }

  async getClaimStatus(claimId, options = {}) {
    return this.get(`${API_ENDPOINTS.NPHIES.CLAIMS}/${claimId}/status`, {
      priority: REQUEST_PRIORITY.HIGH,
      ...options
    });
  }

  // Training API methods
  async getTrainingPrograms(options = {}) {
    return this.get(API_ENDPOINTS.TRAINING.PROGRAMS, {
      cacheStrategy: CACHE_STRATEGY.PERSISTENT,
      ...options
    });
  }

  async enrollInProgram(programId, enrollmentData, options = {}) {
    return this.post(`${API_ENDPOINTS.TRAINING.PROGRAMS}/${programId}/enroll`, enrollmentData, {
      priority: REQUEST_PRIORITY.HIGH,
      ...options
    });
  }

  // AI Analytics methods
  async getAIInsights(context, options = {}) {
    return this.post(API_ENDPOINTS.AI.INSIGHTS, { context }, {
      priority: REQUEST_PRIORITY.NORMAL,
      ...options
    });
  }

  async processAIRequest(requestData, options = {}) {
    return this.post(API_ENDPOINTS.AI.ANALYTICS, requestData, {
      priority: REQUEST_PRIORITY.NORMAL,
      timeout: 60000, // AI requests may take longer
      ...options
    });
  }

  // OID Tree methods
  async getOIDTree(language = 'en', options = {}) {
    return this.get(`${API_ENDPOINTS.OID.TREE}?language=${language}`, {
      cacheStrategy: CACHE_STRATEGY.PERSISTENT,
      ...options
    });
  }

  async searchOIDNodes(query, options = {}) {
    return this.get(`${API_ENDPOINTS.OID.SEARCH}?q=${encodeURIComponent(query)}`, {
      cacheStrategy: CACHE_STRATEGY.MEMORY_ONLY,
      ...options
    });
  }

  // Unified data access
  async getUnifiedData(context = null, options = {}) {
    const url = context ? API_ENDPOINTS.UNIFIED.CONTEXT(context) : API_ENDPOINTS.UNIFIED.DATA;
    return this.get(url, {
      cacheStrategy: CACHE_STRATEGY.AGGRESSIVE,
      ...options
    });
  }

  async callUnifiedOperation(context, operation, data = null, options = {}) {
    const url = API_ENDPOINTS.UNIFIED.OPERATION(context, operation);
    return this.post(url, data, {
      priority: REQUEST_PRIORITY.HIGH,
      ...options
    });
  }

  // System monitoring
  async getSystemStatus(options = {}) {
    return this.get(API_ENDPOINTS.SYSTEM.STATUS, {
      priority: REQUEST_PRIORITY.HIGH,
      bypassCache: true,
      ...options
    });
  }

  async getSystemHealth(options = {}) {
    return this.get(API_ENDPOINTS.SYSTEM.HEALTH, {
      priority: REQUEST_PRIORITY.HIGH,
      bypassCache: true,
      ...options
    });
  }

  // Utility methods
  getPerformanceMetrics() {
    return {
      api: this.performanceMonitor.getMetrics(),
      cache: this.cacheManager.getStats(),
      queue: this.queueManager.getQueueStats()
    };
  }

  clearCache() {
    this.cacheManager.clear();
  }

  resetMetrics() {
    this.performanceMonitor.reset();
  }

  // WebSocket connection for real-time updates
  connectWebSocket(userId, onMessage, onError) {
    const wsUrl = `${API_CONFIG.WS_URL}/ws/${userId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }
}

// Create singleton instance
const unifiedAPIClient = new UnifiedAPIClient();

// Initialize tokens from storage
unifiedAPIClient.loadTokensFromStorage();

// Export the singleton instance and configuration
export default unifiedAPIClient;
export { 
  API_ENDPOINTS, 
  REQUEST_PRIORITY, 
  CACHE_STRATEGY,
  UnifiedAPIClient 
};