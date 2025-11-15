from utils import get_cfg
from eda import fanfo_data

def main():
    cfg = get_cfg()
    print(cfg.paths.processed_output)
    
    # fanfo_data(cfg)



if __name__ == "__main__":
    main()

    

    
    
    