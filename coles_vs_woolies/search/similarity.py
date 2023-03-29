def jaccard_similarity(x: str, y: str):
    """ returns the jaccard similarity between two lists """
    x, y = (sentence.lower().split(" ") for sentence in (x, y))
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)
