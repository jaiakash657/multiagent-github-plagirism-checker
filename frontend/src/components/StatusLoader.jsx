import { useEffect, useState } from "react";
import { checkStatus, getResult } from "../api/api";
import ResultView from "./ResultView";

export default function StatusLoader({ jobId }) {
  const [status, setStatus] = useState("Checking...");
  const [result, setResult] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await checkStatus(jobId);
        setStatus(res.data.status);

        if (res.data.status === "SUCCESS") {
          const finalRes = await getResult(jobId);
          setResult(finalRes.data.result);
          clearInterval(interval);
        }

        if (res.data.status === "FAILURE") {
          setResult({
            error: res.data.detail || "Task failed",
          });
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  const getStatusConfig = () => {
    switch(status) {
      case "SUCCESS":
        return {
          color: "bg-green-100 text-green-800 border-green-300",
          icon: (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          )
        };
      case "FAILURE":
        return {
          color: "bg-red-100 text-red-800 border-red-300",
          icon: (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          )
        };
      case "PENDING":
      case "Checking...":
        return {
          color: "bg-blue-100 text-blue-800 border-blue-300",
          icon: (
            <svg className="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )
        };
      default:
        return {
          color: "bg-yellow-100 text-yellow-800 border-yellow-300",
          icon: (
            <svg className="w-6 h-6 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
          )
        };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <div className="mt-8 max-w-4xl mx-auto">
      <div className={`${statusConfig.color} border-2 rounded-lg p-5 shadow-md transition-all duration-300`}>
        <div className="flex items-center gap-4">
          <div className="shrink-0">
            {statusConfig.icon}
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-1">Task Status</h3>
            <p className="text-lg font-semibold">{status}</p>
          </div>
        </div>
      </div>

      {!result && (
        <div className="mt-6 bg-white rounded-lg border-2 border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="shrink-0">
              <div className="relative">
                <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              </div>
            </div>
            <div>
              <p className="text-slate-700 font-medium text-lg">
                Processing your repository...
              </p>
              <p className="text-slate-500 text-sm mt-1">
                This may take a few moments. Please wait while we analyze the code.
              </p>
            </div>
          </div>
          
          <div className="mt-4 bg-slate-50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-slate-600 text-sm">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Updates every 2 seconds</span>
            </div>
          </div>
        </div>
      )}

      {result && <ResultView result={result} />}
    </div>
  );
}