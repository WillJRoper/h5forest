"""Fuzzy matching utilities for searching HDF5 tree paths.

This module provides fuzzy matching functionality using RapidFuzz's default
scoring algorithm for fast searching through large lists of paths.

Example usage:
    from h5forest.fuzzy import search_paths

    results = search_paths("grpmass", all_paths, limit=20)
    # Returns: [("/Group1/Mass_Data", 95.0), ("/Group2/Mass", 88.5), ...]
"""

from rapidfuzz import process, utils


def get_match_indices(query, text):
    """
    Get the character indices in text that match the query.

    This performs a simple subsequence match to find which characters
    in the text correspond to characters in the query.

    Args:
        query (str):
            The search query string.
        text (str):
            The text to find matches in.

    Returns:
        list:
            List of character indices in text that matched query characters.
            Returns empty list if no match or empty query.
    """
    if not query or not text:
        return []

    query_lower = query.lower()
    text_lower = text.lower()
    matched_indices = []
    text_idx = 0

    # Try to find each query character in order
    for char in query_lower:
        try:
            text_idx = text_lower.index(char, text_idx)
            matched_indices.append(text_idx)
            text_idx += 1
        except ValueError:
            # Character not found - return what we have so far
            return matched_indices

    return matched_indices


def search_paths(query, paths, limit=20):
    """
    Search for paths matching the query using fuzzy matching.

    Uses RapidFuzz's default scoring algorithm with case-insensitive
    matching. Only returns results where all query characters appear in
    order in the path.

    Args:
        query (str):
            The search query string.
        paths (list):
            List of path strings to search through.
        limit (int):
            Maximum number of results to return (default: 20).

    Returns:
        list:
            List of tuples (path, score) sorted by score descending.
            Returns empty list if query is empty.
    """
    if not query or not paths:
        return []

    # Use RapidFuzz's process.extract with default scorer and
    # case-insensitive processor. Request more results than limit
    # to account for filtering
    results = process.extract(
        query=query,
        choices=paths,
        limit=limit * 3,  # Get 3x more results since we'll filter them
        processor=utils.default_process,  # Lowercase and strip whitespace
    )

    # Filter results to only include paths where all query characters
    # appear in order
    filtered_results = []
    for choice, score, _ in results:
        # Check if all query characters are present in order
        matched_indices = get_match_indices(query, choice)
        if len(matched_indices) == len(query):
            # All query characters found in order
            filtered_results.append((choice, score))
            if len(filtered_results) >= limit:
                break

    return filtered_results
