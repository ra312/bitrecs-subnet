"""
Global constants

Constants:
    MAX_DENDRITE_TIMEOUT (int): Length of seconds given to miners to respond to a dendrite request.
    MIN_QUERY_LENGTH (int): Minimum length of a query.
    MAX_QUERY_LENGTH (int): Maximum length of a query.
    MAX_RECS_PER_REQUEST (int): Maximum number of recommendations per request.
    MAX_CONTEXT_LENGTH (int): Maximum length of a context.
    MIN_CATALOG_SIZE (int): Minimum size of a request catalog.
    
"""

MAX_DENDRITE_TIMEOUT = 5
MIN_QUERY_LENGTH = 3
MAX_QUERY_LENGTH = 100
MAX_RECS_PER_REQUEST = 20
MAX_CONTEXT_LENGTH = 200000
MIN_CATALOG_SIZE = 10
MINER_BATTERY_INTERVAL = 300