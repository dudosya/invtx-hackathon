import argparse
from pathlib import Path
from ultralytics import YOLO
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

# THIS SCRIPT IS A TOTAL VIBE
# PROBABLY LOTSA BULLSHIT HERE THAT NEEDS FIXING 
# KINDA DGAF RN. POHUI+POHUI

def predict_on_page(pdf_path: Path, page_num_1_based: int, model: YOLO, output_dir: Path):
    """
    Processes a single page of a PDF, runs object detection, and saves the annotated image.

    Args:
        pdf_path (Path): Path to the input PDF file.
        page_num_1_based (int): The 1-based page number to process.
        model (YOLO): The loaded YOLO model instance.
        output_dir (Path): The directory to save the output image.
    """
    print(f"Processing {pdf_path.name}, page {page_num_1_based}...")

    # 1. Process the Input PDF: Convert the specified page to a PIL image in memory.
    #    pdf2image uses 1-based indexing for pages, which matches our user input.
    try:
        pil_images = convert_from_path(
            pdf_path,
            dpi=300,  # Use a reasonable DPI for good resolution
            first_page=page_num_1_based,
            last_page=page_num_1_based
        )
    except Exception as e:
        print(f"Error converting PDF page to image: {e}")
        return

    if not pil_images:
        print(f"Could not extract page {page_num_1_based}. It might be out of range.")
        return

    pil_image = pil_images[0]

    # 2. Run Inference: Pass the PIL image directly to the model.
    #    The model handles the conversion to a tensor internally.
    print("Running inference...")
    results = model.predict(source=pil_image, conf=0.4)
    
    # The results object is a list, one for each image. We only have one.
    result = results[0]

    # 3. Visualize the Results: Use the built-in plot() method.
    #    This returns a NumPy array of the image with bounding boxes drawn.
    #    The array is in BGR format by default (used by OpenCV).
    print(f"Found {len(result.boxes)} objects on the page.")
    annotated_image_array_bgr = result.plot()

    # 4. Save the Output:
    #    - Convert the BGR NumPy array to RGB for saving with PIL.
    #    - Create a PIL Image object from the array.
    #    - Construct a descriptive filename and save it.
    
    # Convert from BGR to RGB
    annotated_image_array_rgb = cv2.cvtColor(annotated_image_array_bgr, cv2.COLOR_BGR2RGB)
    
    # Create a PIL image from the NumPy array
    final_image = Image.fromarray(annotated_image_array_rgb)
    
    # Create the output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Construct the output filename
    output_filename = f"{pdf_path.stem}_page_{page_num_1_based}_predictions.jpg"
    output_path = output_dir / output_filename
    
    # Save the final annotated image
    final_image.save(output_path)
    print(f"Successfully saved annotated image to: {output_path.resolve()}")


def main():
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run detection on a single page of a PDF.")
    parser.add_argument(
        "--input", 
        type=str, 
        required=True, 
        help="Path to the input PDF file."
    )
    parser.add_argument(
        "--page", 
        type=int, 
        required=True, 
        help="1-based page number to process."
    )
    args = parser.parse_args()

    # Define paths
    input_pdf_path = Path(args.input)
    model_weights_path = Path("runs/detect/train4/weights/best.pt")
    output_dir = Path("predictions")
    
    # Validate input paths
    if not input_pdf_path.exists():
        print(f"Error: Input PDF not found at '{input_pdf_path}'")
        return
        
    if not model_weights_path.exists():
        print(f"Error: Model weights not found at '{model_weights_path}'")
        print("Please ensure you have trained the model and the path is correct.")
        return

    # --- Load the Model ---
    print(f"Loading model from {model_weights_path}...")
    model = YOLO(model_weights_path)
    
    # --- Run Prediction ---
    predict_on_page(input_pdf_path, args.page, model, output_dir)


if __name__ == "__main__":
    main()