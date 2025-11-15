import pydantic
import json
from typing import List, Dict

class BboxModel(pydantic.BaseModel):
    x: float
    y: float
    width: float
    height: float

class AnnotationDetailModel(pydantic.BaseModel):
    category: str
    bbox: BboxModel
    area: float
class PageSizeModel(pydantic.BaseModel):
    width: int
    height: int
class PageModel(pydantic.BaseModel):
    annotations: List[AnnotationDetailModel]
    page_size: PageSizeModel

    @pydantic.validator('annotations', pre=True)
    def unwrap_annotations(cls, v):
        """
        Takes the raw list like [{"annotation_117": {...}}]
        and transforms it into a clean list of [{...}].
        """
        # For each item in the list, take the first (and only) value from the dictionary.
        return [list(item.values())[0] for item in v]

AnnotationsFileModel = Dict[str, Dict[str, PageModel]]
