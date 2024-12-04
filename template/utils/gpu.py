import numpy as np
import bittensor as bt
import torch


class GPUInfo:
    def log_gpu_info():
        bt.logger.info(
            f"""Total GPU memory: {GPUInfo.total_memory} GB
                    Free GPU memory: {GPUInfo.free_memory} GB
                    Used GPU memory: {GPUInfo.used_memory} GB
                    GPU utilization: {GPUInfo.gpu_utilization * 100}%"""
        )

    
    def total_memory(cls):
        return np.sum([torch.cuda.get_device_properties(i).total_memory / (1024**3) for i in range(cls.n_gpus)])

    
    def used_memory(cls):
        return cls.total_memory - cls.free_memory

    
    def free_memory(cls):
        return np.sum([torch.cuda.mem_get_info(i)[0] / (1024**3) for i in range(cls.n_gpus)])

    
    def n_gpus(cls):
        return torch.cuda.device_count()

    
    def gpu_utilization(cls):
        return cls.used_memory / cls.total_memory
