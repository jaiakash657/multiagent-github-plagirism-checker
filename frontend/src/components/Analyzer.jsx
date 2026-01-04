import { useState } from "react";
import { analyzeRepo, checkStatus, getResult } from "../api/api";
import ResultView from "./ResultView";

export default function Analyzer() {
  const [repoUrl, setRepoUrl] = useState("");
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const agents = [
    {
      id: "fingerprint",
      name: "Fingerprint Analysis",
      subtitle: "Surface-Level Similarity Detection",
      icon: "🔍",
      color: "blue",
      description: "Performs a rapid initial assessment of repository characteristics by examining file structures, naming patterns, and basic metadata to identify surface-level similarities between repositories.",
      ranges: [
        { range: "0–20%", label: "Completely Different", desc: "Repositories share no meaningful surface characteristics" },
        { range: "21–40%", label: "Minor Overlap", desc: "Common boilerplate or framework patterns detected" },
        { range: "41–60%", label: "Noticeable Similarity", desc: "Significant shared patterns in structure or naming" },
        { range: "61–80%", label: "High Resemblance", desc: "Strong surface-level similarities across multiple dimensions" },
        { range: "81–100%", label: "Nearly Identical", desc: "Repositories exhibit almost identical surface characteristics" }
      ],
      note: "Use as a quick initial indicator, not definitive proof of similarity"
    },
    {
      id: "simhash",
      name: "SimHash Analysis",
      subtitle: "Lexical & Code-Text Similarity",
      icon: "📝",
      color: "orange",
      description: "Analyzes the textual content and lexical patterns within the code to detect similarities in variable names, function names, comments, and overall code vocabulary, even when logic differs.",
      ranges: [
        { range: "0–25%", label: "Different Code", desc: "Distinct vocabulary and naming conventions" },
        { range: "26–45%", label: "Similar Patterns", desc: "Some shared naming or structural patterns" },
        { range: "46–65%", label: "Likely Modified Copy", desc: "Substantial lexical overlap with modifications" },
        { range: "66–85%", label: "Strong Textual Similarity", desc: "Highly similar code text with minor variations" },
        { range: "86–100%", label: "Almost Identical Code", desc: "Near-identical textual representation" }
      ],
      note: "Effective at catching renamed-variable plagiarism and code obfuscation"
    },
    {
      id: "winnowing",
      name: "Winnowing Analysis",
      subtitle: "Substring-Based Plagiarism Detection",
      icon: "🔴",
      color: "red",
      description: "Employs advanced fingerprinting algorithms to identify exact and near-exact substring matches within the codebase, revealing direct copy-paste instances even across large repositories.",
      ranges: [
        { range: "0–30%", label: "No Plagiarism", desc: "No significant substring matches detected" },
        { range: "31–50%", label: "Shared Snippets", desc: "Common code snippets or library usage" },
        { range: "51–70%", label: "Partial Plagiarism", desc: "Substantial portions appear to be copied" },
        { range: "71–90%", label: "Major Copy-Paste", desc: "Extensive copying with minimal modification" },
        { range: "91–100%", label: "Near-Exact Plagiarism", desc: "Almost complete reproduction of source code" }
      ],
      note: "Strongest indicator for reviewers investigating potential plagiarism"
    },
    {
      id: "structural",
      name: "Structural/AST Analysis",
      subtitle: "Code Architecture & Control Flow",
      icon: "🧱",
      color: "purple",
      description: "Examines the abstract syntax tree (AST) and architectural patterns to compare code structure, control flow logic, and organizational patterns independent of naming or formatting choices.",
      ranges: [
        { range: "0–20%", label: "Different Structure", desc: "Fundamentally different architectural approaches" },
        { range: "21–40%", label: "Conceptual Similarity", desc: "Same general idea with different implementations" },
        { range: "41–60%", label: "Similar Control Flow", desc: "Comparable logic paths and decision structures" },
        { range: "61–80%", label: "Same Structure", desc: "Identical structure with renamed elements" },
        { range: "81–100%", label: "Structurally Identical", desc: "Perfect structural match regardless of naming" }
      ],
      note: "Explains cases where logic is copied but code appears rewritten"
    },
    {
      id: "semantic",
      name: "Semantic Analysis",
      subtitle: "Logic & Intent Similarity",
      icon: "🧠",
      color: "indigo",
      description: "Performs deep analysis of the underlying meaning, purpose, and algorithmic intent of the code to identify functional equivalence even when implementations appear different on the surface.",
      ranges: [
        { range: "0–30%", label: "Different Intent", desc: "Fundamentally different purposes or approaches" },
        { range: "31–50%", label: "Same Domain", desc: "Related problem space but different solutions" },
        { range: "51–70%", label: "Same Algorithm", desc: "Identical algorithmic approach with variations" },
        { range: "71–90%", label: "Same Solution", desc: "Equivalent solutions despite different code" },
        { range: "91–100%", label: "Semantically Identical", desc: "Perfect logical and functional equivalence" }
      ],
      note: "Justifies cases where code looks independent but solves problems identically"
    },
    {
      id: "contributor",
      name: "Contributor Analysis",
      subtitle: "Author & Repository Relationships",
      icon: "👥",
      color: "teal",
      description: "Investigates authorship patterns, commit histories, and repository relationships to determine if similarities are due to shared contributors, forks, or legitimate code reuse among collaborators.",
      ranges: [
        { range: "0%", label: "No Relation", desc: "Completely independent contributors" },
        { range: "25–50%", label: "Partial Overlap", desc: "Some shared contributors or organizations" },
        { range: "75%", label: "Strong Link", desc: "Significant contributor overlap or fork relationship" },
        { range: "100%", label: "Same Author/Fork", desc: "Identical authorship or direct fork relationship" }
      ],
      note: "Provides context - not evidence of plagiarism but relationship information"
    }
  ];

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
      setResult(null);

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

  const getColorClasses = (color) => {
    const colors = {
      blue: "from-blue-500 to-blue-600 bg-blue-50 text-blue-700 border-blue-200",
      orange: "from-orange-500 to-orange-600 bg-orange-50 text-orange-700 border-orange-200",
      red: "from-red-500 to-red-600 bg-red-50 text-red-700 border-red-200",
      purple: "from-purple-500 to-purple-600 bg-purple-50 text-purple-700 border-purple-200",
      indigo: "from-indigo-500 to-indigo-600 bg-indigo-50 text-indigo-700 border-indigo-200",
      teal: "from-teal-500 to-teal-600 bg-teal-50 text-teal-700 border-teal-200"
    };
    return colors[color] || colors.blue;
  };

  const [expandedAgent, setExpandedAgent] = useState(null);

  // Show result view if result is available
  if (result) {
    return (
      <div className="relative">
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

  // Show explanation view
  if (showExplanation) {
    return (
      <div className="min-h-screen bg-linear-to-br from-slate-50 via-blue-50 to-slate-50 p-6">
        <div className="max-w-5xl mx-auto space-y-6">
          
          {/* Back Button */}
          <button
            onClick={() => setShowExplanation(false)}
            className="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-700 font-semibold px-4 py-2 rounded-xl shadow-lg border border-slate-200 transition-all hover:shadow-xl"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Analyzer
          </button>
          
          {/* Header */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 bg-linear-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-3xl shadow-lg">
                📊
              </div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-slate-900 mb-2">
                  Understanding Repository Analysis
                </h1>
                <p className="text-slate-600">
                  My multi-agent system examines repositories from six different perspectives to provide comprehensive similarity analysis. Each agent contributes unique insights to the overall assessment.
                </p>
                <p className="text-sm text-slate-500 mt-2">
                  Made by <span className="font-semibold text-slate-700">Jai Akash</span>
                </p>
              </div>
            </div>
          </div>

          {/* Overall Similarity Score Guide */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <h2 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              Overall Similarity Score
            </h2>
            <p className="text-slate-600 mb-6">
              The final aggregated score combines insights from all six agents to provide a comprehensive similarity assessment. This is the primary metric for evaluating repository relationships.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {[
                { range: "0–20%", label: "No Similarity", color: "bg-green-500" },
                { range: "21–40%", label: "Low Similarity", color: "bg-lime-500" },
                { range: "41–60%", label: "Moderate Similarity", color: "bg-yellow-500" },
                { range: "61–80%", label: "High Similarity", color: "bg-orange-500" },
                { range: "81–100%", label: "Very High Similarity", color: "bg-red-500" }
              ].map((item, idx) => (
                <div key={idx} className="text-center">
                  <div className={`${item.color} text-white font-bold py-3 rounded-lg mb-2 shadow-md`}>
                    {item.range}
                  </div>
                  <div className="text-sm font-semibold text-slate-700">{item.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Individual Agents */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <span className="text-2xl">🤖</span>
              Individual Analysis Agents
            </h2>
            
            {agents.map((agent) => {
              const colorClass = getColorClasses(agent.color);
              const isExpanded = expandedAgent === agent.id;
              
              return (
                <div key={agent.id} className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden transition-all">
                  <button
                    onClick={() => setExpandedAgent(isExpanded ? null : agent.id)}
                    className="w-full p-6 flex items-center gap-4 hover:bg-slate-50 transition-colors text-left"
                  >
                    <div className={`w-14 h-14 bg-linear-to-br ${colorClass.split(' ')[0]} ${colorClass.split(' ')[1]} rounded-xl flex items-center justify-center text-2xl shadow-md`}>
                      {agent.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-slate-900">{agent.name}</h3>
                      <p className="text-sm text-slate-600">{agent.subtitle}</p>
                    </div>
                    <svg 
                      className={`w-6 h-6 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {isExpanded && (
                    <div className="px-6 pb-6 space-y-4 border-t border-slate-100">
                      <div className="pt-4">
                        <h4 className="font-semibold text-slate-900 mb-2">Description</h4>
                        <p className="text-slate-600 leading-relaxed">{agent.description}</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-slate-900 mb-3">Interpretation Scale</h4>
                        <div className="space-y-2">
                          {agent.ranges.map((range, idx) => (
                            <div key={idx} className={`p-3 rounded-lg border ${colorClass.split(' ').slice(2).join(' ')}`}>
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-bold text-sm">{range.range}</span>
                                <span className="font-semibold text-sm">{range.label}</span>
                              </div>
                              <p className="text-xs opacity-75">{range.desc}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div className={`p-4 rounded-lg ${colorClass.split(' ')[2]} border ${colorClass.split(' ')[3]}`}>
                        <div className="flex items-start gap-2">
                          <svg className="w-5 h-5 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          <div>
                            <div className="font-semibold text-sm mb-1">Important Note</div>
                            <div className="text-sm">{agent.note}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Best Practices */}
          <div className="bg-linear-to-br from-blue-500 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <span className="text-2xl">💡</span>
              Interpretation Best Practices
            </h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-white rounded-full mt-2 shrink-0"></div>
                <p className="leading-relaxed">Consider all six agent scores together rather than relying on a single metric</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-white rounded-full mt-2 shrink-0"></div>
                <p className="leading-relaxed">High contributor overlap may explain legitimate similarities (forks, team projects)</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-white rounded-full mt-2 shrink-0"></div>
                <p className="leading-relaxed">Winnowing scores above 70% warrant detailed manual review for potential plagiarism</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-white rounded-full mt-2 shrink-0"></div>
                <p className="leading-relaxed">Structural and semantic similarity may indicate algorithm reuse or common design patterns</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-white rounded-full mt-2 shrink-0"></div>
                <p className="leading-relaxed">The overall similarity score provides the most balanced assessment for decision-making</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    );
  }

  // Main analyzer view
  return (
    <div className="min-h-screen bg-linear-to-br from-slate-100 via-blue-50 to-slate-100 p-6 flex items-center justify-center">
      <div className="max-w-2xl w-full">
        
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
          
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

          <div className="p-8 space-y-6">
            
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

            {status && (
              <div className={`px-5 py-4 rounded-xl border-2 ${getStatusColor()} font-medium flex items-center gap-3 transition-all duration-300`}>
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
                  <span>Get similarity scores and discover related repositories (Takes around 30 to 60 seconds)</span>
                </li>
              </ul>
            </div>

            {/* Explain Button */}
            <div className="pt-2">
              <button
                onClick={() => setShowExplanation(true)}
                className="w-full py-3 bg-linear-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl active:scale-95 transform flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Explain Analysis Metrics
              </button>
            </div>

            {/* Made By */}
            <div className="text-center pt-2 pb-1">
              <p className="text-sm text-slate-500">
                Made by <span className="font-semibold text-slate-700">Jai Akash</span>
              </p>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}