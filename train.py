from ultralytics import YOLO
import multiprocessing 

def train():
    # get the model. the smallest one for now
    # TODO: this can be configged. we can do it later.
    # for now lets finish this damn thing
    model = YOLO("yolov8n.pt")

    # Set epochs back to a reasonable number, like 10 or 25
    model.train(
        data="doc_detector.yaml", 
        epochs=100, 
        imgsz=640, 
        device=0,         
        workers=0         
    )

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    train()