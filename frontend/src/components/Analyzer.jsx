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
            setResult(null); // Clear previous results

            // Poll for status
            pollStatus(response.job_id);
        } catch (err) {
            console.error(err);
            alert("Error starting analysis: " + err.message);
        }
    };

    const pollStatus = (job) => {
        const interval = setInterval(async () => {
            try {
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
            } catch (err) {
                console.error("Polling error:", err);
                clearInterval(interval);
            }
        }, 2000);
    };

    const getStatusColor = () => {
        switch(status) {
            case "SUCCESS": return "text-emerald-600 bg-emerald-50 border-emerald-200";
            case "FAILURE": return "text-red-600 bg-red-50 border-red-200";
            case "Queued": return "text-amber-600 bg-amber-50 border-amber-200";
            default: return "text-blue-600 bg-blue-50 border-blue-200";
        }
    };

    // If we have results, show full-screen ResultView
    if (result) {
        return (
            <div className="relative">
                {/* Back Button */}
                <div className="fixed top-6 left-6 z-50">
                    <button
                        onClick={() => {
                            setResult(null);
                            setStatus(null);
                            setJobId(null);
                        }}
                        className="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-700 font-semibold px-4 py-2 rounded-xl shadow-lg border border-slate-200 transition-all hover:shadow-xl"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        New Analysis
                    </button>
                </div>

                <ResultView result={result} />
            </div>
        );
    }

    // Otherwise show the input form
    return (
        <div className="min-h-screen bg-linear-to-br from-slate-100 via-blue-50 to-slate-100 p-6 flex items-center justify-center">
            <div className="max-w-2xl w-full">
                
                {/* Main Card */}
                <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
                    
                    {/* Header with Gradient */}
                    <div className="bg-linear-to-r from-blue-600 to-purple-600 p-8 text-white">
                        <div className="flex items-center gap-4 mb-2">
                            <div className="w-14 h-14 bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                                </svg>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold">Repository Analyzer</h1>
                                <p className="text-blue-100 text-sm">Discover similar GitHub repositories</p>
                            </div>
                        </div>
                    </div>

                    {/* Form Content */}
                    <div className="p-8 space-y-6">
                        
                        {/* Input Section */}
                        <div>
                            <label className="block text-sm font-semibold text-slate-700 mb-2">
                                GitHub Repository URL
                            </label>
                            <div className="flex flex-col sm:flex-row gap-3">
                                <input
                                    type="text"
                                    placeholder="https://github.com/username/repository"
                                    value={repoUrl}
                                    onChange={(e) => setRepoUrl(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                                    className="flex-1 px-4 py-3 border-2 border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder-slate-400 text-slate-700"
                                />

                                <button 
                                    onClick={handleAnalyze}
                                    disabled={!repoUrl || status === "Queued" || (status && status !== "SUCCESS" && status !== "FAILURE")}
                                    className="px-8 py-3 bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl active:scale-95 transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg disabled:active:scale-100"
                                >
                                    Analyze
                                </button>
                            </div>
                        </div>

                        {/* Status Display */}
                        {status && (
                            <div className={`px-5 py-4 rounded-xl border-2 ${getStatusColor()} font-medium flex items-center gap-3 animate-fadeIn`}>
                                {status === "SUCCESS" && (
                                    <svg className="w-6 h-6 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                    </svg>
                                )}
                                {status === "FAILURE" && (
                                    <svg className="w-6 h-6 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                    </svg>
                                )}
                                {(status === "Queued" || (!["SUCCESS", "FAILURE"].includes(status))) && (
                                    <svg className="w-6 h-6 animate-spin shrink-0" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                )}
                                <div>
                                    <div className="font-bold">Status: {status}</div>
                                    {status === "Queued" && <div className="text-sm opacity-75">Your analysis is in the queue...</div>}
                                    {status !== "SUCCESS" && status !== "FAILURE" && status !== "Queued" && (
                                        <div className="text-sm opacity-75">Processing repository data...</div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Info Section */}
                        <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                            <h3 className="font-bold text-slate-800 mb-2 flex items-center gap-2">
                                <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                </svg>
                                How it works
                            </h3>
                            <ul className="text-sm text-slate-600 space-y-2">
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 mt-0.5">•</span>
                                    <span>Enter any public GitHub repository URL</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 mt-0.5">•</span>
                                    <span>Our AI agents analyze code, README, and structure</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-blue-600 mt-0.5">•</span>
                                    <span>Get similarity scores and discover related repositories</span>
                                </li>
                            </ul>
                        </div>

                    </div>
                </div>

            </div>
        </div>
    );
}