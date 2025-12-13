import { useEffect, useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import StatsCard from '../components/StatsCard';
import ResultsTable from '../components/ResultsTable';
import { AlertCircle, CheckCircle, Database } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const location = useLocation();
  const [data, setData] = useState(null);

  useEffect(() => {
    // Check for results passed via navigation
    if (location.state?.results) {
      setData(location.state.results);
      // Optional: Persist to localStorage
      localStorage.setItem('lastAnalysis', JSON.stringify(location.state.results));
    } else {
        // Check localStorage
        const stored = localStorage.getItem('lastAnalysis');
        if (stored) {
            try {
                setData(JSON.parse(stored));
            } catch (e) {
                console.error("Error parsing stored analysis", e);
            }
        }
    }
  }, [location.state]);

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <h2 className="text-2xl font-semibold text-gray-700">No Analysis Data Available</h2>
        <p className="mt-2 text-gray-500">Run a new analysis to see results here.</p>
        <Link to="/upload" className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
            Go to Upload
        </Link>
      </div>
    );
  }

  /* 
     Data structure from backend (Job object):
     {
        summary: { total_rows, anomalies, mode },
        results: { 
            summary: { ... }, 
            results: [ ...array of rows... ] 
        }
     }
  */
  const summary = data.summary || { total_rows: 0, anomalies: 0 };
  // Check if data.results is the ML payload (most likely) or the array itself (legacy support)
  const resultsArray = Array.isArray(data.results) ? data.results : (data.results?.results || []);

  // Prepare Chart Data
  const anomalyCount = summary.anomalies || 0;
  const normalCount = (summary.total_rows || 0) - anomalyCount;
  
  const barData = [
    { name: 'Normal', count: normalCount },
    { name: 'Anomaly', count: anomalyCount },
  ];

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dashboard Overview</h1>
        <p className="text-gray-400 mt-2">Latest analysis results and system metrics</p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3 mb-8">
        <StatsCard 
            title="Total Processed" 
            value={summary.total_rows} 
            icon={Database}
            color="text-blue-400"
        />
        <StatsCard 
            title="Anomalies Found" 
            value={summary.anomalies} 
            icon={AlertCircle}
            color="text-red-400"
        />
        <StatsCard 
            title="Anomaly Rate" 
            value={`${((summary.anomalies / summary.total_rows) * 100).toFixed(2)}%`} 
            icon={CheckCircle}
            color={summary.anomalies > 0 ? "text-yellow-400" : "text-green-400"}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="card">
          <h3 className="text-lg font-medium text-white mb-6">Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#f8fafc' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Legend wrapperStyle={{ color: '#cbd5e1' }} />
              <Bar dataKey="count" fill="#6366f1" name="Records" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        {/* Placeholder for Histogram or Time Series */}
         <div className="card flex flex-col items-center justify-center text-center p-8">
             <div className="bg-white/5 p-4 rounded-full mb-4">
                <Database className="w-8 h-8 text-gray-500" />
             </div>
             <h4 className="text-white font-medium">Detailed Analysis</h4>
             <p className="text-gray-400 mt-2 text-sm">Upload more data to generate advanced insights and trendlines.</p>
             <Link to="/upload" className="mt-6 btn-secondary text-xs">
                Start New Analysis
             </Link>
        </div>
      </div>

      {/* Results Table */}
      <div className="mt-8">
         <h3 className="text-lg font-bold text-white mb-4">Recent Anomalies</h3>
         <ResultsTable results={resultsArray} />
      </div>
    </div>
  );
};

export default Dashboard;
