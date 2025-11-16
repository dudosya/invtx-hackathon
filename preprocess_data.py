from utils import get_cfg, get_parsed_annotation
import pathlib
import pdf2image
import PIL
from tqdm import tqdm
from PIL import Image, ImageOps

CLASS_MAP = {"signature": 0, "qr":1, "stamp":2}

def main_preprocess():
    cfg = get_cfg()
    
    # define paths
    image_path = cfg.paths.processed_output / "images"
    label_path = cfg.paths.processed_output / "labels"
    #create dirs
    image_path.mkdir(parents=True,exist_ok=True)
    label_path.mkdir(parents=True,exist_ok=True)
    
    # get annotation data
    annotation_data = get_parsed_annotation(cfg.paths.annotation_file)
    
    # class counter for frequency mapping
    class_counter = {"signature": 0, "qr":0, "stamp":0}
    total_num_of_imgs_processed = 0
    
    # iterate thru annotation data
    
    for pdf_filename, file_data in tqdm(annotation_data.items(), desc="PDF processor"):
        print(f"PROCESSING {pdf_filename}")
        for page_name, page_data in file_data.items():
            print(f"PROCESSING {page_name}")
            # define unique base filename
            base_filename = f"{pathlib.Path(pdf_filename).stem}_{page_name}"
            
            # get the source pdf path
            source_pdf_path = cfg.paths.pdf_folder / pdf_filename
            
            # Translate the string "page_2" into the integer index 1
            # 1. Split 'page_2' -> ['page', '2']
            # 2. Get the last part -> '2'
            # 3. Convert to integer -> 2
            # 4. Subtract 1 for 0-based index -> 1
            page_index = int(page_name.split('_')[-1]) - 1
            
            # convert that specific page of pdf to img
            pil_object_list = pdf2image.convert_from_path(
                source_pdf_path,
                dpi=600,
                first_page=page_index+1,
                last_page=page_index+1
                )
            
            #convert from path ALWAYS returns a list. therefore, it is here for clarification
            pil_object = pil_object_list[0]
            
            # grayscale + contrast
            pil_object = ImageOps.grayscale(pil_object)
            #pil_object = ImageOps.autocontrast(pil_object, cutoff=5)
            
            
            #define save path
            output_image_path = image_path / f"{base_filename}.jpg"
            
            #save the pil object
            pil_object.save(output_image_path)
            
            # increment the total num of imgs counter here
            total_num_of_imgs_processed += 1
            
            # define save path for the yolo annotations
            output_label_path = label_path / f"{base_filename}.txt"
            yolo_annotations = []
            
            for ann in page_data.annotations:
                
                # normalization calculcations
                x_center_norm = (ann.bbox.x + ann.bbox.width / 2) / page_data.page_size.width
                y_center_norm = (ann.bbox.y + ann.bbox.height / 2) / page_data.page_size.height
                width_norm = ann.bbox.width / page_data.page_size.width
                height_norm = ann.bbox.height / page_data.page_size.height
                
                #integer assoc with the category
                class_id = CLASS_MAP[ann.category]
                
                #increment counter
                class_counter[ann.category] += 1
                
                # YOLO format string
                yolo_format_string = f"{class_id} {x_center_norm} {y_center_norm} {width_norm} {height_norm}"
                yolo_annotations.append(yolo_format_string)
            
            with open(output_label_path,'w') as f:
                f.write("\n".join(yolo_annotations))
                
    # SOME STATISTICS on the preprocessing
    # VIBECODED
    print("\nDataset Processing Complete.")
    print("---------------------------")
    print(f"Total images processed: {total_num_of_imgs_processed}")
    print("Class Distribution:")
    # Loop through your class_counter dictionary to print each class
    for class_name, count in class_counter.items():
        print(f"- {class_name}: {count} instances")
    print("---------------------------")
    print(f"Dataset ready at: {cfg.paths.processed_output.resolve()}") # .resolve() gives the full, absolute path
            

if __name__ == "__main__":
    main_preprocess()