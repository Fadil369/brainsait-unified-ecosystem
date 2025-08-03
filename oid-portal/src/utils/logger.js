/**
 * Secure Logger Wrapper for BrainSAIT Healthcare Platform
 * Provides secure logging with input sanitization and healthcare compliance
 */

import { sanitizeForLogging } from "./security.js";

class SecureLogger {
  constructor(context = "BrainSAIT") {
    this.context = context;
    this.sensitiveFields = [
      "password",
      "token",
      "secret",
      "key",
      "credential",
      "auth",
      "ssn",
      "social",
      "dob",
      "dateOfBirth",
      "medicalRecord",
      "patientId",
      "nationalId",
      "passport",
      "visa",
    ];
  }

  /**
   * Sanitizes data before logging to prevent injection attacks
   * @param {any} data - Data to sanitize
   * @returns {string} - Sanitized log string
   */
  sanitize(data) {
    return sanitizeForLogging(data);
  }

  /**
   * Redacts sensitive healthcare information
   * @param {Object} data - Data object to redact
   * @returns {Object} - Redacted data object
   */
  redactSensitiveData(data) {
    if (!data || typeof data !== "object") {
      return data;
    }

    const redacted = { ...data };

    // Redact sensitive fields
    for (const field of this.sensitiveFields) {
      if (redacted[field]) {
        redacted[field] = "[REDACTED]";
      }
    }

    // Redact nested objects
    for (const [key, value] of Object.entries(redacted)) {
      if (typeof value === "object" && value !== null) {
        redacted[key] = this.redactSensitiveData(value);
      }
    }

    return redacted;
  }

  /**
   * Formats log message with context and timestamp
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {any} data - Additional data
   * @returns {string} - Formatted log message
   */
  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const sanitizedMessage = this.sanitize(message);

    let logEntry = `[${timestamp}] [${level.toUpperCase()}] [${
      this.context
    }] ${sanitizedMessage}`;

    if (data !== null) {
      const redactedData = this.redactSensitiveData(data);
      const sanitizedData = this.sanitize(redactedData);
      logEntry += ` | Data: ${sanitizedData}`;
    }

    return logEntry;
  }

  /**
   * Log debug message
   * @param {string} message - Debug message
   * @param {any} data - Additional data
   */
  debug(message, data = null) {
    if (process.env.NODE_ENV === "development") {
      const formattedMessage = this.formatMessage("debug", message, data);
      console.debug(formattedMessage);
    }
  }

  /**
   * Log info message
   * @param {string} message - Info message
   * @param {any} data - Additional data
   */
  info(message, data = null) {
    const formattedMessage = this.formatMessage("info", message, data);
    console.info(formattedMessage);
  }

  /**
   * Log warning message
   * @param {string} message - Warning message
   * @param {any} data - Additional data
   */
  warn(message, data = null) {
    const formattedMessage = this.formatMessage("warn", message, data);
    console.warn(formattedMessage);
  }

  /**
   * Log error message
   * @param {string} message - Error message
   * @param {any} error - Error object or data
   */
  error(message, error = null) {
    let errorData = null;

    if (error instanceof Error) {
      errorData = {
        name: error.name,
        message: error.message,
        stack:
          process.env.NODE_ENV === "development"
            ? error.stack
            : "[STACK_REDACTED]",
      };
    } else if (error) {
      errorData = error;
    }

    const formattedMessage = this.formatMessage("error", message, errorData);
    console.error(formattedMessage);
  }

  /**
   * Log healthcare audit event (HIPAA/PDPL compliance)
   * @param {string} action - Action performed
   * @param {string} userId - User ID performing action
   * @param {string} resourceType - Type of resource accessed
   * @param {string} resourceId - ID of resource (redacted)
   * @param {Object} metadata - Additional metadata
   */
  auditLog(action, userId, resourceType, resourceId, metadata = {}) {
    const auditData = {
      action: this.sanitize(action),
      userId: this.sanitize(userId),
      resourceType: this.sanitize(resourceType),
      resourceId: resourceId ? "[REDACTED_ID]" : null,
      timestamp: new Date().toISOString(),
      ipAddress: "[REDACTED_IP]",
      userAgent: "[REDACTED_UA]",
      ...this.redactSensitiveData(metadata),
    };

    const auditMessage = `AUDIT: ${action} on ${resourceType} by user ${userId}`;
    const formattedMessage = this.formatMessage(
      "audit",
      auditMessage,
      auditData
    );

    console.info(formattedMessage);

    // In production, send to secure audit logging service
    if (process.env.NODE_ENV === "production") {
      this.sendToAuditService(auditData);
    }
  }

  /**
   * Send audit data to secure logging service
   * @param {Object} auditData - Audit data to send
   */
  async sendToAuditService(auditData) {
    try {
      // Implementation would send to secure audit logging service
      // This is a placeholder for the actual implementation
      console.info(
        "[AUDIT_SERVICE] Would send audit data:",
        this.sanitize(auditData)
      );
    } catch (error) {
      console.error(
        "[AUDIT_SERVICE] Failed to send audit data:",
        this.sanitize(error.message)
      );
    }
  }

  /**
   * Log performance metrics
   * @param {string} operation - Operation name
   * @param {number} duration - Duration in milliseconds
   * @param {Object} metadata - Additional metadata
   */
  performance(operation, duration, metadata = {}) {
    const perfData = {
      operation: this.sanitize(operation),
      duration,
      timestamp: new Date().toISOString(),
      ...this.redactSensitiveData(metadata),
    };

    const perfMessage = `PERFORMANCE: ${operation} took ${duration}ms`;
    const formattedMessage = this.formatMessage("perf", perfMessage, perfData);

    console.info(formattedMessage);
  }

  /**
   * Log security event
   * @param {string} event - Security event type
   * @param {string} severity - Severity level
   * @param {Object} details - Event details
   */
  security(event, severity, details = {}) {
    const securityData = {
      event: this.sanitize(event),
      severity: this.sanitize(severity),
      timestamp: new Date().toISOString(),
      ...this.redactSensitiveData(details),
    };

    const securityMessage = `SECURITY: ${severity} - ${event}`;
    const formattedMessage = this.formatMessage(
      "security",
      securityMessage,
      securityData
    );

    console.warn(formattedMessage);

    // In production, send to security monitoring service
    if (process.env.NODE_ENV === "production") {
      this.sendToSecurityService(securityData);
    }
  }

  /**
   * Send security data to monitoring service
   * @param {Object} securityData - Security data to send
   */
  async sendToSecurityService(securityData) {
    try {
      // Implementation would send to security monitoring service
      console.warn(
        "[SECURITY_SERVICE] Would send security data:",
        this.sanitize(securityData)
      );
    } catch (error) {
      console.error(
        "[SECURITY_SERVICE] Failed to send security data:",
        this.sanitize(error.message)
      );
    }
  }
}

// Create default logger instance
const logger = new SecureLogger("BrainSAIT-Portal");

// Export both class and default instance
export { SecureLogger };
export default logger;
