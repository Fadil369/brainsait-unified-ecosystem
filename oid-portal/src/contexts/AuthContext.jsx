import { createContext, useContext, useEffect, useState } from "react";
import logger from "../utils/logger.js";
import {
  generateCSRFToken,
  isValidEmail,
  sanitizeInput,
  validateCSRFToken,
} from "../utils/security.js";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [csrfToken, setCsrfToken] = useState(null);

  // Generate CSRF token on component mount
  useEffect(() => {
    const token = generateCSRFToken();
    setCsrfToken(token);
    sessionStorage.setItem("brainsait-csrf-token", token);
  }, []);

  // Authenticate user with enhanced security
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("brainsait-token");
        if (token) {
          // Simulate user data - replace with actual API call
          const userData = {
            id: "user_001",
            name: "Dr. Ahmed Al-Rashid",
            nameAr: "د. أحمد الراشد",
            email: "ahmed.rashid@brainsait.sa",
            role: "physician",
            accessLevel: "high",
            organization: "King Faisal Specialist Hospital",
            nphiesId: "NPHIES_DR_001",
            avatar: null,
          };
          setUser(userData);
          setIsAuthenticated(true);

          logger.auditLog(
            "AUTH_CHECK_SUCCESS",
            userData.id,
            "USER_SESSION",
            userData.id,
            { role: userData.role, organization: userData.organization }
          );
        }
      } catch (error) {
        logger.error("Auth check failed", error);
        logger.security("AUTH_CHECK_FAILED", "medium", {
          error: error.message,
        });
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    try {
      setIsLoading(true);

      // Validate input
      if (!credentials.email || !credentials.password) {
        const error = "Email and password are required";
        logger.security("LOGIN_ATTEMPT_INVALID_INPUT", "low", {
          email: sanitizeInput(credentials.email),
        });
        return { success: false, error };
      }

      // Validate email format
      if (!isValidEmail(credentials.email)) {
        const error = "Invalid email format";
        logger.security("LOGIN_ATTEMPT_INVALID_EMAIL", "medium", {
          email: sanitizeInput(credentials.email),
        });
        return { success: false, error };
      }

      // Validate CSRF token
      const storedCsrfToken = sessionStorage.getItem("brainsait-csrf-token");
      if (!validateCSRFToken(credentials.csrfToken, storedCsrfToken)) {
        const error = "Invalid security token";
        logger.security("LOGIN_ATTEMPT_CSRF_FAILURE", "high", {
          email: sanitizeInput(credentials.email),
          providedToken: !!credentials.csrfToken,
          storedToken: !!storedCsrfToken,
        });
        return { success: false, error };
      }

      // Sanitize inputs
      const sanitizedEmail = sanitizeInput(credentials.email);

      logger.auditLog("LOGIN_ATTEMPT", "UNKNOWN", "USER_SESSION", null, {
        email: sanitizedEmail,
      });

      // Simulate API call with security delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const token = "mock-jwt-token";
      const userData = {
        id: "user_001",
        name: "Dr. Ahmed Al-Rashid",
        nameAr: "د. أحمد الراشد",
        email: sanitizedEmail,
        role: "physician",
        accessLevel: "high",
        organization: "King Faisal Specialist Hospital",
        nphiesId: "NPHIES_DR_001",
        avatar: null,
      };

      localStorage.setItem("brainsait-token", token);
      setUser(userData);
      setIsAuthenticated(true);

      // Generate new CSRF token after successful login
      const newCsrfToken = generateCSRFToken();
      setCsrfToken(newCsrfToken);
      sessionStorage.setItem("brainsait-csrf-token", newCsrfToken);

      logger.auditLog(
        "LOGIN_SUCCESS",
        userData.id,
        "USER_SESSION",
        userData.id,
        {
          role: userData.role,
          organization: userData.organization,
          email: sanitizedEmail,
        }
      );

      return { success: true, user: userData, csrfToken: newCsrfToken };
    } catch (error) {
      logger.error("Login failed", error);
      logger.security("LOGIN_ERROR", "high", {
        email: sanitizeInput(credentials.email),
        error: error.message,
      });
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    const userId = user?.id;

    try {
      localStorage.removeItem("brainsait-token");
      sessionStorage.removeItem("brainsait-csrf-token");

      setUser(null);
      setIsAuthenticated(false);
      setCsrfToken(null);

      logger.auditLog(
        "LOGOUT_SUCCESS",
        userId || "UNKNOWN",
        "USER_SESSION",
        userId,
        {}
      );
    } catch (error) {
      logger.error("Logout failed", error);
      logger.security("LOGOUT_ERROR", "medium", {
        userId: userId || "UNKNOWN",
        error: error.message,
      });
    }
  };

  const refreshCSRFToken = () => {
    const newToken = generateCSRFToken();
    setCsrfToken(newToken);
    sessionStorage.setItem("brainsait-csrf-token", newToken);
    return newToken;
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    csrfToken,
    login,
    logout,
    refreshCSRFToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
