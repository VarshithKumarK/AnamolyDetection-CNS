import { X, AlertTriangle, CheckCircle, Activity, BarChart2 } from 'lucide-react';

const ResultModal = ({ isOpen, onClose, data }) => {
  if (!isOpen || !data) return null;

  const isAnomaly = ['Anomaly', 'ANOMALY'].includes(data.final_label);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden" aria-labelledby="slide-over-title" role="dialog" aria-modal="true">
      <div className="absolute inset-0 overflow-hidden">
        {/* Backdrop */}
        <div 
            className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm transition-opacity" 
            onClick={onClose} 
        />

        <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div className="pointer-events-auto w-screen max-w-2xl transform transition-transform duration-500 ease-in-out sm:duration-700">
            <div className="flex h-full flex-col overflow-y-scroll bg-[#0f111a] border-l border-gray-800 shadow-2xl">
              
              {/* Header */}
              <div className="px-4 py-6 sm:px-6 border-b border-gray-800 bg-[#131620]">
                <div className="flex items-start justify-between">
                  <div>
                      <h2 className="text-2xl font-bold text-white tracking-tight" id="slide-over-title">
                        Analysis Details
                      </h2>
                      <p className="mt-1 text-sm text-gray-400">
                        Transaction Index: <span className="font-mono text-indigo-400">#{data.index}</span>
                      </p>
                  </div>
                  <div className="ml-3 flex h-7 items-center">
                    <button
                      type="button"
                      className="rounded-full bg-gray-800 p-2 text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 ring-offset-2 ring-offset-[#0f111a] transition-all"
                      onClick={onClose}
                    >
                      <span className="sr-only">Close panel</span>
                      <X className="h-5 w-5" aria-hidden="true" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="relative flex-1 px-4 py-6 sm:px-6 space-y-8">
                
                {/* Verdict Section */}
                <div className={`rounded-2xl p-6 border ${isAnomaly ? 'bg-red-900/10 border-red-900/30' : 'bg-emerald-900/10 border-emerald-900/30'}`}>
                    <div className="flex items-center space-x-4">
                        <div className={`p-3 rounded-full ${isAnomaly ? 'bg-red-500/20 text-red-500' : 'bg-emerald-500/20 text-emerald-500'}`}>
                            {isAnomaly ? <AlertTriangle className="w-8 h-8"/> : <CheckCircle className="w-8 h-8"/>}
                        </div>
                        <div>
                            <p className={`text-sm font-medium uppercase tracking-wider ${isAnomaly ? 'text-red-400' : 'text-emerald-400'}`}>
                                Final Verdict
                            </p>
                            <h3 className={`text-3xl font-extrabold ${isAnomaly ? 'text-white' : 'text-white'}`}>
                                {isAnomaly ? 'ANOMALY DETECTED' : 'NORMAL BEHAVIOR'}
                            </h3>
                        </div>
                    </div>
                </div>

                {/* Scores Grid */}
                <div>
                     <h3 className="text-lg font-medium text-gray-200 mb-4 flex items-center">
                        <Activity className="w-5 h-5 mr-2 text-indigo-400"/>
                        Model Scores
                     </h3>
                     <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700/50">
                            <p className="text-sm text-gray-400 mb-1">Autoencoder (AE) Score</p>
                            <div className="flex items-baseline space-x-2">
                                <span className="text-2xl font-bold text-white font-mono">{data.ae_score?.toFixed(4)}</span>
                                <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${data.ae_label === 1 ? 'bg-red-900/30 text-red-300' : 'bg-emerald-900/30 text-emerald-300'}`}>
                                    {data.ae_label === 1 ? 'Anomaly' : 'Normal'}
                                </span>
                            </div>
                        </div>
                         <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700/50">
                            <p className="text-sm text-gray-400 mb-1">ISO Latent Score</p>
                             <div className="flex items-baseline space-x-2">
                                <span className="text-2xl font-bold text-white font-mono">{data.iso_latent_score?.toFixed(4)}</span>
                                <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${data.iso_latent_label === 1 ? 'bg-red-900/30 text-red-300' : 'bg-emerald-900/30 text-emerald-300'}`}>
                                    {data.iso_latent_label === 1 ? 'Anomaly' : 'Normal'}
                                </span>
                            </div>
                        </div>
                     </div>
                </div>

                {/* Explanation */}
                <div>
                    <h3 className="text-lg font-medium text-gray-200 mb-4 flex items-center">
                        <BarChart2 className="w-5 h-5 mr-2 text-indigo-400"/>
                        Detailed Analysis
                    </h3>
                    <div className="bg-gray-800/30 rounded-xl border border-gray-700/50 overflow-hidden">
                        
                        {/* Triggered By */}
                        {data.explanation?.triggered_by?.length > 0 && (
                            <div className="p-5 border-b border-gray-700/50">
                                <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Triggered By</h4>
                                <div className="flex flex-wrap gap-2">
                                    {data.explanation.triggered_by.map((trigger, idx) => (
                                        <span key={idx} className="px-3 py-1.5 rounded-lg text-sm font-medium bg-red-500/10 text-red-400 border border-red-500/20 shadow-sm">
                                            {trigger}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Raw Explanation Content */}
                        <div className="p-5">
                            {typeof data.explanation === 'string' ? (
                                <p className="text-gray-300 leading-relaxed">{data.explanation}</p>
                            ) : (
                                <div className="space-y-4">
                                     {data.explanation?.scores && (
                                       <div>
                                           <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Detailed Metrics</h4>
                                           <div className="space-y-2">
                                               {Object.entries(data.explanation.scores).map(([key, value]) => (
                                                   <div key={key} className="flex justify-between items-center py-2 border-b border-gray-700/30 last:border-0 hover:bg-white/5 px-2 rounded -mx-2 transition-colors">
                                                       <span className="text-gray-300 text-sm font-medium">{key.replace(/_/g, ' ')}</span>
                                                       <span className="font-mono text-indigo-300 font-semibold">{typeof value === 'number' ? value.toFixed(4) : value}</span>
                                                   </div>
                                               ))}
                                           </div>
                                       </div>
                                   )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                 {/* Raw Data (Collapsible/Optional) */}
                 {data.sample && (
                     <div className="pt-4 border-t border-gray-800">
                        <details className="group">
                            <summary className="flex items-center cursor-pointer text-gray-500 hover:text-indigo-400 transition-colors list-none text-sm font-medium">
                                <span className="mr-2 transform group-open:rotate-90 transition-transform">▶</span>
                                View Raw Features
                            </summary>
                            <div className="mt-4">
                                <pre className="bg-[#0a0c10] p-4 rounded-lg text-xs text-gray-400 overflow-x-auto font-mono border border-gray-800">
                                    {JSON.stringify(data.sample, null, 2)}
                                </pre>
                            </div>
                        </details>
                     </div>
                 )}

              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultModal;
