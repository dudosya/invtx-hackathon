import pydantic

class PathsModel(pydantic.BaseModel):
    annotation_file: str
    pdf_folder: str

class AppModel(pydantic.BaseModel):
    paths: PathsModel