"""Fuzzy matching utilities for searching HDF5 tree paths.

This module provides fuzzy matching functionality using RapidFuzz's default
scoring algorithm for fast searching through large lists of paths.

Example usage:
    from h5forest.fuzzy import search_paths

    results = search_paths("grpmass", all_paths, limit=20)
    # Returns: [("/Group1/Mass_Data", 95.0), ("/Group2/Mass", 88.5), ...]
"""

from rapidfuzz import process


def search_paths(query, paths, limit=20):
    """
    Search for paths matching the query using fuzzy matching.

    Uses RapidFuzz's default scoring algorithm for matching.

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

    # Use RapidFuzz's process.extract with default scorer
    results = process.extract(
        query=query,
        choices=paths,
        limit=limit,
    )

    # Results are tuples of (choice, score, index)
    # We only need (choice, score)
    return [(choice, score) for choice, score, _ in results]
