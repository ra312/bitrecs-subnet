import os
import time
import requests
import json
import secrets
import bittensor as bt
from urllib.parse import urlparse
from typing import Any, Dict, Tuple
from datetime import datetime
from dataclasses import asdict, dataclass, field
from substrateinterface import Keypair
from bitrecs.utils import constants as CONST
SERVICE_URL = os.environ.get("BITRECS_PROXY_URL", "").removesuffix("/") if os.environ.get("BITRECS_PROXY_URL") else ""


@dataclass
class ValidatorUploadRequest:
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    hot_key: str = field(default_factory=str)
    val_uid: int = field(default=0)
    step: str = field(default_factory=str)
    llm_provider: str = field(default_factory=str)
    llm_model: str = field(default_factory=str)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
    

def create_secure_message(timestamp: int, report: ValidatorUploadRequest, nonce: str = None) -> Tuple[bytes, str]:    
    if nonce is None:
        nonce = secrets.token_hex(16)    
    report_json = json.dumps(report.to_dict(), sort_keys=True)
    components = [
        str(timestamp),
        report.hot_key,
        report_json,
        nonce
    ]
    message = '.'.join(components)
    return message.encode('utf-8'), nonce


def get_r2_upload_url(report: ValidatorUploadRequest, keypair: Keypair) -> str:    
    if not SERVICE_URL:
        bt.logging.warning("BITRECS_PROXY_URL is not set. Skipping R2 upload URL generation.")
        return ""
        
    request_url = f"{SERVICE_URL}/validator/upload"    
    timestamp = int(time.time())
    message, nonce = create_secure_message(timestamp, report)
    sig = keypair.sign(message).hex()
    report_dict = report.to_dict()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Signature': sig,
        'X-Timestamp': str(timestamp),
        'X-Nonce': nonce
    }
    
    try:
        response = requests.post(
            request_url, 
            json=report_dict,
            headers=headers,
            timeout=10  # Add timeout to prevent hanging
        )        
        
        if response.status_code == 200:
            result = response.json()
            if "signed_url" in result:
                return result["signed_url"]
            else:                
                bt.logging.error("No signed_url in response")
                bt.logging.trace("Response:", json.dumps(result, indent=2))
                return ""
        else:            
            bt.logging.error(f"Request failed with status code: {response.status_code}")
            bt.logging.error(response.text)
            return ""

    except requests.exceptions.RequestException as e:
        bt.logging.error(f"Error connecting to R2 proxy: {e}")
        return ""


def put_r2_upload(request: ValidatorUploadRequest, keypair: Keypair) -> bool:
    if not request or not keypair:
        return False    
    
    data_file = os.path.join(CONST.ROOT_DIR, "miner_responses.db")
    if not os.path.exists(data_file):
        bt.logging.error(f"Miner response file does not exist: {data_file}")
        return False
    
    signed_url = get_r2_upload_url(request, keypair)
    if not is_valid_url(signed_url):
        bt.logging.error("Failed to get signed URL")
        return False
    
    bt.logging.trace("STARTING UPLOAD -----------------------------------------")
    try:
        with open(data_file, 'rb') as f:
            file_data = f.read()
            
        headers = {
            'Content-Type': 'application/x-sqlite3',
            'Content-Length': str(len(file_data))
        }        
        
        response = requests.put(
            signed_url, 
            data=file_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in (200, 201):
            bt.logging.info("Successfully uploaded to R2")
            bt.logging.info("FINISHED UPLOAD SUCCESS -----------------------------------------")
            return True
        else:
            bt.logging.error(f"Upload failed with status code: {response.status_code}")
            bt.logging.error("Response headers:", dict(response.headers))
            bt.logging.error("Response body:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:        
        bt.logging.error(f"Upload request failed: {str(e)}")
        return False
    except IOError as e:        
        bt.logging.error(f"File operation failed: {str(e)}")
        return False
    except Exception as e:        
        bt.logging.error(f"Unexpected error: {str(e)}")
        return False