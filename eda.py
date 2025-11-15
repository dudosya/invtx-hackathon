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
    