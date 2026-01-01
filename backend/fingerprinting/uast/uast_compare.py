from fingerprinting.uast.subtree_extractor import SubtreeExtractor


class UASTComparator:
    @staticmethod
    def similarity(tree_a, tree_b) -> float:
        subs_a = set(SubtreeExtractor.extract(tree_a))
        subs_b = set(SubtreeExtractor.extract(tree_b))

        if not subs_a or not subs_b:
            return 0.0

        common = subs_a.intersection(subs_b)
        return len(common) / max(len(subs_a), len(subs_b))
