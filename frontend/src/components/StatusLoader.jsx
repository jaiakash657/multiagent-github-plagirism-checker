import { useEffect, useState } from "react";
import { checkStatus, getResult } from "../api/api";
import ResultView from "./ResultView";

export default function StatusLoader({ jobId }) {
  const [status, setStatus] = useState("Checking...");
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 10;
      });
    }, 500);

    const interval = setInterval(async () => {
      try {
        const res = await checkStatus(jobId);
        setStatus(res.data.status);

        if (res.data.status === "SUCCESS") {
          setProgress(100);
          const finalRes = await getResult(jobId);
          setResult(finalRes.data.result);
          clearInterval(interval);
          clearInterval(progressInterval);
        }

        if (res.data.status === "FAILURE") {
          setResult({
            error: res.data.detail || "Task failed",
          });
          clearInterval(interval);
          clearInterval(progressInterval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);

    return () => {
      clearInterval(interval);
      clearInterval(progressInterval);
    };
  }, [jobId]);

  const getStatusConfig = () => {
    switch(status) {
      case "SUCCESS":
        return {
          color: "from-emerald-500 to-emerald-600",
          bgColor: "bg-emerald-50",
          textColor: "text-emerald-800",
          borderColor: "border-emerald-200",
          icon: (
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          ),
          label: "Analysis Complete"
        };
      case "FAILURE":
        return {
          color: "from-red-500 to-red-600",
          bgColor: "bg-red-50",
          textColor: "text-red-800",
          borderColor: "border-red-200",
          icon: (
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          ),
          label: "Analysis Failed"
        };
      case "PENDING":
      case "Checking...":
        return {
          color: "from-blue-500 to-purple-600",
          bgColor: "bg-blue-50",
          textColor: "text-blue-800",
          borderColor: "border-blue-200",
          icon: (
            <svg className="w-8 h-8 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ),
          label: "Initializing..."
        };
      default:
        return {
          color: "from-amber-500 to-amber-600",
          bgColor: "bg-amber-50",
          textColor: "text-amber-800",
          borderColor: "border-amber-200",
          icon: (
            <svg className="w-8 h-8 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
          ),
          label: "Processing..."
        };
    }
  };

  const statusConfig = getStatusConfig();

  if (result && !result.error) {
    return <ResultView result={result} />;
  }

  if (result && result.error) {
    return (
      <div className="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 p-6 flex items-center justify-center">
        <div className="max-w-2xl w-full">
          <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-red-200">
            <div className="bg-linear-to-r from-red-500 to-red-600 p-8 text-white">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                  <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-3xl font-bold">Analysis Failed</h1>
                  <p className="text-red-100 text-sm">Something went wrong</p>
                </div>
              </div>
            </div>
            <div className="p-8">
              <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
                <p className="text-red-800 font-medium">{result.error}</p>
              </div>
              <button
                onClick={() => window.location.reload()}
                className="mt-6 w-full bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg hover:shadow-xl"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 p-6 flex items-center justify-center">
      <div className="max-w-3xl w-full space-y-6">
        
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
          
          <div className={`bg-linear-to-r ${statusConfig.color} p-8 text-white`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                  {statusConfig.icon}
                </div>
                <div>
                  <h2 className="text-3xl font-bold mb-1">{statusConfig.label}</h2>
                  <p className="text-sm opacity-90">Analyzing repository structure and content</p>
                </div>
              </div>
            </div>
            
            <div className="mt-6">
              <div className="flex justify-between text-sm mb-2 opacity-90">
                <span>Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-3 bg-white bg-opacity-20 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-white rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>

          <div className="p-8 space-y-6">
            
            <div className={`${statusConfig.bgColor} ${statusConfig.borderColor} border-2 rounded-2xl p-6`}>
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 ${statusConfig.bgColor} rounded-xl flex items-center justify-center`}>
                  <div className={`w-3 h-3 ${statusConfig.color.replace('from-', 'bg-').split(' ')[0]} rounded-full animate-pulse`}></div>
                </div>
                <div>
                  <p className={`${statusConfig.textColor} font-bold text-lg`}>Current Status</p>
                  <p className={`${statusConfig.textColor} opacity-75`}>{status}</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider">
                Processing Steps
              </h3>
              
              <div className="space-y-2">
                {[
                  { label: "Fetching repository data", done: progress > 20 },
                  { label: "Analyzing README files", done: progress > 40 },
                  { label: "Scanning code structure", done: progress > 60 },
                  { label: "Computing similarity scores", done: progress > 80 },
                  { label: "Generating results", done: progress >= 100 }
                ].map((step, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      step.done 
                        ? 'bg-emerald-100 text-emerald-600' 
                        : 'bg-slate-200 text-slate-400'
                    }`}>
                      {step.done ? (
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <span className="text-xs font-bold">{idx + 1}</span>
                      )}
                    </div>
                    <span className={`text-sm ${step.done ? 'text-slate-700 font-medium' : 'text-slate-500'}`}>
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
              <svg className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div className="text-sm text-blue-800">
                <p className="font-medium">Status updates every 2 seconds</p>
                <p className="opacity-75">This process typically takes 30-60 seconds depending on repository size</p>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}