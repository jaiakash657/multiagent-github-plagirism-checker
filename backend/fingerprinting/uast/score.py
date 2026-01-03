class UASTScorer:
    @staticmethod
    def normalize(raw_score: float, size: int) -> float:
        if size <= 0:
            return 0.0

        factor = min(1.0, size / 15.0)
        return round(raw_score * factor, 4)
