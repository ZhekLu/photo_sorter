from pathlib import Path

from fastapi import APIRouter, HTTPException

from photo_sorter.api.schemas.folder import (
    FolderScanRequest,
    FolderScanResponse,
    FolderStatsResponse,
    PhotoResponse,
)
from photo_sorter.services.folder_scanner import FolderScanner

router = APIRouter(
    prefix="/folders",
    tags=["folders"],
)


@router.post("/scan")
def scan_folder(
    request: FolderScanRequest,
) -> FolderScanResponse:
    try:
        folder = FolderScanner.scan(Path(request.path))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Folder does not exist",
        )
    except NotADirectoryError:
        raise HTTPException(
            status_code=400,
            detail="Path is not a directory",
        )

    return FolderScanResponse(
        path=request.path,
        photo_count=folder.num_selected_files,
        photos=[
            PhotoResponse(
                path=photo.path.name,
                size_bytes=photo.size_bytes,
            )
            for photo in folder.photos
        ],
        stats=FolderStatsResponse(
            scanned=folder.num_scanned_files,
            selected=folder.num_selected_files,
            unsupported=folder.num_skipped_files,
            not_a_file=folder.num_skipped_objects,
        ),
    )
