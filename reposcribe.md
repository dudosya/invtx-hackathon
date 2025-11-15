

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
import pdf2image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from label_handler import AnnotationsFileModel, PageModel
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
    
    
    
    
    
    
```



File: C:\Users\aezak\Desktop\desktop folder\swe\invtx_hackathon_folder\invtx-hackathon\label_handler.py
```python
import pydantic
import json
from typing import List, Dict

class BboxModel(pydantic.BaseModel):
    x: float
    y: float
    width: float
    height: float

class AnnotationDetailModel(pydantic.BaseModel):
    category: str
    bbox: BboxModel
    area: float
class PageSizeModel(pydantic.BaseModel):
    width: int
    height: int
class PageModel(pydantic.BaseModel):
    annotations: List[AnnotationDetailModel]
    page_size: PageSizeModel

    @pydantic.validator('annotations', pre=True)
    def unwrap_annotations(cls, v):
        """
        Takes the raw list like [{"annotation_117": {...}}]
        and transforms it into a clean list of [{...}].
        """
        # For each item in the list, take the first (and only) value from the dictionary.
        return [list(item.values())[0] for item in v]

AnnotationsFileModel = Dict[str, Dict[str, PageModel]]

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

## Environment Setup

Follow these steps to set up the project environment. This project requires Python 3.8 or higher.

### 1. Install Python Dependencies

First, install the required Python libraries using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 2. Install Poppler

This project uses the `pdf2image` library, which depends on Poppler, a PDF rendering utility. It must be installed and accessible on your system.

**For Windows:**

1.  **Download Poppler:** Download the latest pre-compiled binaries from [this link](https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.11.0-0). Choose the `.zip` file (e.g., `Release-25.11.0-0.zip`).

2.  **Extract Files:** Extract the downloaded zip file to a permanent location, for example, `C:\poppler`.

3.  **Add to System PATH:** You must add the `bin` directory from the extracted folder to your system's PATH variable to make Poppler accessible from the command line.
    *   Search for "Edit the system environment variables" in the Start Menu and open it.
    *   Click on "Environment Variables...".
    *   In the "System variables" section, find `Path`, select it, and click "Edit...".
    *   Click "New" and add the full path to the `bin` folder. For example: `C:\poppler\poppler-23.11.0\Library\bin`
    *   Click "OK" to save and close all windows.

### 3. Verify Installation (Optional)

Open a **new** terminal or command prompt and run `pdfinfo --version`. If it shows the Poppler version information, the setup is complete and correct.

