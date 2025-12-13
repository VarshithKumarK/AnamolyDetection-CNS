import { useState } from 'react';
import FileUploader from '../components/FileUploader';
import mlService from '../api/mlService';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(0);
    try {
      const result = await mlService.uploadFile(file, (event) => {
        const percent = Math.round((event.loaded * 100) / event.total);
        setProgress(percent);
      });
      toast.success('File uploaded and analyzed successfully!');
      // Assuming result contains the analysis data, we can navigate to dashboard or results
      // For now, let's navigate to dashboard which presumably fetches latest results
      // Or we can pass state to dashboard
      // The prompt says "Show upload progress spinner, then show returned results."
      // Let's pass the result object to the results page or dashboard
      localStorage.setItem('lastAnalysis', JSON.stringify(result));
      navigate('/results', { state: { results: result } });
    } catch (error) {
      console.error(error);
      toast.error('Upload failed');
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white mb-8">Upload CSV for Anomaly Detection</h1>
      
      <div className="card p-8">
        <FileUploader onFileSelect={setFile} />
        
        {uploading && (
           <div className="mt-8 animate-fade">
             <div className="flex justify-between mb-2">
               <span className="text-sm font-medium text-indigo-400">Analyzing...</span>
               <span className="text-sm font-medium text-indigo-400">{progress}%</span>
             </div>
             <div className="w-full bg-gray-700 rounded-full h-2.5 overflow-hidden">
               <div className="bg-gradient-to-r from-[var(--primary-start)] to-[var(--primary-end)] h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
             </div>
           </div>
        )}

        <div className="mt-8 flex justify-end">
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`btn-primary ${(!file || uploading) ? 'opacity-50 cursor-not-allowed transform-none' : ''}`}
          >
            {uploading ? 'Processing...' : 'Run Analysis'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Upload;
