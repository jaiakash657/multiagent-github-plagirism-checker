from core.weights import AGENT_WEIGHTS

def aggregate_results(results: list):
    """
    results = [
       {"agent": "LexicalAgent", "score": 0.78},
       {"agent": "StructuralAgent", "score": 0.83},
       ...
    ]
    """

    total_weight = sum(AGENT_WEIGHTS.values())
    weighted_sum = 0

    for r in results:
        agent = r["agent"]
        score = r["score"]

        weight = AGENT_WEIGHTS.get(agent, 1)  # default 1
        weighted_sum += score * weight

    final_score = weighted_sum / total_weight

    return {
        "results": results,
        "aggregated_score": round(final_score, 4)
    }
