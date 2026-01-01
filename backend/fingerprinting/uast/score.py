class UASTScorer:
    @staticmethod
    def normalize(raw_score: float, size: int) -> float:
        if size < 5:
            return raw_score * 0.5
        if size < 10:
            return raw_score * 0.75
        return raw_score
