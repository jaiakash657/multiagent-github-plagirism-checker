# core/weights.py
AGENT_WEIGHTS = {
    "lexical": 1.0,
    "structural": 1.0,
    "semantic": 2.0,
    "contributor": 0.5,
    "fingerprint": 1.0,
    # new agents
    "simhash": 0.5,
    "winnowing": 1.5,
    "ast": 2.0
}

# normalization helper (used in aggregator)
TOTAL_WEIGHT = sum(AGENT_WEIGHTS.values())
