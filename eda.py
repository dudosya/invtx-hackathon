from pathlib import Path
import json
import pdf2image
import numpy as np
import matplotlib.pyplot as plt

def fanfo_data(cfg):
    with open(cfg.paths.annotation_file,'r', encoding='utf-8') as f:
        annot_dict = json.load(f)
        
    # somehow get the pdf paths
    pdf_paths = sorted(cfg.paths.pdf_folder.glob("*.pdf"))
    
    sample_num = 3
    
    sample_path = pdf_paths[sample_num]
    
    print(f"SAMPLE PATH: {sample_path}")
    
    # convert pdf to img
    
    PIL_objects = pdf2image.convert_from_path(sample_path)
    
    PIL_obj = PIL_objects[sample_num]
    
    # convert PIL to numpy arr
    img_arr = np.array(PIL_obj)
    
    # visalize the thing
    plt.imshow(img_arr)
    plt.show()
    
    # get the bounding boxes from annotations
    
    # o
    