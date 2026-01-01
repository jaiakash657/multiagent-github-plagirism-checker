AGENT_WEIGHTS = {
    "lexical": 1.0,
    "structural": 1.0,
    "semantic": 2.0,
    "contributor": 0.5,
    "fingerprint": 1.0,
    "simhash": 0.5,
    "winnowing": 1.5,
    "ast": 2.0,   # or "uast" if renamed later
}

TOTAL_WEIGHT = sum(AGENT_WEIGHTS.values())
