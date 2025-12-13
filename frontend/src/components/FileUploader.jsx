import { useRef, useState } from 'react';
import { UploadCloud, FileText, X } from 'lucide-react';
import { toast } from 'react-toastify';

const FileUploader = ({ onFileSelect }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file');
      return;
    }
    setSelectedFile(file);
    onFileSelect(file);
  };

  const removeFile = () => {
    setSelectedFile(null);
    onFileSelect(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <label
          htmlFor="dropzone-file"
          className={`flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 ${
            dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <UploadCloud className="w-10 h-10 mb-3 text-gray-400" />
            <p className="mb-2 text-sm text-gray-500">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">CSV files only</p>
          </div>
          <input
            id="dropzone-file"
            type="file"
            className="hidden"
            accept=".csv"
            onChange={handleChange}
            ref={inputRef}
          />
        </label>
      ) : (
        <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
          <div className="flex items-center space-x-3">
             <FileText className="w-8 h-8 text-indigo-500" />
             <div>
               <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
               <p className="text-xs text-gray-500">{(selectedFile.size / 1024).toFixed(2)} KB</p>
             </div>
          </div>
          <button onClick={removeFile} className="p-1 rounded-full hover:bg-gray-100 text-gray-500 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
