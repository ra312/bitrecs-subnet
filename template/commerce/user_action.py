import bittensor as bt
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from neurons.miner import Miner


@dataclass
class UserAction:
    ip: str = field(default_factory=str)
    site_info: str = field(default_factory=str)
    user: str = field(default_factory=str)
    action: str = field(default_factory=str)
    sku: str = field(default_factory=str)
    hot_key: str = field(default=str)
    created_at: str = field(default_factory=str)

    
    @staticmethod
    def get_actions(hot_key: str) -> list["UserAction"]:
        """
        Load all the actions attributed to this miner
        """
        actions = []
        try:
            r = requests.get(f"https://api.bitrecs.ai/miner/{hot_key}")
            actions = r.json()
        except Exception as e:
            bt.logging.error(f"load_user_actions Exception: {e}")
        return actions
    
    
    @staticmethod
    def get_actions_range(start_date: datetime, end_date: datetime) -> list["UserAction"]:
        """
        Load all the actions for miners in a range
        """
        actions = []
        try:
            dt_from = int(start_date.timestamp())
            dt_to = int(end_date.timestamp())
            if dt_from >= dt_to:                
                raise ValueError("Start date must be less than end date")
            r = requests.get(f"https://api.bitrecs.ai/miner/stats/from/{dt_from}/to/{dt_to}")
            actions = r.json()
        except Exception as e:
            bt.logging.error(f"load_user_actions Exception: {e}")
        return actions
    

    @staticmethod
    def get_default_range(days_ago=7) -> tuple:
        """
        Get the default range for the actions
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_ago)
        return start_date, end_date
        