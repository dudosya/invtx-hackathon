from pathlib import Path
import json
import pdf2image
import numpy as np
import matplotlib.pyplot as plt
from label_handler import AnnotationsFileModel
import pydantic

def get_parsed_annotation(annotation_file_path):
    with open(annotation_file_path,'r', encoding='utf-8') as f:
        annot_dict = json.load(f)
        
    parsed_annotations = pydantic.parse_obj_as(AnnotationsFileModel,annot_dict)
    return parsed_annotations


def get_page_data(file_data, page_number:str):
    if page_number not in file_data.keys():
        raise ValueError("there is no such page in the file data")
    
    return file_data[page_number]
        
    

def fanfo_data(cfg):
    parsed_annotations = get_parsed_annotation(cfg.paths.annotation_file)
    
    # somehow get the pdf paths
    pdf_paths = sorted(cfg.paths.pdf_folder.glob("*.pdf"))
    
    sample_num = 3
    
    sample_path = pdf_paths[sample_num]
    
    print(f"SAMPLE PATH: {sample_path}")
    
    # gets the file data
    
    file_data = parsed_annotations[sample_path.name]
    
    # gets the page data
    
    sample_page_number = 'page_10'
    
    page_data = get_page_data(file_data,sample_page_number)
    
    print(type(page_data))
    
    # 
    
    
    
    # get the page data
    
    
    # # convert pdf to img
    
    # PIL_objects = pdf2image.convert_from_path(sample_path)
    
    # PIL_obj = PIL_objects[sample_num]
    
    # # convert PIL to numpy arr
    # img_arr = np.array(PIL_obj)
    
    # # visalize the thing
    # plt.imshow(img_arr)
    # plt.show()
    
    
    
    