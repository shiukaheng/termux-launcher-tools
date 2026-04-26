def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_search(query: str, candidates: list, threshold_ratio: float = 0.5) -> list:
    query_lower = query.lower()
    results = []
    
    for candidate in candidates:
        candidate_lower = candidate.lower()
        distance = levenshtein_distance(query_lower, candidate_lower)
        max_len = max(len(query_lower), len(candidate_lower))
        if max_len == 0:
            continue
        ratio = 1 - (distance / max_len)
        if ratio >= threshold_ratio:
            results.append((candidate, distance, ratio))
    
    results.sort(key=lambda x: x[1])
    return results
