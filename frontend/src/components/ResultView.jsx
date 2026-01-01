export default function ResultView({ result }) {

  /* -------------------- Helpers -------------------- */

  const isAgentOpened = (agent) => {
    return agent.details && Object.keys(agent.details).length > 0;
  };

  const getAgentStyles = (opened) => {
    return opened
      ? {
          container: "bg-slate-50 border-slate-200",
          icon: "text-blue-600",
          badge: "bg-blue-100 text-blue-700 border-blue-300",
          label: "Completed"
        }
      : {
          container: "bg-red-50 border-red-300",
          icon: "text-red-600",
          badge: "bg-red-100 text-red-700 border-red-300",
          label: "Not Opened"
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

  /* -------------------- UI -------------------- */

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-slate-200">
          <h1 className="text-3xl font-bold text-slate-800">
            Repository Analysis Complete
          </h1>
          <p className="text-slate-500 mt-1">
            Similarity analysis results
          </p>
        </div>

        {/* Similar Repositories */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {result.top_3_repos?.map((repo, index) => (
            <div
              key={index}
              className="bg-white rounded-2xl shadow-xl border-2 border-slate-200 overflow-hidden"
            >

              {/* Repo Header */}
              <div className={`bg-gradient-to-r ${getSimilarityColor(repo.final_similarity)} p-6 text-white`}>
                <div className="flex justify-between items-start mb-3">
                  <span className="font-bold">Rank #{index + 1}</span>
                  <span className="bg-white text-slate-800 px-4 py-2 rounded-full font-bold">
                    {(repo.final_similarity * 100).toFixed(1)}%
                  </span>
                </div>
                <h3 className="text-xl font-bold break-words">
                  {formatRepoName(repo.repo_url)}
                </h3>
                <span className="inline-block mt-2 bg-white bg-opacity-30 px-3 py-1 rounded-full text-sm">
                  {getSimilarityLabel(repo.final_similarity)}
                </span>
              </div>

              {/* Repo Body */}
              <div className="p-6 space-y-4">

                <a
                  href={repo.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline text-sm"
                >
                  View on GitHub
                </a>

                {/* Agent Scores */}
                <div className="space-y-3">
                  <h4 className="text-sm font-bold uppercase text-slate-700">
                    Agent Scores
                  </h4>

                  {repo.agent_scores.map((agent, idx) => {
                    const opened = isAgentOpened(agent);
                    const styles = getAgentStyles(opened);

                    return (
                      <div
                        key={idx}
                        className={`rounded-lg p-4 border ${styles.container}`}
                      >

                        {/* Agent Header */}
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
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

                            <span className="font-bold capitalize">
                              {agent.agent} Agent
                            </span>

                            <span
                              className={`text-xs px-2 py-0.5 rounded-full border ${styles.badge}`}
                            >
                              {styles.label}
                            </span>
                          </div>

                          <span className="font-mono font-semibold">
                            {(agent.score * 100).toFixed(2)}%
                          </span>
                        </div>

                        {/* Agent Details */}
                        {opened && (
                          <div className="grid grid-cols-2 gap-3 mt-3 pt-3 border-t">
                            {agent.details.token_count_a && (
                              <div className="bg-white p-3 rounded shadow-sm">
                                <p className="text-xs text-slate-500">
                                  Input Tokens
                                </p>
                                <p className="font-mono font-bold">
                                  {agent.details.token_count_a.toLocaleString()}
                                </p>
                              </div>
                            )}
                            {agent.details.token_count_b && (
                              <div className="bg-white p-3 rounded shadow-sm">
                                <p className="text-xs text-slate-500">
                                  Candidate Tokens
                                </p>
                                <p className="font-mono font-bold">
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
          ))}
        </div>

      </div>
    </div>
  );
}
