import pydantic
from pathlib import Path
import yaml

class PathsModel(pydantic.BaseModel):
    annotation_file: Path
    pdf_folder: Path

    @pydantic.validator('annotation_file', 'pdf_folder', pre=True)
    def make_path_absolute(cls, v):
        return Path.cwd() / v

class AppModel(pydantic.BaseModel):
    paths: PathsModel