from pathlib import Path
import json
import pdf2image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from label_handler import AnnotationsFileModel, PageModel
import pydantic
from utils import get_parsed_annotation


def get_page_data(file_data, page_number:str):
    if page_number not in file_data.keys():
        raise ValueError("there is no such page in the file data")
    
    return file_data[page_number]


def visualize_img_with_bbox(file_path, page_number: int, page_data: PageModel):
    """
    Renders a specific page of a PDF, draws scaled bounding boxes from annotations,
    and displays the result.

    Args:
        file_path (Path): The path to the PDF file.
        page_number (int): The 0-based index of the page to visualize.
        page_data (PageModel): The Pydantic object containing annotations for that page.
    """
    try:
        pil_image = pdf2image.convert_from_path(
            file_path, 
            dpi=300, 
            first_page=page_number + 1,
            last_page=page_number + 1
        )[0]
    except pdf2image.exceptions.PDFPageCountError:
        print(f"Error: Page number {page_number} is out of range for the PDF '{file_path.name}'.")
        return

    img_arr = np.array(pil_image)
    
    image_height, image_width, _ = img_arr.shape
    
    annotation_width = page_data.page_size.width
    annotation_height = page_data.page_size.height
    
    x_scale = image_width / annotation_width
    y_scale = image_height / annotation_height

    print(f"Image Pixel Shape: (Height={image_height}, Width={image_width})")
    print(f"Annotation Coordinate Size: (Height={annotation_height}, Width={annotation_width})")
    print(f"Calculated Scaling factors -> x_scale: {x_scale:.3f}, y_scale: {y_scale:.3f}\n")

    fig, ax = plt.subplots(figsize=(15, 15 * image_height / image_width)) 
    ax.imshow(img_arr)
    
    print(f"Drawing {len(page_data.annotations)} bounding boxes...")
    for ann in page_data.annotations:
        bbox = ann.bbox
        
        scaled_x = bbox.x * x_scale
        scaled_y = bbox.y * y_scale
        scaled_width = bbox.width * x_scale
        scaled_height = bbox.height * y_scale
    
        rect = patches.Rectangle(
            (scaled_x, scaled_y),
            scaled_width,
            scaled_height,
            linewidth=2,
            edgecolor='lime', 
            facecolor='none'
        )
        ax.add_patch(rect)

        ax.text(
            scaled_x, 
            scaled_y - 10,
            ann.category, 
            color='lime', 
            fontsize=14,
            bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', pad=0.2)
        )

    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.show()
        

def visualize_img(file_path, page_number):
    PIL_objects = pdf2image.convert_from_path(file_path)
    
    assert page_number < len(PIL_objects)
    
    PIL_obj = PIL_objects[page_number]
    
    # convert PIL to numpy arr
    img_arr = np.array(PIL_obj)
    
    # visalize the thing
    plt.imshow(img_arr)
    plt.show()
    
    
    
def fanfo_data(cfg):
    parsed_annotations = get_parsed_annotation(cfg.paths.annotation_file)
    
    pdf_paths = sorted(cfg.paths.pdf_folder.glob("*.pdf"))
    
    sample_number = 40
    
    sample_path = pdf_paths[sample_number]
    
    print(f"SAMPLE PATH: {sample_path}")
    
    if sample_path.name not in parsed_annotations:
        print(f"Error: No annotations found for file '{sample_path.name}'")
        return
        
    file_data = parsed_annotations[sample_path.name]
    
    if not file_data:
        print(f"Error: Annotation data for '{sample_path.name}' is empty.")
        return
        
    sample_page_name = list(file_data.keys())[1] 
    print(f"Found annotations for page: '{sample_page_name}'")

    page_data = get_page_data(file_data, sample_page_name)
    
    # Translate the string "page_2" into the integer index 1
    # 1. Split 'page_2' -> ['page', '2']
    # 2. Get the last part -> '2'
    # 3. Convert to integer -> 2
    # 4. Subtract 1 for 0-based index -> 1
    page_index = int(sample_page_name.split('_')[-1]) - 1
    
    print(f"Translated '{sample_page_name}' to 0-based index: {page_index}")

    visualize_img_with_bbox(sample_path, page_number=page_index, page_data=page_data)
    
    
    
    
    
    