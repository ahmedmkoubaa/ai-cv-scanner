import re
from enum import Enum


class QueryIntent(str, Enum):
    SEMANTIC = "semantic"
    INVENTORY_COUNT = "inventory_count"
    INVENTORY_LIST = "inventory_list"


INVENTORY_TERMS = (
    "candidate",
    "candidates",
    "cv",
    "cvs",
    "resume",
    "resumes",
    "indexed",
    "database",
    "profile",
    "profiles",
)

COUNT_PHRASES = (
    "how many",
    "total number",
    "count of",
    "number of",
    "how many cvs",
    "how many cv",
)

LIST_PHRASES = (
    "list all",
    "list every",
    "all candidates",
    "all candidate",
    "all cvs",
    "all cv",
    "every candidate",
    "show all",
    "name all",
    "names of all",
)


def detect_query_intent(query: str) -> QueryIntent:
    normalized = re.sub(r"\s+", " ", query.lower().strip())
    if not normalized:
        return QueryIntent.SEMANTIC

    has_inventory_context = any(term in normalized for term in INVENTORY_TERMS)
    has_count_phrase = any(phrase in normalized for phrase in COUNT_PHRASES)
    has_list_phrase = any(phrase in normalized for phrase in LIST_PHRASES)

    if has_list_phrase or _looks_like_list_request(normalized, has_inventory_context):
        return QueryIntent.INVENTORY_LIST

    if has_count_phrase and (
        has_inventory_context or _looks_like_global_count(normalized)
    ):
        return QueryIntent.INVENTORY_COUNT

    return QueryIntent.SEMANTIC


def _looks_like_list_request(normalized: str, has_inventory_context: bool) -> bool:
    if re.search(r"\blist\b.*\b(names?|candidates?|cvs?|profiles?)\b", normalized):
        return True
    if re.search(r"\b(names?|candidates?|cvs?|profiles?)\b.*\blist\b", normalized):
        return True
    return has_inventory_context and re.search(
        r"\b(enumerate|inventory|catalogue|catalog)\b", normalized
    )


def _looks_like_global_count(normalized: str) -> bool:
    patterns = (
        r"\bhow many\b.*\b(do we have|are there|are indexed|in the system|in total|available|stored)\b",
        r"\btotal number\b.*\b(of|in)\b",
        r"\bcount of\b.*\b(candidates?|cvs?|resumes?|profiles?|indexed)\b",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)
