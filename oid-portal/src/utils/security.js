/**
 * Security Utilities for BrainSAIT Healthcare Platform
 * Provides input sanitization, validation, and security helpers
 */

import DOMPurify from "dompurify";

/**
 * Sanitizes user input to prevent XSS and injection attacks
 * @param {string} input - The input string to sanitize
 * @param {Object} options - Sanitization options
 * @returns {string} - Sanitized string
 */
export const sanitizeInput = (input, options = {}) => {
  if (typeof input !== "string") {
    return String(input);
  }

  const {
    allowHtml = false,
    maxLength = 1000,
    stripScripts = true,
    preserveNewlines = false,
  } = options;

  let sanitized = input;

  // Truncate to max length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }

  // Remove script tags and potentially dangerous content
  if (stripScripts) {
    sanitized = sanitized.replace(
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      ""
    );
    sanitized = sanitized.replace(/javascript:/gi, "");
    sanitized = sanitized.replace(/on\w+\s*=/gi, "");
  }

  // Handle HTML content
  if (allowHtml) {
    sanitized = DOMPurify.sanitize(sanitized, {
      ALLOWED_TAGS: ["b", "i", "em", "strong", "p", "br"],
      ALLOWED_ATTR: [],
    });
  } else {
    // Escape HTML entities
    sanitized = sanitized
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#x27;");
  }

  // Handle newlines
  if (!preserveNewlines) {
    sanitized = sanitized.replace(/[\r\n]/g, " ");
  }

  return sanitized.trim();
};

/**
 * Validates and sanitizes healthcare-specific data
 * @param {Object} data - Healthcare data object
 * @returns {Object} - Sanitized data object
 */
export const sanitizeHealthcareData = (data) => {
  const sanitized = {};

  for (const [key, value] of Object.entries(data)) {
    if (typeof value === "string") {
      // Special handling for sensitive healthcare fields
      if (key.includes("id") || key.includes("identifier")) {
        // Only allow alphanumeric and specific characters for IDs
        sanitized[key] = value.replace(/[^a-zA-Z0-9\-_.]/g, "");
      } else if (key.includes("name") || key.includes("description")) {
        // Allow more characters for names and descriptions but sanitize
        sanitized[key] = sanitizeInput(value, { maxLength: 500 });
      } else {
        sanitized[key] = sanitizeInput(value);
      }
    } else if (typeof value === "object" && value !== null) {
      sanitized[key] = sanitizeHealthcareData(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
};

/**
 * Validates email addresses with enhanced security
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid
 */
export const isValidEmail = (email) => {
  if (!email || typeof email !== "string") return false;

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const sanitizedEmail = sanitizeInput(email, { maxLength: 254 });

  return emailRegex.test(sanitizedEmail) && sanitizedEmail.length <= 254;
};

/**
 * Validates NPHIES ID format
 * @param {string} nphiesId - NPHIES ID to validate
 * @returns {boolean} - True if valid format
 */
export const isValidNphiesId = (nphiesId) => {
  if (!nphiesId || typeof nphiesId !== "string") return false;

  // NPHIES ID format: NPHIES_ followed by alphanumeric
  const nphiesRegex = /^NPHIES_[A-Z0-9_]{1,50}$/;
  const sanitized = sanitizeInput(nphiesId, { maxLength: 60 });

  return nphiesRegex.test(sanitized);
};

/**
 * Generates CSRF token
 * @returns {string} - CSRF token
 */
export const generateCSRFToken = () => {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, (byte) => byte.toString(16).padStart(2, "0")).join(
    ""
  );
};

/**
 * Validates CSRF token
 * @param {string} token - Token to validate
 * @param {string} storedToken - Stored token for comparison
 * @returns {boolean} - True if valid
 */
export const validateCSRFToken = (token, storedToken) => {
  if (!token || !storedToken) return false;
  if (typeof token !== "string" || typeof storedToken !== "string")
    return false;

  return token === storedToken && token.length === 64;
};

/**
 * Sanitizes data for logging to prevent log injection
 * @param {any} data - Data to be logged
 * @returns {string} - Safe string for logging
 */
export const sanitizeForLogging = (data) => {
  if (data === null || data === undefined) {
    return "null";
  }

  let logString;

  if (typeof data === "object") {
    try {
      // Remove sensitive fields before logging
      const sanitizedData = { ...data };
      const sensitiveFields = [
        "password",
        "token",
        "secret",
        "key",
        "credential",
      ];

      for (const field of sensitiveFields) {
        if (sanitizedData[field]) {
          sanitizedData[field] = "[REDACTED]";
        }
      }

      logString = JSON.stringify(sanitizedData);
    } catch (error) {
      logString = "[Object - JSON serialization failed]";
    }
  } else {
    logString = String(data);
  }

  // Remove control characters and limit length
  return logString
    .replace(/[^\x20-\x7E\u00A0-\uFFFF]/g, "") // Keep only printable characters
    .replace(/[\r\n]/g, " ") // Replace newlines with spaces
    .substring(0, 1000); // Limit length
};

/**
 * Rate limiting helper
 * @param {string} key - Rate limit key (usually user ID or IP)
 * @param {number} limit - Maximum requests
 * @param {number} windowMs - Time window in milliseconds
 * @returns {boolean} - True if within limits
 */
export const checkRateLimit = (key, limit = 100, windowMs = 60000) => {
  const now = Date.now();
  const storageKey = `rateLimit_${key}`;

  try {
    const stored = localStorage.getItem(storageKey);
    const data = stored
      ? JSON.parse(stored)
      : { count: 0, resetTime: now + windowMs };

    if (now > data.resetTime) {
      // Reset window
      data.count = 1;
      data.resetTime = now + windowMs;
    } else {
      data.count++;
    }

    localStorage.setItem(storageKey, JSON.stringify(data));

    return data.count <= limit;
  } catch (error) {
    // If localStorage fails, allow the request
    return true;
  }
};

/**
 * Content Security Policy helper
 * @returns {Object} - CSP directives
 */
export const getCSPDirectives = () => {
  return {
    "default-src": "'self'",
    "script-src": "'self' 'unsafe-inline' https://apis.google.com",
    "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src": "'self' https://fonts.gstatic.com",
    "img-src": "'self' data: https:",
    "connect-src": "'self' https://api.brainsait.sa wss://api.brainsait.sa",
    "frame-ancestors": "'none'",
    "base-uri": "'self'",
    "form-action": "'self'",
  };
};

export default {
  sanitizeInput,
  sanitizeHealthcareData,
  sanitizeForLogging,
  isValidEmail,
  isValidNphiesId,
  generateCSRFToken,
  validateCSRFToken,
  checkRateLimit,
  getCSPDirectives,
};
