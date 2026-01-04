export default function ResultView({ result }) {

  const isAgentOpened = (agent) => {
    return agent.details && Object.keys(agent.details).length > 0;
  };

  const getAgentStyles = (opened) => {
    return opened
      ? {
          container: "bg-gradient-to-br from-emerald-50 via-teal-50 to-emerald-100 border-emerald-300",
          icon: "text-emerald-600",
          badge: "bg-emerald-500 text-white",
          label: "Completed"
        }
      : {
          container: "bg-gradient-to-br from-slate-50 to-slate-100 border-slate-300",
          icon: "text-slate-400",
          badge: "bg-slate-400 text-white",
          label: "Skipped"
        };
  };

  const getSimilarityColor = (score) => {
    if (score >= 0.7) return "from-red-500 via-red-600 to-rose-600";
    if (score >= 0.4) return "from-orange-500 via-orange-600 to-amber-600";
    if (score >= 0.2) return "from-blue-500 via-blue-600 to-indigo-600";
    return "from-emerald-500 via-emerald-600 to-teal-600";
  };

  const getVerdictColor = (score) => {
    if (score >= 0.7) return "text-red-600 bg-red-50 border-red-200";
    if (score >= 0.4) return "text-orange-600 bg-orange-50 border-orange-200";
    if (score >= 0.2) return "text-blue-600 bg-blue-50 border-blue-200";
    return "text-green-600 bg-green-50 border-green-200";
  };

  const getSimilarityLabel = (score) => {
    if (score >= 0.7) return "High Similarity";
    if (score >= 0.4) return "Moderate Similarity";
    if (score >= 0.2) return "Low Similarity";
    return "Minimal Similarity";
  };

  const getVerdict = (score) => {
    if (score >= 0.7) return "⚠️ Plagiarism Detected";
    if (score >= 0.4) return "⚡ Suspicious Similarity";
    if (score >= 0.2) return "✓ Minor Overlap";
    return "✓ Original Content";
  };

  const formatRepoName = (url) => {
    const parts = url.split("/");
    return parts[parts.length - 1] || url;
  };

  const getOwnerName = (url) => {
    const parts = url.split("/");
    return parts.length >= 2 ? parts[parts.length - 2] : "";
  };

  const aggregatedScore = result.top_3_repos && result.top_3_repos.length > 0
    ? Math.max(...result.top_3_repos.map(r => r.final_similarity))
    : 0;

  const repoName = formatRepoName(result.input_repo);

  const handleDownloadPDF = () => {
    window.open(
      `http://localhost:8000/reports/download/pdf/${repoName}`,
      "_blank"
    );
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">

        <div className="bg-linear-to-br from-slate-800 via-slate-850 to-slate-900 rounded-3xl p-8 md:p-12 shadow-2xl border border-slate-700 relative overflow-hidden">
          
          <div className="absolute inset-0 bg-linear-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5 animate-pulse"></div>
          
          <div className="relative z-10">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-8">
              
              <div className="flex-1">
                <div className="text-slate-400 text-sm font-semibold mb-3 uppercase tracking-wider flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Analyzed Repository
                </div>
                <div className="flex items-center gap-3 flex-wrap">
                  <svg className="w-8 h-8 text-slate-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                  <h1 className="text-3xl md:text-5xl font-black text-white break-all bg-linear-to-r from-white to-slate-300 bg-clip-text">
                    {getOwnerName(result.input_repo)}/{repoName}
                  </h1>
                </div>
              </div>

              <button
                onClick={handleDownloadPDF}
                className="group px-6 py-3 bg-linear-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-3 self-start hover:scale-105 active:scale-95"
              >
                <svg className="w-5 h-5 group-hover:animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Download PDF</span>
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              
              <div className={`bg-linear-to-br ${getSimilarityColor(aggregatedScore)} rounded-2xl p-8 text-white relative overflow-hidden shadow-2xl`}>
                <div className="absolute top-0 right-0 w-40 h-40 bg-white opacity-10 rounded-full -mr-20 -mt-20 blur-2xl"></div>
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-black opacity-10 rounded-full -ml-16 -mb-16 blur-xl"></div>
                <div className="relative z-10">
                  <div className="text-sm font-bold mb-3 opacity-90 uppercase tracking-wider flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Aggregated Score
                  </div>
                  <div className="text-7xl font-black mb-3 leading-none">
                    {(aggregatedScore * 100).toFixed(1)}
                    <span className="text-3xl align-super">%</span>
                  </div>
                  <div className="inline-block bg-white bg-opacity-30 backdrop-blur-sm px-5 py-2 rounded-full text-sm font-bold shadow-lg">
                    {getSimilarityLabel(aggregatedScore)}
                  </div>
                  
                  <div className="mt-6">
                    <div className="h-3 bg-white bg-opacity-20 rounded-full overflow-hidden backdrop-blur-sm">
                      <div 
                        className="h-full bg-white rounded-full transition-all duration-1000 ease-out shadow-lg"
                        style={{ width: `${aggregatedScore * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className={`${getVerdictColor(aggregatedScore)} rounded-2xl p-8 border-2 relative overflow-hidden shadow-xl`}>
                <div className="absolute top-0 right-0 w-48 h-48 bg-current opacity-5 rounded-full -mr-24 -mt-24 blur-3xl"></div>
                <div className="relative z-10">
                  <div className="text-sm font-bold mb-4 opacity-70 uppercase tracking-wider flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Final Verdict
                  </div>
                  <div className="text-4xl md:text-5xl font-black mb-4 leading-tight">
                    {getVerdict(aggregatedScore)}
                  </div>
                  <div className="text-sm font-semibold opacity-70 flex items-start gap-2">
                    <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Comprehensive analysis across multiple detection algorithms
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1 h-px bg-linear-to-r from-transparent via-slate-700 to-transparent"></div>
          <div className="text-slate-400 text-sm font-bold uppercase tracking-wider flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-full border border-slate-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Top 3 Similar Repositories
          </div>
          <div className="flex-1 h-px bg-linear-to-r from-transparent via-slate-700 to-transparent"></div>
        </div>

        <div className="grid grid-cols-1 gap-8">
          {result.top_3_repos?.map((repo, index) => (
            <div
              key={index}
              className="bg-linear-to-br from-slate-800 via-slate-850 to-slate-900 rounded-3xl shadow-2xl overflow-hidden border border-slate-700 hover:border-slate-600 transition-all duration-300 hover:shadow-3xl"
            >

              <div className="grid lg:grid-cols-3 gap-0">
                
                <div className={`bg-linear-to-br ${getSimilarityColor(repo.final_similarity)} p-8 lg:p-10 text-white flex flex-col justify-between relative overflow-hidden`}>
                  
                  <div className="absolute top-0 left-0 w-64 h-64 bg-white opacity-5 rounded-full -ml-32 -mt-32 blur-3xl"></div>
                  <div className="absolute bottom-0 right-0 w-48 h-48 bg-black opacity-10 rounded-full -mr-24 -mb-24 blur-2xl"></div>

                  <div className="absolute top-6 right-6">
                    <div className="w-16 h-16 bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl flex items-center justify-center border-2 border-white border-opacity-30 shadow-xl">
                      <span className="text-3xl font-black">#{index + 1}</span>
                    </div>
                  </div>

                  <div className="relative z-10">
                    <div className="text-xs font-bold mb-4 opacity-90 uppercase tracking-widest flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                      Match Score
                    </div>
                    <div className="text-7xl lg:text-8xl font-black mb-4 leading-none">
                      {(repo.final_similarity * 100).toFixed(1)}
                      <span className="text-2xl align-super">%</span>
                    </div>
                    <div className="inline-block bg-white bg-opacity-30 backdrop-blur-sm px-5 py-2 rounded-xl text-xs font-bold uppercase tracking-wider shadow-lg">
                      {getSimilarityLabel(repo.final_similarity)}
                    </div>
                  </div>
                  
                  <div className="mt-8 relative z-10">
                    <div className="h-3 bg-white bg-opacity-20 rounded-full overflow-hidden backdrop-blur-sm shadow-inner">
                      <div 
                        className="h-full bg-white rounded-full transition-all duration-1000 ease-out shadow-lg"
                        style={{ width: `${repo.final_similarity * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="lg:col-span-2 p-8 lg:p-10 space-y-8">

                  <div className="border-b border-slate-700 pb-6">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider bg-slate-700/50 px-3 py-1 rounded-full">
                        {getOwnerName(repo.repo_url)}
                      </div>
                    </div>
                    <h3 className="text-3xl lg:text-4xl font-black text-white mb-5 break-all bg-linear-to-r from-white to-slate-400 bg-clip-text">
                      {formatRepoName(repo.repo_url)}
                    </h3>
                    <a
                      href={repo.repo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-bold text-sm group transition-all px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 rounded-lg border border-blue-500/30"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                      </svg>
                      <span>View Repository</span>
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold uppercase text-slate-400 mb-5 tracking-widest flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                      </svg>
                      Agent Analysis Results
                    </h4>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {repo.agent_scores.map((agent, idx) => {
                        const opened = isAgentOpened(agent);
                        const styles = getAgentStyles(opened);

                        return (
                          <div
                            key={idx}
                            className={`rounded-2xl p-6 border-2 ${styles.container} transition-all hover:shadow-xl backdrop-blur-sm hover:scale-[1.02] duration-300 relative overflow-hidden`}
                          >
                            <div className={`absolute top-0 right-0 w-32 h-32 ${opened ? 'bg-emerald-400' : 'bg-slate-300'} opacity-10 rounded-full -mr-16 -mt-16 blur-2xl`}></div>
                            
                            <div className="relative z-10">
                              <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                  <div className={`w-11 h-11 rounded-xl ${opened ? 'bg-linear-to-br from-emerald-500 to-teal-600' : 'bg-linear-to-br from-slate-400 to-slate-500'} flex items-center justify-center shadow-lg`}>
                                    <svg
                                      className="w-6 h-6 text-white"
                                      fill="none"
                                      stroke="currentColor"
                                      viewBox="0 0 24 24"
                                      strokeWidth={3}
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d={
                                          opened
                                            ? "M5 13l4 4L19 7"
                                            : "M6 18L18 6M6 6l12 12"
                                        }
                                      />
                                    </svg>
                                  </div>
                                  <div>
                                    <span className="font-black text-slate-800 capitalize block text-base mb-1">
                                      {agent.agent}
                                    </span>
                                    <span
                                      className={`text-[10px] px-2.5 py-1 rounded-full ${styles.badge} font-bold uppercase tracking-wider shadow-sm`}
                                    >
                                      {styles.label}
                                    </span>
                                  </div>
                                </div>

                                <div className="text-right">
                                  <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                                    Score
                                  </div>
                                  <div className="text-3xl font-black text-slate-800">
                                    {(agent.score * 100).toFixed(1)}<span className="text-lg">%</span>
                                  </div>
                                </div>
                              </div>

                              {opened && agent.details && (
                                <div className="space-y-3 pt-4 border-t-2 border-slate-200">
                                  {agent.details.reason && (
                                    <div className="bg-linear-to-r from-amber-50 to-orange-50 border-2 border-amber-200 p-3 rounded-xl shadow-sm">
                                      <div className="flex items-start gap-2">
                                        <svg className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                        </svg>
                                        <div>
                                          <p className="text-[10px] font-bold text-amber-800 uppercase tracking-wider mb-1">
                                            Not Run
                                          </p>
                                          <p className="text-xs text-amber-900 font-medium leading-relaxed">
                                            {agent.details.reason}
                                          </p>
                                        </div>
                                      </div>
                                    </div>
                                  )}
                                  
                                  {(agent.details.token_count_a || agent.details.token_count_b) && (
                                    <div className="space-y-2">
                                      {agent.details.token_count_a && (
                                        <div className="bg-white p-3 rounded-lg shadow-md border border-slate-200 hover:shadow-lg transition-shadow">
                                          <div className="flex items-center justify-between">
                                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                                              Target Tokens
                                            </p>
                                            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                                            </svg>
                                          </div>
                                          <p className="font-mono font-black text-slate-800 text-xl mt-1">
                                            {agent.details.token_count_a.toLocaleString()}
                                          </p>
                                        </div>
                                      )}
                                      {agent.details.token_count_b && (
                                        <div className="bg-white p-3 rounded-lg shadow-md border border-slate-200 hover:shadow-lg transition-shadow">
                                          <div className="flex items-center justify-between">
                                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                                              Candidate Tokens
                                            </p>
                                            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                                            </svg>
                                          </div>
                                          <p className="font-mono font-black text-slate-800 text-xl mt-1">
                                            {agent.details.token_count_b.toLocaleString()}
                                          </p>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  {(agent.details.score_a !== undefined || agent.details.score_b !== undefined) && (
                                    <div className="grid grid-cols-2 gap-2">
                                      {agent.details.score_a !== undefined && (
                                        <div className="bg-linear-to-br from-blue-50 to-cyan-50 p-3 rounded-lg shadow-md border border-blue-200 hover:shadow-lg transition-shadow">
                                          <p className="text-[10px] text-blue-600 font-bold uppercase tracking-wider flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            Target
                                          </p>
                                          <p className="font-black text-blue-900 text-xl mt-1">
                                            {(agent.details.score_a * 100).toFixed(1)}%
                                          </p>
                                        </div>
                                      )}
                                      {agent.details.score_b !== undefined && (
                                        <div className="bg-linear-to-br from-purple-50 to-pink-50 p-3 rounded-lg shadow-md border border-purple-200 hover:shadow-lg transition-shadow">
                                          <p className="text-[10px] text-purple-600 font-bold uppercase tracking-wider flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            Candidate
                                          </p>
                                          <p className="font-black text-purple-900 text-xl mt-1">
                                            {(agent.details.score_b * 100).toFixed(1)}%
                                          </p>
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                </div>
              </div>

            </div>
          ))}
        </div>

      </div>
    </div>
  );
}