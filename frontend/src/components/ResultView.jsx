export default function ResultView({ result }) {

  /* -------------------- Helpers -------------------- */

  const isAgentOpened = (agent) => {
    return agent.details && Object.keys(agent.details).length > 0;
  };

  const getAgentStyles = (opened) => {
    return opened
      ? {
          container: "bg-emerald-50 border-emerald-200",
          icon: "text-emerald-600",
          badge: "bg-emerald-100 text-emerald-700 border-emerald-300",
          label: "Completed"
        }
      : {
          container: "bg-amber-50 border-amber-300",
          icon: "text-amber-600",
          badge: "bg-amber-100 text-amber-700 border-amber-300",
          label: "Skipped"
        };
  };

  const getSimilarityColor = (score) => {
    if (score >= 0.7) return "from-red-500 to-red-600";
    if (score >= 0.4) return "from-orange-500 to-orange-600";
    if (score >= 0.2) return "from-blue-500 to-blue-600";
    return "from-slate-500 to-slate-600";
  };

  const getSimilarityLabel = (score) => {
    if (score >= 0.7) return "High Similarity";
    if (score >= 0.4) return "Moderate Similarity";
    if (score >= 0.2) return "Low Similarity";
    return "Minimal Similarity";
  };

  const formatRepoName = (url) => {
    const parts = url.split("/");
    return parts[parts.length - 1] || url;
  };

  const getOwnerName = (url) => {
    const parts = url.split("/");
    return parts.length >= 2 ? parts[parts.length - 2] : "";
  };

  /* -------------------- UI -------------------- */

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Header Bento */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          {/* Main Title Card */}
          <div className="md:col-span-2 bg-linear-to-br from-blue-500 to-purple-600 rounded-3xl p-8 text-white shadow-2xl">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-4xl font-bold mb-2">Analysis Complete</h1>
                <p className="text-blue-100 text-lg">Repository similarity scan finished</p>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl px-4 py-2">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="mt-6 flex items-center gap-2 text-sm">
              <span className="bg-white bg-opacity-20 backdrop-blur-sm px-3 py-1 rounded-full">
                {formatRepoName(result.input_repo)}
              </span>
            </div>
          </div>

          {/* Stats Card */}
          <div className="bg-white rounded-3xl p-6 shadow-xl">
            <div className="text-slate-500 text-sm font-semibold mb-2">REPOSITORIES FOUND</div>
            <div className="text-5xl font-bold text-slate-800 mb-1">
              {result.all_repo_scores?.length || result.top_3_repos?.length || 0}
            </div>
            <div className="text-slate-400 text-sm">Total matches analyzed</div>
          </div>

        </div>

        {/* Repository Cards - Bento Grid */}
        <div className="grid grid-cols-1 gap-6">
          {result.top_3_repos?.map((repo, index) => (
            <div
              key={index}
              className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200"
            >

              {/* Bento Layout */}
              <div className="grid md:grid-cols-3 gap-0">
                
                {/* Left: Similarity Score */}
                <div className={`bg-linear-to-br ${getSimilarityColor(repo.final_similarity)} p-8 text-white flex flex-col justify-between`}>
                  <div>
                    <div className="text-sm font-semibold mb-1 opacity-90">RANK #{index + 1}</div>
                    <div className="text-6xl font-bold mb-2">
                      {(repo.final_similarity * 100).toFixed(1)}
                      <span className="text-2xl">%</span>
                    </div>
                    <div className="inline-block bg-white bg-opacity-25 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium">
                      {getSimilarityLabel(repo.final_similarity)}
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <div className="h-2 bg-white bg-opacity-20 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-white rounded-full transition-all duration-500"
                        style={{ width: `${repo.final_similarity * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Right: Repository Info & Agent Scores */}
                <div className="md:col-span-2 p-8 space-y-6">

                  {/* Repo Header */}
                  <div>
                    <div className="text-xs font-semibold text-slate-500 mb-1">{getOwnerName(repo.repo_url)}</div>
                    <h3 className="text-2xl font-bold text-slate-800 mb-3 wrap-break-word">
                      {formatRepoName(repo.repo_url)}
                    </h3>
                    <a
                      href={repo.repo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm group"
                    >
                      <span>View on GitHub</span>
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  </div>

                  {/* Agent Scores */}
                  <div>
                    <h4 className="text-xs font-bold uppercase text-slate-500 mb-3 tracking-wider">
                      Agent Analysis
                    </h4>

                    <div className="space-y-3">
                      {repo.agent_scores.map((agent, idx) => {
                        const opened = isAgentOpened(agent);
                        const styles = getAgentStyles(opened);

                        return (
                          <div
                            key={idx}
                            className={`rounded-2xl p-4 border-2 ${styles.container} transition-all hover:shadow-md`}
                          >

                            {/* Agent Header */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-xl ${opened ? 'bg-emerald-100' : 'bg-amber-100'} flex items-center justify-center`}>
                                  <svg
                                    className={`w-5 h-5 ${styles.icon}`}
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                  >
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d={
                                        opened
                                          ? "M9 12l2 2 4-4"
                                          : "M6 18L18 6M6 6l12 12"
                                      }
                                    />
                                  </svg>
                                </div>

                                <div>
                                  <span className="font-bold text-slate-800 capitalize block">
                                    {agent.agent}
                                  </span>
                                  <span
                                    className={`text-xs px-2 py-0.5 rounded-full border ${styles.badge}`}
                                  >
                                    {styles.label}
                                  </span>
                                </div>
                              </div>

                              <div className="text-right">
                                <div className="text-2xl font-bold text-slate-800">
                                  {(agent.score * 100).toFixed(1)}%
                                </div>
                              </div>
                            </div>

                            {/* Agent Details */}
                            {opened && (
                              <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-slate-200">
                                {agent.details.token_count_a && (
                                  <div className="bg-white p-3 rounded-xl shadow-sm border border-slate-100">
                                    <p className="text-xs text-slate-500 mb-1 font-medium">
                                      Input Tokens
                                    </p>
                                    <p className="font-mono font-bold text-slate-800 text-lg">
                                      {agent.details.token_count_a.toLocaleString()}
                                    </p>
                                  </div>
                                )}
                                {agent.details.token_count_b && (
                                  <div className="bg-white p-3 rounded-xl shadow-sm border border-slate-100">
                                    <p className="text-xs text-slate-500 mb-1 font-medium">
                                      Candidate Tokens
                                    </p>
                                    <p className="font-mono font-bold text-slate-800 text-lg">
                                      {agent.details.token_count_b.toLocaleString()}
                                    </p>
                                  </div>
                                )}
                              </div>
                            )}

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