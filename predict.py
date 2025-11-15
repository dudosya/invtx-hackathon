# HOLY MOTHER OF VIBE CODE
# I SUCCUMBED TO THE EVIL

import argparse
from pathlib import Path
from ultralytics import YOLO
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
import cv2
import numpy as np
from tqdm import tqdm

def predict_on_page(pdf_path: Path, page_num_1_based: int, model: YOLO, output_dir: Path):
    """
    Processes a single page of a PDF, runs object detection, and saves the annotated image.

    Args:
        pdf_path (Path): Path to the input PDF file.
        page_num_1_based (int): The 1-based page number to process.
        model (YOLO): The loaded YOLO model instance.
        output_dir (Path): The directory to save the output image.
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
        return

    if not pil_images:
        print(f"Could not extract page {page_num_1_based} from {pdf_path.name}. It might be out of range.")
        return

    pil_image = pil_images[0]

    # 2. Run Inference
    results = model.predict(source=pil_image, conf=0.4, verbose=False) # verbose=False for cleaner folder processing
    result = results[0]

    # 3. Visualize the Results
    annotated_image_array_bgr = result.plot()

    # 4. Save the Output
    annotated_image_array_rgb = cv2.cvtColor(annotated_image_array_bgr, cv2.COLOR_BGR2RGB)
    final_image = Image.fromarray(annotated_image_array_rgb)
    
    output_filename = f"{pdf_path.stem}_page_{page_num_1_based}_predictions.jpg"
    output_path = output_dir / output_filename
    final_image.save(output_path)
    # The print statement is removed from here to be handled by the tqdm progress bar

def main():
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run detection on PDF files. Can process a single file, a specific page, or a whole directory.")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input PDF file or a directory containing PDF files."
    )
    parser.add_argument(
        "--page",
        type=int,
        default=None, # Make page optional
        help="Optional: 1-based page number to process for a single PDF. If not provided, all pages are processed."
    )
    args = parser.parse_args()

    # --- Setup Paths ---
    input_path = Path(args.input)
    model_weights_path = Path("runs/detect/600_dpi/weights/best.pt")
    # --- NEW: Create a model-specific output directory ---
    # Extracts the experiment name (e.g., 'train4') from the model path.
    # Path(...).parent.parent.name gets the name of the grandparent directory.
    model_name = model_weights_path.parent.parent.name
    output_dir = Path("predictions") / model_name  # e.g., predictions/train4
    output_dir.mkdir(parents=True, exist_ok=True) # Create output dir ahead of time

    # --- Validate Paths ---
    if not input_path.exists():
        print(f"Error: Input path not found at '{input_path}'")
        return
    if not model_weights_path.exists():
        print(f"Error: Model weights not found at '{model_weights_path}'")
        print("Please ensure you have trained the model and the path is correct.")
        return

    # --- Load the Model (once) ---
    print(f"Loading model from {model_weights_path}...")
    model = YOLO(model_weights_path)

    # --- Determine Mode: File or Directory ---
    pdf_files_to_process = []
    if input_path.is_dir():
        print(f"Input is a directory. Searching for PDF files in '{input_path}'...")
        pdf_files_to_process = sorted(list(input_path.glob("*.pdf")))
        if not pdf_files_to_process:
            print("No PDF files found in the directory.")
            return
        print(f"Found {len(pdf_files_to_process)} PDF file(s).")

    elif input_path.is_file() and input_path.suffix.lower() == '.pdf':
        print(f"Input is a single file: '{input_path.name}'")
        pdf_files_to_process.append(input_path)

    else:
        print(f"Error: Input path '{input_path}' is not a valid PDF file or directory.")
        return
        
    # --- Main Processing Loop ---
    for pdf_path in tqdm(pdf_files_to_process, desc="Processing PDFs"):
        try:
            # Efficiently get page count without rendering the whole PDF
            info = pdfinfo_from_path(pdf_path)
            total_pages = info['Pages']
        except Exception as e:
            print(f"\nCould not get info for {pdf_path.name}. Skipping. Error: {e}")
            continue

        # Logic for which pages to process
        pages_to_process = []
        if input_path.is_file() and args.page is not None:
            # Single file, specific page
            if 1 <= args.page <= total_pages:
                pages_to_process.append(args.page)
            else:
                print(f"\nWarning: Page {args.page} is out of range for {pdf_path.name} which has {total_pages} pages. Skipping file.")
                continue
        else:
            # Directory OR single file with all pages
            pages_to_process = range(1, total_pages + 1)
        
        # Process the selected pages for the current PDF
        for page_num in tqdm(pages_to_process, desc=f"Pages in {pdf_path.name}", leave=False):
            predict_on_page(pdf_path, page_num, model, output_dir)
            
    print("\nProcessing complete.")
    print(f"All predictions saved in: {output_dir.resolve()}")


if __name__ == "__main__":
    main()