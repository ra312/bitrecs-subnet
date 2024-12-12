import random
import socket
import bittensor as bt
import numpy as np
from typing import List

from template.base.neuron import BaseNeuron


def check_uid_availability(
    metagraph: "bt.metagraph.Metagraph", uid: int, vpermit_tao_limit: int
) -> bool:
    """Check if uid is available. The UID should be available if it is serving and has less than vpermit_tao_limit stake
    Args:
        metagraph (:obj: bt.metagraph.Metagraph): Metagraph object
        uid (int): uid to be checked
        vpermit_tao_limit (int): Validator permit tao limit
    Returns:
        bool: True if uid is available, False otherwise
    """
    # Filter non serving axons.
    if not metagraph.axons[uid].is_serving:
        return False
    # Filter validator permit > 1024 stake.
    if metagraph.validator_permit[uid]:
        if metagraph.S[uid] > vpermit_tao_limit:
            return False
    # Available otherwise.
    return True


def get_random_uids(self, k: int, exclude: List[int] = None) -> np.ndarray:
    """Returns k available random uids from the metagraph.
    Args:
        k (int): Number of uids to return.
        exclude (List[int]): List of uids to exclude from the random sampling.
    Returns:
        uids (np.ndarray): Randomly sampled available uids.
    Notes:
        If `k` is larger than the number of available `uids`, set `k` to the number of available `uids`.
    """
    candidate_uids = []
    avail_uids = []

    for uid in range(self.metagraph.n.item()):
        uid_is_available = check_uid_availability(
            self.metagraph, uid, self.config.neuron.vpermit_tao_limit
        )
        uid_is_not_excluded = exclude is None or uid not in exclude

        if uid_is_available:
            avail_uids.append(uid)
            if uid_is_not_excluded:
                candidate_uids.append(uid)
    # If k is larger than the number of available uids, set k to the number of available uids.
    k = min(k, len(avail_uids))
    # Check if candidate_uids contain enough for querying, if not grab all avaliable uids
    available_uids = candidate_uids
    if len(candidate_uids) < k:
        available_uids += random.sample(
            [uid for uid in avail_uids if uid not in candidate_uids],
            k - len(candidate_uids),
        )
    uids = np.array(random.sample(available_uids, k))
    return uids


def best_uid(metagraph: bt.metagraph) -> int:
    """Returns the best performing UID in the metagraph."""
    return max(range(metagraph.n), key=lambda uid: metagraph.I[uid].item())


def get_axons(
    self: BaseNeuron,
    *hotkeys,
    not_check_self: bool = False,
    include_hotkeys: bool = False,
):
    result = [
        self.metagraph.axons[uid]
        for uid in range(self.metagraph.n.item())
        if (not_check_self or uid != self.uid)
        and (include_hotkeys or self.metagraph.axons[uid].hotkey in hotkeys)
    ]
    return result


# async def ping_uid(self: BaseNeuron, uid, timeout=5):
#     """
#     Ping a UID to check their availability.
#     Returns True if successful, false otherwise
#     """
#     status_code = None
#     status_message = None
#     try:
#         response = await self.dendrite.query(
#             self.metagraph.axons[uid], 
#             bt.synapse(),
#             deserialize=False,
#             timeout=timeout,
#         )
#         status_code = response.dendrite.status_code
#         status_message = response.dendrite.status_message
#         return status_code == 200, status_message
#     except Exception as e:
#         bt.logging.error(f"Dendrite ping failed: {e}")
#     return False, None

async def ping_uid(self: BaseNeuron, uid, timeout=5) -> bool:
    """
    Ping a UID to check their availability.
    Returns True if successful, false otherwise
    """
    hk = self.metagraph.axons[uid].hotkey
    ip = self.metagraph.axons[uid].ip
    port = self.metagraph.axons[uid].port
    
    ignored = ["localhost", "127.0.0.1", "0.0.0.0"]
    if ip in ignored:
        bt.logging.trace("Ignoring localhost ping.")
        return False    

    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        # Set a timeout of 1 second
        sock.settimeout(timeout)
        # Try to connect to the specified IP and port
        sock.connect((ip, port))
        # If no exception is raised, the port is connected
        return True
    except ConnectionRefusedError:
        # If a ConnectionRefusedError is raised, the port is not connected
        #print(f"Port {port} on IP {ip} is not connected.")
        bt.logging.error(f"Port {port} on IP {ip} is not connected.")
        return False
    except socket.timeout:
        # If a timeout occurs, the port is likely not connected or does not respond
        #print(f"No response from Port {port} on IP {ip}.")
        bt.logging.error(f"No response from Port {port} on IP {ip}.")
        return False
    except Exception as e:
        # For any other exceptions, print an error message and return False
        #print(f"An error occurred: {e}")
        bt.logging.error(f"An error occurred: {e}")
        return False

    finally:
        # Close the socket regardless of whether an exception was raised
        if 'sock' in locals():
            sock.close()

   