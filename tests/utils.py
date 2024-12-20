
import os
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent.parent

def write_prompt_to_file(prompt: str) -> None:
    write_dir = os.path.join(ROOT_DIR, 'tests', 'logs')
    if not os.path.exists(write_dir):
        os.makedirs
    file_path: str = os.path.join(write_dir, 'test_prompt_{}.txt'.format(str(uuid.uuid4())))  
    with open(file_path, 'w') as file:
        file.write(prompt)