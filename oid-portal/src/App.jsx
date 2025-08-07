import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";
import { Box, CircularProgress, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { useEffect, useState } from "react";
import { HelmetProvider } from "react-helmet-async";
import { Toaster } from "react-hot-toast";
import { QueryClient, QueryClientProvider } from "react-query";
import { Routes, Route, BrowserRouter as Router } from "react-router-dom";
import { prefixer } from "stylis";
import rtlPlugin from "stylis-plugin-rtl";

// Import UNIFIED components (ULTRATHINK CONSOLIDATION)
import Layout from "./components/Layout";
import RevolutionaryHealthcareDashboard from "./components/RevolutionaryHealthcareDashboard";
import UnifiedPortalRouter from "./components/UnifiedPortalRouter";
import UnifiedWorkspace from "./pages/UnifiedWorkspace"; // Main workspace entry point
import OidTree from "./pages/OidTree"; // Now uses optimal modular architecture

// Essential utility pages
import ChatAssistant from "./pages/ChatAssistant";
import EditBadge from "./pages/EditBadge";
import RegisterBadge from "./pages/RegisterBadge";
import TestPage from "./pages/TestPage";

// Import hooks and contexts
import { AuthProvider } from "./contexts/AuthContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import { UnifiedHealthcareProvider } from "./contexts/UnifiedHealthcareContext";
import { useLanguage } from "./hooks/useLanguage";

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Create RTL cache for Arabic support
const rtlCache = createCache({
  key: "muirtl",
  stylisPlugins: [prefixer, rtlPlugin],
});

const ltrCache = createCache({
  key: "muiltr",
});

function AppContent() {
  const { language: _language, isRTL } = useLanguage();
  const [isLoading, setIsLoading] = useState(true);

  // Enhanced theme with Arabic support and healthcare colors
  const theme = createTheme({
    direction: isRTL ? "rtl" : "ltr",
    palette: {
      mode: "dark",
      primary: {
        main: "#00b4d8", // BrainSAIT Blue
        light: "#48cae4",
        dark: "#0077b6",
        contrastText: "#ffffff",
      },
      secondary: {
        main: "#f72585", // Healthcare Pink
        light: "#ff6b9d",
        dark: "#c41e3a",
        contrastText: "#ffffff",
      },
      success: {
        main: "#06d6a0", // Saudi Green
        light: "#40e0d0",
        dark: "#048a81",
      },
      warning: {
        main: "#ffd166", // Warning Yellow
        light: "#ffe066",
        dark: "#ffb700",
      },
      error: {
        main: "#f72585",
        light: "#ff6b9d",
        dark: "#c41e3a",
      },
      background: {
        default: "#0f1419",
        paper: "#1a1f2e",
      },
      text: {
        primary: "#ffffff",
        secondary: "#b0bec5",
      },
    },
    typography: {
      fontFamily: isRTL
        ? '"Noto Sans Arabic", "Cairo", "Tajawal", "Arial", sans-serif'
        : '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontSize: "2.5rem",
        fontWeight: 700,
        lineHeight: 1.2,
      },
      h2: {
        fontSize: "2rem",
        fontWeight: 600,
        lineHeight: 1.3,
      },
      h3: {
        fontSize: "1.75rem",
        fontWeight: 600,
        lineHeight: 1.4,
      },
      h4: {
        fontSize: "1.5rem",
        fontWeight: 500,
        lineHeight: 1.4,
      },
      h5: {
        fontSize: "1.25rem",
        fontWeight: 500,
        lineHeight: 1.5,
      },
      h6: {
        fontSize: "1rem",
        fontWeight: 500,
        lineHeight: 1.5,
      },
      body1: {
        fontSize: "1rem",
        lineHeight: 1.6,
      },
      body2: {
        fontSize: "0.875rem",
        lineHeight: 1.5,
      },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            scrollbarColor: "#6b6b6b #2b2b2b",
            "&::-webkit-scrollbar, & *::-webkit-scrollbar": {
              backgroundColor: "#2b2b2b",
              width: "8px",
            },
            "&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb": {
              borderRadius: 8,
              backgroundColor: "#6b6b6b",
              minHeight: 24,
            },
          },
          "@font-face": [
            {
              fontFamily: "Cairo",
              fontStyle: "normal",
              fontDisplay: "swap",
              fontWeight: 400,
              src: `url('https://fonts.googleapis.com/css2?family=Cairo:wght@200;300;400;500;600;700;800;900&display=swap')`,
            },
            {
              fontFamily: "Noto Sans Arabic",
              fontStyle: "normal",
              fontDisplay: "swap",
              fontWeight: 400,
              src: `url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@100;200;300;400;500;600;700;800;900&display=swap')`,
            },
          ],
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            textTransform: "none",
            fontWeight: 500,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            backgroundColor: "#1a1f2e",
            border: "1px solid #2d3748",
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            "& .MuiOutlinedInput-root": {
              borderRadius: 8,
            },
          },
        },
      },
    },
  });

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <CacheProvider value={isRTL ? rtlCache : ltrCache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <HelmetProvider>
          <Router>
            <Layout>
              <Routes>
                {/* REVOLUTIONARY HEALTHCARE DASHBOARD */}
                <Route
                  path="/revolutionary"
                  element={<RevolutionaryHealthcareDashboard />}
                />

                {/* UNIFIED HEALTHCARE WORKSPACE - Single Entry Point */}
                <Route path="/" element={<UnifiedWorkspace />} />
                <Route path="/workspace" element={<UnifiedWorkspace />} />
                <Route path="/dashboard" element={<UnifiedWorkspace />} />

                {/* Essential OID Management Functions */}
                <Route path="/oid-tree" element={<OidTree />} />
                <Route path="/register" element={<RegisterBadge />} />
                <Route path="/edit/:oid" element={<EditBadge />} />
                <Route path="/chat" element={<ChatAssistant />} />
                <Route path="/test" element={<TestPage />} />

                {/* UNIFIED HEALTHCARE PORTALS - Role-based Access */}
                <Route path="/portals/*" element={<UnifiedPortalRouter />} />
                <Route
                  path="/doctor-portal/*"
                  element={<UnifiedPortalRouter />}
                />
                <Route
                  path="/nurse-portal/*"
                  element={<UnifiedPortalRouter />}
                />
                <Route
                  path="/patient-portal/*"
                  element={<UnifiedPortalRouter />}
                />
                <Route
                  path="/admin-dashboard/*"
                  element={<UnifiedPortalRouter />}
                />

                {/* Legacy Routes - Redirect to Unified Workspace with Context */}
                <Route path="/healthcare" element={<UnifiedWorkspace />} />
                <Route path="/nphies" element={<UnifiedWorkspace />} />
                <Route path="/rcm" element={<UnifiedWorkspace />} />
                <Route path="/ai-analytics" element={<UnifiedWorkspace />} />
                <Route path="/training" element={<UnifiedWorkspace />} />
                <Route path="/bot-dashboard" element={<UnifiedWorkspace />} />
                <Route path="/home" element={<UnifiedWorkspace />} />

                {/* Legacy Routes - All redirect to Unified Workspace */}
                <Route path="/legacy/home" element={<UnifiedWorkspace />} />
                <Route
                  path="/legacy/healthcare"
                  element={<UnifiedWorkspace />}
                />
                <Route path="/legacy/nphies" element={<UnifiedWorkspace />} />
                <Route path="/legacy/rcm" element={<UnifiedWorkspace />} />
                <Route
                  path="/legacy/ai-analytics"
                  element={<UnifiedWorkspace />}
                />
                <Route path="/legacy/training" element={<UnifiedWorkspace />} />
                <Route
                  path="/legacy/bot-dashboard"
                  element={<UnifiedWorkspace />}
                />
              </Routes>
            </Layout>
          </Router>
          <Toaster
            position={isRTL ? "top-left" : "top-right"}
            toastOptions={{
              duration: 4000,
              style: {
                background: "#1a1f2e",
                color: "#ffffff",
                border: "1px solid #2d3748",
                borderRadius: "8px",
                fontFamily: theme.typography.fontFamily,
              },
            }}
          />
        </HelmetProvider>
      </ThemeProvider>
    </CacheProvider>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <LanguageProvider>
          <UnifiedHealthcareProvider>
            <AppContent />
          </UnifiedHealthcareProvider>
        </LanguageProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
