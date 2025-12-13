import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Results from './pages/Results';
import Profile from './pages/Profile';
import PrivateRoute from './components/PrivateRoute';
import { AuthProvider } from './context/AuthContext';
import { ResultsProvider } from './context/ResultsContext';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <Router>
      <AuthProvider>
        <ResultsProvider>
          <ErrorBoundary>
            <div className="min-h-screen bg-[var(--bg)] text-white font-sans selection:bg-indigo-500/30">
              <Navbar />
              <div className="pt-16">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/signup" element={<Signup />} />
                  <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                  <Route path="/upload" element={<PrivateRoute><Upload /></PrivateRoute>} />
                  <Route path="/results" element={<PrivateRoute><Results /></PrivateRoute>} />
                  <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </div>
              <ToastContainer position="bottom-right" theme="dark" toastClassName="bg-gray-800 text-white" />
            </div>
          </ErrorBoundary>
        </ResultsProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
