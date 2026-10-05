from pydantic import BaseModel


class FolderScanRequest(BaseModel):
    path: str


class PhotoResponse(BaseModel):
    path: str
    size_bytes: int


class FolderStatsResponse(BaseModel):
    scanned: int
    selected: int
    unsupported: int
    not_a_file: int


class FolderScanResponse(BaseModel):
    path: str
    photo_count: int
    photos: list[PhotoResponse]
    stats: FolderStatsResponse
