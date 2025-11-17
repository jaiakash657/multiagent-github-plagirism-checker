from core.weights import AGENT_WEIGHTS, TOTAL_WEIGHT

def aggregate_single_repo(results: list):
    weighted_sum = 0
    for r in results:
        agent = r.get("agent")
        score = float(r.get("score", 0))
        weight = AGENT_WEIGHTS.get(agent, 1.0)
        weighted_sum += score * weight
    final_score = weighted_sum / TOTAL_WEIGHT
    return round(final_score, 4)

# keep aggregate_multiple_repos as you had earlier, calling aggregate_single_repo

def aggregate_multiple_repos(repo_results: dict):
    """
    repo_results = {
        "repo1_url": [
            {"agent": "LexicalAgent", "score": 0.78},
            {"agent": "StructuralAgent", "score": 0.83},
            ...
        ],
        "repo2_url": [...],
        "repo3_url": [...],
    }

    Returns top 3 similar repositories with their aggregated score.
    """

    aggregated_output = []

    for repo_url, agent_scores in repo_results.items():
        final_score = aggregate_single_repo(agent_scores)

        aggregated_output.append({
            "repo_url": repo_url,
            "agent_scores": agent_scores,
            "final_similarity": final_score
        })

    # Sort by highest similarity
    aggregated_output.sort(key=lambda x: x["final_similarity"], reverse=True)

    # Pick top 3
    top_3 = aggregated_output[:3]

    return {
        "top_3_repos": top_3,
        "all_repo_scores": aggregated_output  # optional but useful
    }
