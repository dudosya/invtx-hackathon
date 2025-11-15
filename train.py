from ultralytics import YOLO
import multiprocessing 

def train():
    # get the model. the smallest one for now
    # TODO: this can be configged. we can do it later.
    # for now lets finish this damn thing
    model = YOLO("yolov8n.pt")

    model.train(
        data="doc_detector.yaml",
        epochs=100,
        imgsz=640,
        device=0,
        workers=0,
        name='600_dpi',              
    )

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    train()