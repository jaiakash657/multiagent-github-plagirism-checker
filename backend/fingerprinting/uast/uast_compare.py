from fingerprinting.uast.subtree_extractor import SubtreeExtractor

class UASTComparator:
    @staticmethod
    def similarity(tree_a, tree_b) -> float:
        subs_a = set(SubtreeExtractor.extract(tree_a))
        subs_b = set(SubtreeExtractor.extract(tree_b))

        if not subs_a or not subs_b:
            return 0.0

        common = subs_a & subs_b
        union = subs_a | subs_b

        return round(len(common) / len(union), 4)
