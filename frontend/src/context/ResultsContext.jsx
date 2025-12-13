import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import jobsService from '../api/jobsService';

const ResultsContext = createContext();

export const useResults = () => {
    return useContext(ResultsContext);
};

export const ResultsProvider = ({ children }) => {
    const [resultsHistory, setResultsHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    
    const fetchHistory = useCallback(async () => {
        setLoading(true);
        try {
            const jobs = await jobsService.getJobs();
            if (Array.isArray(jobs)) {
                setResultsHistory(jobs);
            } else {
                console.error("Fetched jobs is not an array:", jobs);
                setResultsHistory([]);
            }
        } catch (error) {
            console.error("Failed to fetch jobs history", error);
            setResultsHistory([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    // We still keep addResult to optimistically update UI or for manual additions
    // But ideally we just re-fetch or prepend
    // We still keep addResult to optimistically update UI or for manual additions
    // But ideally we just re-fetch or prepend
    const addResult = useCallback((newResult) => {
        setResultsHistory(prev => {
             const exists = prev.some(r => r._id === newResult._id);
             if (exists) return prev;
             return [newResult, ...prev];
        });
    }, []);
    
    const getJobDetails = useCallback(async (id) => {
        try {
            return await jobsService.getJob(id);
        } catch (error) {
            console.error("Failed to fetch job details", error);
            throw error;
        }
    }, []);

    const clearHistory = useCallback(() => {
        // Implement delete all if needed, for now just clear local state
        setResultsHistory([]);
    }, []);

    return (
        <ResultsContext.Provider value={{ resultsHistory, addResult, clearHistory, getJobDetails, fetchHistory, loading }}>
            {children}
        </ResultsContext.Provider>
    );
};

export default ResultsProvider;
