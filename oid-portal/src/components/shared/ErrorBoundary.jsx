// React import removed

/**
 * Error Boundary Component
 * Catches JavaScript errors in child components and displays fallback UI
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Log error to monitoring service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl text-red-600">⚠️</span>
            </div>
            
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Something went wrong
            </h2>
            
            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>
            
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Refresh Page
              </button>
              
              <button
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
                className="w-full px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Try Again
              </button>
            </div>
            
            {/* Development error details */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                  Error Details (Development Only)
                </summary>
                <div className="mt-2 p-4 bg-gray-100 rounded text-xs text-gray-700 overflow-auto">
                  <div className="font-medium mb-2">Error:</div>
                  <pre className="whitespace-pre-wrap">{this.state.error.toString()}</pre>
                  
                  {this.state.errorInfo.componentStack && (
                    <>
                      <div className="font-medium mt-4 mb-2">Component Stack:</div>
                      <pre className="whitespace-pre-wrap">{this.state.errorInfo.componentStack}</pre>
                    </>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for easy healthcare error boundary usage
export const withHealthcareErrorBoundary = (Component, healthcareContext) => {
  return function WrappedComponent(props) {
    return (
      <ErrorBoundary 
        healthcareContext={healthcareContext}
        userId={props.userId}
      >
        <Component {...props} />
      </ErrorBoundary>
    );
  };
};

// Specialized error boundaries for different healthcare contexts
export const DoctorPortalErrorBoundary = ({ children, ...props }) => (
  <ErrorBoundary healthcareContext="doctor_portal" {...props}>
    {children}
  </ErrorBoundary>
);

export const PatientPortalErrorBoundary = ({ children, ...props }) => (
  <ErrorBoundary healthcareContext="patient_portal" {...props}>
    {children}
  </ErrorBoundary>
);

export const NPHIESErrorBoundary = ({ children, ...props }) => (
  <ErrorBoundary healthcareContext="nphies_integration" {...props}>
    {children}
  </ErrorBoundary>
);

export const RCMErrorBoundary = ({ children, ...props }) => (
  <ErrorBoundary healthcareContext="rcm_operations" {...props}>
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;