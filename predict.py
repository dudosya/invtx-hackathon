# predict.py

import argparse
from pathlib import Path
from ultralytics import YOLO
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image, ImageOps
import cv2
import numpy as np
from tqdm import tqdm
import json

def predict_on_page(pdf_path: Path, page_num_1_based: int, model: YOLO, output_dir: Path, annotation_id_counter: int):
    """
    Processes a single page of a PDF, runs object detection, saves the annotated image,
    and returns the structured prediction data.

    Returns:
        A tuple containing:
        - A dictionary with the page's prediction data, or None on error.
        - The updated annotation ID counter.
    """
    # 1. Process the Input PDF: Convert the specified page to a PIL image in memory.
    try:
        pil_images = convert_from_path(
            pdf_path,
            dpi=600,
            first_page=page_num_1_based,
            last_page=page_num_1_based
        )
    except Exception as e:
        print(f"Error converting page {page_num_1_based} of {pdf_path.name}: {e}")
        return None, annotation_id_counter

    if not pil_images:
        print(f"Could not extract page {page_num_1_based} from {pdf_path.name}.")
        return None, annotation_id_counter

    pil_image = pil_images[0]
    
    # Apply preprocessing from your version
    pil_image = ImageOps.grayscale(pil_image)
    # pil_image = ImageOps.autocontrast(pil_image, cutoff=2)

    # 2. Run Inference
    results = model.predict(source=pil_image, conf=0.4, verbose=False)
    result = results[0]

    # --- SAVE VISUALIZATION (IMAGE) ---
    annotated_image_array_bgr = result.plot()
    annotated_image_array_rgb = cv2.cvtColor(annotated_image_array_bgr, cv2.COLOR_BGR2RGB)
    final_image = Image.fromarray(annotated_image_array_rgb)
    
    output_filename = f"{pdf_path.stem}_page_{page_num_1_based}_predictions.jpg"
    output_path = output_dir / output_filename
    final_image.save(output_path)

    # --- GENERATE STRUCTURED DATA (FOR JSON) ---
    page_height, page_width = result.orig_shape
    
    annotations_list = []
    for box in result.boxes:
        # Get coordinates in xyxy format and convert to float
        x_min, y_min, x_max, y_max = box.xyxy[0].cpu().numpy().astype(float)
        
        # Calculate width and height for the bbox
        bbox_width = x_max - x_min
        bbox_height = y_max - y_min
        
        # Calculate area
        area = bbox_width * bbox_height
        
        # Get class name
        class_id = int(box.cls[0].cpu().numpy())
        category = result.names[class_id]
        
        # Create the annotation structure
        annotation_detail = {
            "category": category,
            "bbox": {
                "x": round(x_min, 4),
                "y": round(y_min, 4),
                "width": round(bbox_width, 4),
                "height": round(bbox_height, 4)
            },
            "area": round(area, 4)
        }
        
        # Wrap it in the "annotation_XXX" key
        wrapped_annotation = {f"annotation_{annotation_id_counter}": annotation_detail}
        annotations_list.append(wrapped_annotation)
        
        # Increment the unique ID counter for the next annotation
        annotation_id_counter += 1

    # Assemble the final dictionary for the page
    page_data = {
        "annotations": annotations_list,
        "page_size": {
            "width": page_width,
            "height": page_height
        }
    }
    
    return page_data, annotation_id_counter


def main():
    parser = argparse.ArgumentParser(description="Run detection on PDF files and generate JSON output.")
    parser.add_argument("--input", type=str, required=True, help="Path to PDF file or directory.")
    parser.add_argument("--page", type=int, default=None, help="Optional: 1-based page number.")
    args = parser.parse_args()

    input_path = Path(args.input)
    # Using the same model path as your provided script
    model_weights_path = Path("runs/detect/8n_grayscale_600_dpi_no_contrast/weights/best.pt")
    
    model_name = model_weights_path.parent.parent.name
    output_dir = Path("predictions") / model_name
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"Error: Input path not found at '{input_path}'")
        return
    if not model_weights_path.exists():
        print(f"Error: Model weights not found at '{model_weights_path}'")
        return

    print(f"Loading model from {model_weights_path}...")
    model = YOLO(model_weights_path)

    pdf_files_to_process = []
    if input_path.is_dir():
        pdf_files_to_process = sorted(list(input_path.glob("*.pdf")))
        print(f"Found {len(pdf_files_to_process)} PDF file(s) in directory.")
    elif input_path.is_file() and input_path.suffix.lower() == '.pdf':
        pdf_files_to_process.append(input_path)
    else:
        print(f"Error: Input path '{input_path}' is not a valid PDF file or directory.")
        return
    
    # --- Initialize containers for JSON output ---
    all_predictions_data = {}
    annotation_id_counter = 1 # A global counter for unique annotation IDs

    for pdf_path in tqdm(pdf_files_to_process, desc="Processing PDFs"):
        try:
            total_pages = pdfinfo_from_path(pdf_path)['Pages']
        except Exception as e:
            print(f"\nCould not get info for {pdf_path.name}. Skipping. Error: {e}")
            continue

        pages_to_process = range(1, total_pages + 1)
        if input_path.is_file() and args.page is not None:
            if 1 <= args.page <= total_pages:
                pages_to_process = [args.page]
            else:
                print(f"\nWarning: Page {args.page} is out of range. Skipping.")
                continue
        
        for page_num in tqdm(pages_to_process, desc=f"Pages in {pdf_path.name}", leave=False):
            # The function now returns data and the updated counter
            page_data, annotation_id_counter = predict_on_page(
                pdf_path, page_num, model, output_dir, annotation_id_counter
            )
            
            # If data was successfully generated, add it to our main dictionary
            if page_data:
                # Ensure the PDF file key exists
                if pdf_path.name not in all_predictions_data:
                    all_predictions_data[pdf_path.name] = {}
                
                # Add the page data under the page key
                all_predictions_data[pdf_path.name][f"page_{page_num}"] = page_data
                
    # --- SAVE THE FINAL JSON FILE ---
    if all_predictions_data:
        json_output_path = output_dir / "predictions.json"
        print(f"\nSaving prediction data to {json_output_path.resolve()}...")
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_predictions_data, f, ensure_ascii=False, indent=2)
        print("JSON file saved successfully.")
            
    print("\nProcessing complete.")
    print(f"All predictions (images and JSON) saved in: {output_dir.resolve()}")


if __name__ == "__main__":
    main()