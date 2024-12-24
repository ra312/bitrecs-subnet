

import bittensor as bt
from template.commerce.product import Product, ProductFactory
from template.protocol import BitrecsRequest
from template.utils import constants as CONST


def validate_br_request(synapse: BitrecsRequest) -> bool:        
    if not isinstance(synapse, BitrecsRequest):
        bt.logging.error(f"Invalid synapse item: {synapse}")
        return False
    if len(synapse.query) < CONST.MIN_QUERY_LENGTH or len(synapse.query) > CONST.MAX_QUERY_LENGTH:
        bt.logging.error(f"Invalid synampse Query!: {synapse}")
        return False
    if len(synapse.results) != 0:
        bt.logging.error(f"Results it not empty!: {synapse}")
        return False
    if synapse.context is None or synapse.context == "":
        bt.logging.error(f"Context is empty!: {synapse}")
        return False
    if len(synapse.context) > CONST.MAX_CONTEXT_LENGTH:
        bt.logging.error(f"Context is too long!: {synapse}")
        return False
    if len(synapse.models_used) != 0:
        bt.logging.error(f"Models used is not empty!: {synapse}")
        return False
    if synapse.site_key is None or synapse.site_key == "":
        bt.logging.error(f"Site key is empty!: {synapse}")
        return False
    if synapse.num_results < 1 or synapse.num_results > CONST.MAX_RECS_PER_REQUEST:
        bt.logging.error(f"Number of recommendations should be less than {CONST.MAX_RECS_PER_REQUEST}!: {synapse}")
        return False
    
    store_catalog: list[Product] = ProductFactory.try_parse_context(synapse.context)
    if len(store_catalog) < CONST.MIN_CATALOG_SIZE or len(store_catalog) > CONST.MAX_CATALOG_SIZE:
        bt.logging.error(f"Invalid catalog size: {len(store_catalog)}")
        return False
    
    dupe_threshold = .10
    dupes = ProductFactory.get_dupe_count(store_catalog)
    if dupes > len(store_catalog) * dupe_threshold:
        bt.logging.error(f"Too many duplicates in catalog: {dupes}")
        return False


    return True