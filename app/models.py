from pydantic import BaseModel, Field
from typing import List

class Region(BaseModel):
    """
    Represents a rectangular region on the image.
    This mirrors the data structure used by the frontend JavaScript.
    """
    id: int = Field(..., description="Unique identifier for the box (e.g., index)")
    x: int = Field(..., ge=0, description="X coordinate of the top-left corner")
    y: int = Field(..., ge=0, description="Y coordinate of the top-left corner")
    w: int = Field(..., gt=0, description="Width of the box")
    h: int = Field(..., gt=0, description="Height of the box")

class FinalizeRequest(BaseModel):
    """
    The payload sent when the user clicks 'Download'.
    It contains the original image data and the list of confirmed regions to blur.
    """
    image_base64: str = Field(..., description="Base64 encoded string of the image")
    boxes: List[Region] = Field(..., description="List of regions to apply blur to")