import { Link } from 'react-router-dom';
import { Activity, Shield, Zap, BarChart2 } from 'lucide-react';

const Home = () => {
  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32 relative z-10">
        <div className="text-center">
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6">
            <span className="block">Advanced Security</span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-[var(--primary-start)] to-[var(--primary-end)]">
              Anomaly Detection
            </span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-400">
            Protect your network with AI-driven insights. Detect, analyze, and mitigate threats in real-time with our state-of-the-art CNS platform.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link to="/signup" className="btn-primary text-lg px-8 py-3 shadow-cyan-500/20">
              Get Started
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              Live Demo
            </Link>
          </div>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card text-center p-8 hover:bg-white/5">
                <div className="bg-indigo-500/10 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <Zap className="w-8 h-8 text-indigo-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Real-time Analysis</h3>
                <p className="text-gray-400">Instant processing of network logs to identify suspicious patterns immediately.</p>
            </div>
            <div className="card text-center p-8 hover:bg-white/5">
                <div className="bg-cyan-500/10 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <Shield className="w-8 h-8 text-cyan-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Secure & Private</h3>
                <p className="text-gray-400">Your data is processed securely with enterprise-grade encryption and privacy controls.</p>
            </div>
            <div className="card text-center p-8 hover:bg-white/5">
                <div className="bg-orange-500/10 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <BarChart2 className="w-8 h-8 text-orange-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Visual Reporting</h3>
                <p className="text-gray-400">Comprehensive dashboards with intuitive charts and detailed actionable reports.</p>
            </div>
        </div>
      </div>

      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-0 pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/10 blur-[100px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/10 blur-[100px]" />
      </div>
    </div>
  );
};

export default Home;
