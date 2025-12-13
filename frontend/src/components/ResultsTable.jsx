import { useState, useMemo } from 'react';
import { usePagination, DOTS } from '../hooks/usePagination';
import ResultModal from './ResultModal';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const PageSize = 10;

const ResultsTable = ({ results = [] }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [filter, setFilter] = useState('all'); // all, anomaly, normal
  const [selectedRow, setSelectedRow] = useState(null);

  const filteredData = useMemo(() => {
    const data = Array.isArray(results) ? results : [];
    if (filter === 'all') return data;
    return data.filter(item => {
      if (filter === 'anomaly') return ['Anomaly', 'ANOMALY'].includes(item.final_label);
      return ['Normal', 'NORMAL'].includes(item.final_label);
    });
  }, [results, filter]);

  const currentTableData = useMemo(() => {
    const firstPageIndex = (currentPage - 1) * PageSize;
    const lastPageIndex = firstPageIndex + PageSize;
    return filteredData.slice(firstPageIndex, lastPageIndex);
  }, [currentPage, filteredData]);

  const paginationRange = usePagination({
    currentPage,
    totalCount: filteredData.length,
    siblingCount: 1,
    pageSize: PageSize
  });

  const onNext = () => {
    setCurrentPage(currentPage + 1);
  };

  const onPrevious = () => {
    setCurrentPage(currentPage - 1);
  };

  if(!results.length) {
      return <div className="text-center py-10 text-gray-500">No results found.</div>
  }

  return (
    <div className="flex flex-col">
      <div className="mb-6 flex flex-col sm:flex-row items-center justify-between">
         <h3 className="text-2xl font-bold text-white tracking-tight">Analysis Results</h3>
         <div className="flex space-x-3 mt-4 sm:mt-0 w-full sm:w-auto">
             <div className="relative w-full sm:w-64">
                <select
                    value={filter}
                    onChange={(e) => {
                        setFilter(e.target.value);
                        setCurrentPage(1);
                    }}
                    className="block w-full pl-4 pr-10 py-2.5 text-base bg-gray-900/50 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 rounded-xl text-gray-200 shadow-lg transition-all appearance-none cursor-pointer hover:bg-gray-800/80"
                >
                    <option value="all">Show All Results</option>
                    <option value="anomaly">Show Anomalies Only</option>
                    <option value="normal">Show Normal Only</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-400">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
             </div>
         </div>
      </div>

      <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
          <div className="shadow overflow-hidden border-b border-gray-700 sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-900/50">
                <tr>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Index</th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Verdict</th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">AE Score</th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">ISO Score</th>
                   <th scope="col" className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800/20 divide-y divide-gray-700/50">
                {currentTableData.map((row) => (
                  <tr key={row.index} onClick={() => setSelectedRow(row)} className="group hover:bg-indigo-900/10 cursor-pointer transition-all duration-200">
                    <td className="px-6 py-5 whitespace-nowrap text-sm font-medium text-gray-300 group-hover:text-white">
                      #{row.index}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                       {['Anomaly', 'ANOMALY'].includes(row.final_label) ? (
                           <span className="px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full bg-red-500/10 text-red-400 border border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.2)]">
                               ANOMALY
                           </span>
                       ) : (
                           <span className="px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                               NORMAL
                           </span>
                       )}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-sm text-gray-400 group-hover:text-gray-200 font-mono">
                      {row.ae_score?.toFixed(4)}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-sm text-gray-400 group-hover:text-gray-200 font-mono">
                      {row.iso_latent_score?.toFixed(4)}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-right text-sm font-medium">
                        <span className="text-indigo-400 group-hover:text-indigo-300 transition-colors">View Details &rarr;</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Pagination */}
      <div className="bg-[var(--card)] px-4 py-3 flex items-center justify-between border-t border-gray-700 sm:px-6 mt-4 rounded-b-lg">
        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
           <div>
            <p className="text-sm text-gray-400">
              Showing <span className="font-medium text-white">{(currentPage - 1) * PageSize + 1}</span> to <span className="font-medium text-white">{Math.min(currentPage * PageSize, filteredData.length)}</span> of{' '}
              <span className="font-medium text-white">{filteredData.length}</span> results
            </p>
          </div>
          <div>
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
               <button
                  onClick={onPrevious}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-600 bg-gray-800 text-sm font-medium text-gray-400 hover:bg-gray-700 disabled:opacity-50"
               >
                 <span className="sr-only">Previous</span>
                 <ChevronLeft className="h-5 w-5" aria-hidden="true" />
               </button>
               {paginationRange && paginationRange.map((pageNumber, idx) => {
                   if (pageNumber === DOTS) {
                       return <span key={idx} className="relative inline-flex items-center px-4 py-2 border border-gray-600 bg-gray-800 text-sm font-medium text-gray-400">...</span>;
                   }
                   return (
                       <button
                           key={idx}
                           onClick={() => setCurrentPage(pageNumber)}
                           className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                               pageNumber === currentPage
                                   ? 'z-10 bg-indigo-600 border-indigo-600 text-white'
                                   : 'bg-gray-800 border-gray-600 text-gray-400 hover:bg-gray-700'
                           }`}
                       >
                           {pageNumber}
                       </button>
                   );
               })}
               <button
                  onClick={onNext}
                  disabled={currentPage === 0 || (paginationRange && currentPage === paginationRange[paginationRange.length - 1])}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-600 bg-gray-800 text-sm font-medium text-gray-400 hover:bg-gray-700 disabled:opacity-50"
               >
                 <span className="sr-only">Next</span>
                 <ChevronRight className="h-5 w-5" aria-hidden="true" />
               </button>
            </nav>
          </div>
        </div>
      </div>
      
      <ResultModal isOpen={!!selectedRow} onClose={() => setSelectedRow(null)} data={selectedRow} />
    </div>
  );
};

export default ResultsTable;
