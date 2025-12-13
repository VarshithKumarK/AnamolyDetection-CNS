import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4">
          <h1 className="text-3xl font-bold text-red-500 mb-4">Something went wrong.</h1>
          <div className="bg-gray-800 p-6 rounded-lg max-w-2xl w-full overflow-auto">
            <h2 className="text-xl font-semibold mb-2">Error: {this.state.error?.toString()}</h2>
            <details className="whitespace-pre-wrap text-gray-400 text-sm">
              {this.state.errorInfo?.componentStack}
            </details>
          </div>
          <button 
            onClick={() => window.location.href = '/'} 
            className="mt-6 px-6 py-2 bg-indigo-600 rounded hover:bg-indigo-700"
          >
            Go to Home
          </button>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;
