"""Fuzzy matching utilities for searching HDF5 tree paths.

This module provides fuzzy matching functionality similar to fzf (fuzzy finder).
It can be used with RapidFuzz for fast searching through large lists of paths.

The main scorer function can be easily swapped out for RapidFuzz's built-in
scorers if performance requires it.

Example usage:
    from h5forest.fuzzy import search_paths

    results = search_paths("grpmass", all_paths, limit=20)
    # Returns: [("/Group1/Mass_Data", 250), ("/Group2/Mass", 180), ...]
"""

from rapidfuzz import process


def fzf_scorer(query, choice, **kwargs):
    """
    FZF-style subsequence matching scorer.

    This scorer implements fuzzy matching similar to fzf:
    - All query characters must appear in order in the choice
    - Characters can have gaps between them
    - Scoring favors:
      - Consecutive character matches
      - Matches at word boundaries (after /, _, -, .)
      - Matches at the start of the string

    This function is designed to be easily swappable with RapidFuzz's built-in
    scorers. To use RapidFuzz's partial_ratio instead:
        from rapidfuzz import fuzz
        results = process.extract(query, choices, scorer=fuzz.partial_ratio)

    Args:
        query (str):
            The search query string.
        choice (str):
            The string to match against.
        **kwargs:
            Additional arguments (for RapidFuzz compatibility).

    Returns:
        int:
            Score from 0-100+ (higher is better, 0 means no match).
    """
    if not query:
        return 0

    query_lower = query.lower()
    choice_lower = choice.lower()

    score = 0
    choice_idx = 0
    prev_idx = -1
    matched_indices = []

    # Try to find each query character in order
    for char in query_lower:
        try:
            choice_idx = choice_lower.index(char, choice_idx)
        except ValueError:
            # Character not found - no match
            return 0

        matched_indices.append(choice_idx)

        # Base score for each matched character
        score += 100

        # Bonus: Consecutive character match
        if choice_idx == prev_idx + 1:
            score += 50

        # Bonus: Match at word boundary (start or after separator)
        if choice_idx == 0 or choice_lower[choice_idx - 1] in "/_-.":
            score += 30

        # Bonus: Match at start of choice
        if choice_idx == 0:
            score += 20

        prev_idx = choice_idx
        choice_idx += 1

    # Bonus: Shorter matches are better (prefer "Mass" over "Mass_Data_Extra")
    # Normalize by length difference
    length_penalty = len(choice_lower) - len(query_lower)
    score -= length_penalty * 2

    return max(0, score)  # Ensure non-negative


def search_paths(query, paths, limit=20, scorer=None):
    """
    Search for paths matching the query using fuzzy matching.

    Args:
        query (str):
            The search query string.
        paths (list):
            List of path strings to search through.
        limit (int):
            Maximum number of results to return (default: 20).
        scorer (callable, optional):
            Custom scorer function. If None, uses fzf_scorer.
            Can be set to RapidFuzz scorers like fuzz.partial_ratio.

    Returns:
        list:
            List of tuples (path, score) sorted by score descending.
            Returns empty list if query is empty.
    """
    if not query or not paths:
        return []

    # Use custom scorer if not provided
    if scorer is None:
        scorer = fzf_scorer

    # Use RapidFuzz's process.extract for fast searching
    results = process.extract(
        query=query,
        choices=paths,
        scorer=scorer,
        limit=limit,
        score_cutoff=0,  # Only return actual matches (score > 0)
    )

    # Results are tuples of (choice, score, index)
    # We only need (choice, score)
    return [(choice, score) for choice, score, _ in results]
