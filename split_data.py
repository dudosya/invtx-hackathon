import pathlib
from pathlib import Path
import random
import math

#define necessary paths
processed_output = Path.cwd() / "output"
new_output_dir = Path.cwd() / "dataset"

# create the subdirs
(new_output_dir / "images/train").mkdir(parents=True,exist_ok=True)
(new_output_dir / "images/val").mkdir(parents=True,exist_ok=True)
(new_output_dir / "labels/train").mkdir(parents=True,exist_ok=True)
(new_output_dir / "labels/val").mkdir(parents=True,exist_ok=True)

#get list of img files from output
jpg_path_list = sorted((processed_output / "images").glob("*.jpg"))

# shuffle the list
random.shuffle(jpg_path_list)

# define split ratio
train_split = 0.8

# find index to split
index_to_split = math.floor(len(jpg_path_list) * train_split)

for index,jpg_path in enumerate(jpg_path_list):
    print(f"WE ARE WORKING ON {jpg_path.name}")
    
    label_path = processed_output / "labels" / f"{jpg_path.stem}.txt"
    
    # training set
    if index < index_to_split:
        print(f"{jpg_path.name} is going to the train split")
        img_destination_path = new_output_dir / "images" / "train" / jpg_path.name
        label_destination_path = new_output_dir / "labels" / "train" / label_path.name
    # val set
    else:
        print(f"{jpg_path.name} is going to the val split")
        img_destination_path = new_output_dir / "images" / "val" / jpg_path.name
        label_destination_path = new_output_dir / "labels" / "val" / label_path.name
        
    
    
    # move the img and paths
    jpg_path.rename(img_destination_path)
    label_path.rename(label_destination_path)


