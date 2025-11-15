import argparse
from pathlib import Path
import yaml
from config import AppModel
import pydantic
import sys

def get_cfg():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-cfg","--config", required=True)
    
    args = parser.parse_args()
    
    CONFIG_PATH = Path.cwd() / f"{args.config}.yaml"
    
    with open(CONFIG_PATH,'r') as f:
        cfg_dict = yaml.safe_load(f)
        
    try:
        cfg = AppModel(**cfg_dict)
    except pydantic.ValidationError as e:
        print(f"VALIDATION ERROR: {e}")
        sys.exit(1)
    
    return cfg