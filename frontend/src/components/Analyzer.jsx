import { useState } from "react";
import { analyzeRepo, checkStatus, getResult } from "../api/api";
import ResultView from "./ResultView";

export default function Analyzer() {
    const [repoUrl, setRepoUrl] = useState("");
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
        console.log("Analyze button clicked");

        if (!repoUrl) {
            alert("Enter a Repo URL");
            return;
        }

        try {
            const response = await analyzeRepo(repoUrl);
            console.log("Analyze API response:", response);

            setJobId(response.job_id);
            setStatus("Queued");

            // Poll for status
            pollStatus(response.job_id);
        } catch (err) {
            console.error(err);
        }
    };

    const pollStatus = (job) => {
        const interval = setInterval(async () => {
            const statusRes = await checkStatus(job);
            console.log("Status:", statusRes);

            setStatus(statusRes.status);

            if (statusRes.status === "SUCCESS") {
                clearInterval(interval);
                const data = await getResult(job);
                console.log("Final result:", data);
                setResult(data.result);
            }
            else if (statusRes.status === "FAILURE") {
                clearInterval(interval);
                alert("Task failed: " + statusRes.detail);
            }
        }, 2000);
    };

    const getStatusColor = () => {
        switch(status) {
            case "SUCCESS": return "text-green-600 bg-green-50 border-green-200";
            case "FAILURE": return "text-red-600 bg-red-50 border-red-200";
            case "Queued": return "text-yellow-600 bg-yellow-50 border-yellow-200";
            default: return "text-blue-600 bg-blue-50 border-blue-200";
        }
    };

    return (
        <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 p-6">
            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg shadow-lg p-8">
                    <h2 className="text-3xl font-bold text-slate-800 mb-6 flex items-center gap-3">
                        <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                        </svg>
                        Repo Analyzer
                    </h2>

                    <div className="flex flex-col sm:flex-row gap-3 mb-6">
                        <input
                            type="text"
                            placeholder="Enter GitHub Repo URL"
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            className="flex-1 px-4 py-3 border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder-slate-400"
                        />

                        <button 
                            onClick={handleAnalyze}
                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg active:scale-95 transform"
                        >
                            Analyze Repo
                        </button>
                    </div>

                    {status && (
                        <div className={`mb-6 px-4 py-3 rounded-lg border-2 ${getStatusColor()} font-medium flex items-center gap-2`}>
                            {status === "SUCCESS" && (
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            )}
                            {status === "FAILURE" && (
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            )}
                            {(status === "Queued" || (!["SUCCESS", "FAILURE"].includes(status))) && (
                                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            )}
                            <span>Status: {status}</span>
                        </div>
                    )}

                    {result && (
                    <div className="bg-slate-50 rounded-lg border-2 border-slate-200 overflow-hidden">
                        
                        <div className="bg-slate-800 px-4 py-2 flex items-center justify-between">
                        <span className="text-slate-200 font-semibold text-sm">
                            Analysis Result
                        </span>
                        </div>

                        {/* 🔥 Bento Result UI */}
                        <ResultView result={result} />

                    </div>
                    )}

                </div>
            </div>
        </div>
    );
}