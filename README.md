# Signature, stamp and QR code detection on documents

## Project Overview

This project implements a complete computer vision pipeline to detect and locate specific objects [signatures, QR codes, and stamps] within PDF documents. 

## End-to-End Workflow

1.  **Prepare Data**: Run `python preprocess_data.py` to convert raw PDFs and JSON annotations into JPG images and YOLO-formatted `.txt` labels.

2.  **Split Dataset**: Execute `python split_data.py` to automatically divide the processed data into training and validation sets, creating the final `dataset/` directory.

3.  **Train Model**: Run `python train.py` to train the YOLOv8 model on the prepared dataset. The best model weights are saved in the `runs/detect/` directory.

4.  **Run Inference**: Use a trained model with `python predict.py` to detect objects in new PDF documents, generating annotated images and a structured JSON output.



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

## Data Preprocessing

The `preprocess_data.py` script is the crucial first step to transform the raw dataset into a format suitable for training an object detection model.

### Usage

To run the script, execute it from the terminal, specifying the configuration file:

```bash
python preprocess_data.py --config config
```

### Configuration

The script relies on paths defined in `config.yaml`. Ensure the following paths are correctly set:

```yaml
paths:
  annotation_file: "data/selected_annotations.json" # Input: Raw JSON annotations
  pdf_folder: "data/pdfs"                         # Input: Folder with raw PDFs
  processed_output: "data/processed"              # Output: Destination for processed data
```

### Key Steps & Logic

The script performs two critical transformations for each annotated page in the dataset:

1.  **PDF to Image Conversion:**
    *   Each PDF page with annotations is converted into a high-resolution JPG image (`dpi=300`). This DPI setting is important for preserving the detail of small objects like signatures and QR codes.

2.  **Annotation to YOLO Format:**
    *   The script reads the absolute pixel coordinates (`x`, `y`, `width`, `height`) from the JSON file.
    *   It then converts these coordinates into the **normalized YOLO format**, which is required by the model. This involves scaling all values to be between 0 and 1, relative to the image's total width and height.
    *   The final labels are saved as `.txt` files, with each line representing one object in the format:
        `<class_id> <x_center_norm> <y_center_norm> <width_norm> <height_norm>`

### Output Structure

After running, the script populates the `output` directory with a clean, model-ready structure. The image and label files share the same base name for easy pairing during training.

```
root/
└── output/
    ├── images/
    │   ├── document1_page_1.jpg
    │   ├── document1_page_2.jpg
    │   └── ...
    └── labels/
        ├── document1_page_1.txt
        ├── document1_page_2.txt
        └── ...
```

## Splitting the Dataset

This script prepares the data for model training by splitting it into training and validation sets.

### Usage

Run the script from the project root:

```bash
python split_data.py
```

This will take the contents of the `output/` directory, perform a random 80/20 split, and create the final YOLO-compatible structure in a new `dataset/` folder. The `output/` directory will be empty after the script runs.

### Output Structure

```
dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

## Prediction

To run inference on a new PDF, use the `predict.py` script. You must provide the path to the PDF and the 1-based page number you want to analyze.


Three ways to run it:

1.  **Process a specific page of a single PDF :**
    ```bash
    python predict.py --input data/pdfs/some_document.pdf --page 2
    ```

2.  **Process all pages of a single PDF:**
    ```bash
    python predict.py --input data/pdfs/some_document.pdf
    ```

3.  **Process all pages of all PDFs in a directory:**
    ```bash
    # Assuming you have a folder named 'test' with PDFs in it
    python predict.py --input test/
    ```


## Training

The model is trained using the Ultralytics YOLOv8 framework.

### Usage

To start training, run the script from the project root:

```bash
python train.py
```

### Configuration

-   Dataset configuration (paths, class names) is defined in `doc_detector.yaml`.
-   Training hyperparameters (epochs, image size, etc.) are set directly within the `train.py` script.

### Output

Trained model weights, logs, and validation results will be saved automatically to a new directory inside `runs/detect/`.

## Model Performance

Several experiments were conducted to determine the optimal preprocessing pipeline and training configuration. The key objective was to maximize the model's ability to detect signatures, QR codes, and stamps accurately. The results of these experiments are summarized below.

### Summary of Experiments

| # | Experiment Name          | Key Pipeline Details                 | Overall mAP50 | Overall mAP50-95 | Signature mAP50 | QR mAP50 | Stamp mAP50 |
|---|--------------------------|--------------------------------------|---------------|------------------|-----------------|----------|-------------|
| 1 | Baseline                 | 300 DPI, Color                       | 0.569         | 0.475            | 0.595           | 0.336    | 0.775       |
| 2 | Less Augmentation        | 300 DPI, Color, Reduced Aug          | 0.564         | 0.470            | 0.560           | 0.357    | 0.775       |
| 3 | Lower Learning Rate      | 300 DPI, Color                       | 0.569         | 0.475            | 0.595           | 0.336    | 0.775       |
| 4 | High Resolution (Color)  | 600 DPI, Color                       | 0.883         | 0.718            | 0.659           | 0.995    | 0.995       |
| 5 | High Res (Grayscale)     | 600 DPI, Grayscale, No Contrast      | 0.874         | 0.751            | 0.740           | 0.995    | 0.887       |
| 6 | **Grayscale and Contrast** | **300 DPI, Grayscale + High Contrast** | **0.920**     | **0.777**        | **0.769**       | **0.995**| **0.995**   |


