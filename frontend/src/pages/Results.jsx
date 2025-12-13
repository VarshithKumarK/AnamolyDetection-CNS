import { useLocation, Navigate } from 'react-router-dom';
import ResultsTable from '../components/ResultsTable';
import { useResults } from '../context/ResultsContext';
import { useEffect, useState } from 'react';
import { Clock, FileText, Loader } from 'lucide-react';

const Results = () => {
    const location = useLocation();
    const { resultsHistory, addResult, getJobDetails, loading: historyLoading } = useResults();
    const [selectedResult, setSelectedResult] = useState(null);
    const [loadingDetails, setLoadingDetails] = useState(false);

    const handleSelectResult = async (jobSummary) => {
        // If we already have the full results (e.g. from fresh upload or previous fetch), just set it
        if (jobSummary.results && jobSummary.results.results) {
            setSelectedResult(jobSummary);
            return;
        }

        // Otherwise fetch full details
        setLoadingDetails(true);
        try {
            const fullJob = await getJobDetails(jobSummary._id);
            // augment the history item with full results so we don't fetch again?
            // simpler to just set selectedResult for now
            setSelectedResult(fullJob);
        } catch (error) {
            console.error("Failed to load job details", error);
        } finally {
            setLoadingDetails(false);
        }
    };

    // Initial load: prefer location state (fresh upload), else first history item
    useEffect(() => {
        const init = async () => {
            if (location.state?.results) {
                // New upload just finished
                // Add to history (optimistic) and select it
                addResult(location.state.results);
                setSelectedResult(location.state.results);
            } else if (resultsHistory.length > 0 && !selectedResult) {
                // Load first historical item
                handleSelectResult(resultsHistory[0]);
            }
        };
        init();
    }, [location.state, resultsHistory, addResult]); // Keep deps minimal

    // If still strictly no history and not loading
    if (!selectedResult && resultsHistory.length === 0 && !historyLoading) {
        return (
            <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8 text-center">
                <p className="text-gray-400 text-lg">No results found. Please upload a file to start analysis.</p>
                <button onClick={() => window.history.back()} className="mt-4 btn-secondary">Go Back</button>
            </div>
        );
    }

    const currentData = selectedResult; 
    const results = currentData?.results?.results || [];

    return (
        <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-white mb-6">Analysis Results</h1>
            
            <div className="flex flex-col md:flex-row gap-6">
                {/* History Sidebar */}
                <div className="md:w-1/4 space-y-4">
                    <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                        <h2 className="text-xl font-semibold text-gray-200 mb-4 flex items-center">
                            <Clock className="w-5 h-5 mr-2 text-indigo-400" />
                            History
                        </h2>
                        {historyLoading ? (
                            <div className="flex justify-center py-4">
                                <Loader className="w-6 h-6 animate-spin text-indigo-500"/>
                            </div>
                        ) : (
                            <div className="space-y-2 max-h-[60vh] overflow-y-auto">
                                {resultsHistory.map((item, index) => (
                                    <button
                                        key={item._id || index}
                                        onClick={() => handleSelectResult(item)}
                                        className={`w-full text-left p-3 rounded-lg flex items-center transition-all ${
                                            ((selectedResult && selectedResult._id === item._id) || (selectedResult === item))
                                                ? 'bg-indigo-600/20 border-indigo-500/50 border shadow-lg shadow-indigo-500/10' 
                                                : 'bg-gray-800 hover:bg-gray-750 border border-transparent hover:border-gray-600'
                                        }`}
                                    >
                                        <FileText className="w-4 h-4 mr-3 text-gray-400 flex-shrink-0" />
                                        <div className="overflow-hidden">
                                            <div className="text-sm font-medium text-gray-200 truncate">
                                                {item.filename || `Analysis ${index + 1}`}
                                            </div>
                                            <div className="text-xs text-gray-500 mt-1">
                                                {item.completedAt ? new Date(item.completedAt).toLocaleString() : 'Just now'}
                                            </div>
                                            <div className="mt-1 flex gap-2">
                                                <span className="text-[10px] bg-red-900/30 text-red-300 px-1.5 rounded border border-red-900/50">
                                                    {item.results?.summary?.anomalies ?? item.summary?.anomalies ?? 0} Anomalies
                                                </span>
                                            </div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Main Content */}
                <div className="md:w-3/4">
                    <div className="card p-1 min-h-[400px]">
                        {loadingDetails ? (
                             <div className="flex flex-col items-center justify-center h-full py-20 text-gray-400">
                                <Loader className="w-10 h-10 animate-spin text-indigo-500 mb-4"/>
                                <p>Loading analysis details...</p>
                             </div>
                        ) : (
                            <ResultsTable results={results} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Results;
