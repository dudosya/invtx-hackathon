from utils import get_cfg
import pathlib

def main_preprocess():
    cfg = get_cfg()
    
    # define paths
    image_path = cfg.paths.processed_output / "images"
    label_path = cfg.paths.processed_output / "labels"
    #create dirs
    image_path.mkdir(parents=True,exist_ok=True)
    label_path.mkdir(parents=True,exist_ok=True)

if __name__ == "__main__":
    main_preprocess()