

File: C:\Users\aezak\Desktop\desktop folder\swe\invtx_hackathon_folder\invtx-hackathon\config.py
```python
import pydantic
from pathlib import Path
import yaml

class PathsModel(pydantic.BaseModel):
    annotation_file: Path
    pdf_folder: Path

    @pydantic.validator('annotation_file', 'pdf_folder', pre=True)
    def make_path_absolute(cls, v):
        return Path.cwd() / v

class AppModel(pydantic.BaseModel):
    paths: PathsModel
```



File: C:\Users\aezak\Desktop\desktop folder\swe\invtx_hackathon_folder\invtx-hackathon\config.yaml
```yaml
paths:
  annotation_file: "data/selected_annotations.json"
  pdf_folder: "data/pdfs"
```



File: C:\Users\aezak\Desktop\desktop folder\swe\invtx_hackathon_folder\invtx-hackathon\eda.py
```python
from pathlib import Path
import json

def fanfo_data(cfg):
    with open(cfg.paths.annotation_file,'r', encoding='utf-8') as f:
        annot_dict = json.load(f)
        
    # somehow get the pdf paths
    pdf_paths = sorted(cfg.paths.pdf_folder.glob("*.pdf"))
    
    sample_num = 3
    
    sample_path = pdf_paths[sample_num]
    
    print(f"SAMPLE PATH: {sample_path}")
    
    # conver convert pdf to img
    
```



File: C:\Users\aezak\Desktop\desktop folder\swe\invtx_hackathon_folder\invtx-hackathon\main.py
```python
from pathlib import Path
import argparse
import yaml
from config import AppModel
import pydantic
import sys
from eda import fanfo_data


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
    

def main():
    cfg = get_cfg()
    
    fanfo_data(cfg)



if __name__ == "__main__":
    main()

    

    
    
    
```



File: C:\Users\aezak\Desktop\desktop folder\swe\invtx_hackathon_folder\invtx-hackathon\README.md
# invtx-hackathon

