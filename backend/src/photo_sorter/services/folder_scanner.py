from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
}


@dataclass(frozen=True)
class ScannedPhoto:
    path: Path
    size_bytes: int


@dataclass(frozen=True)
class ScannedFolder:
    path: Path
    size_bytes: int
    num_scanned_files: int = field(
        doc="Number of scanned files (skipped_files + selected_files)"
    )
    num_selected_files: int = field(doc="Number of selected files (photos)")
    num_skipped_files: int = field(
        doc="Number of files skipped because they are not supported image formats"
    )
    num_skipped_objects: int = field(
        doc="Number of objects skipped because they are not files"
    )

    photos: list[ScannedPhoto]


class FolderScanner:
    @staticmethod
    def scan(folder: Path) -> ScannedFolder:
        """
        Flat scanner for a folder. It will scan only the files in the folder, not in subfolders.
        :param folder: folder to scan
        :return: ScannedFolder object with photos sorted by creation date (newest first)
        :raises NotADirectoryError: if folder is not a directory
        :raises FileNotFoundError: if folder does not exist

        :todo: Add support for scanning subfolders recursively (is_recursive=True)
        """
        if not folder.exists():
            raise FileNotFoundError(folder)

        if not folder.is_dir():
            raise NotADirectoryError(folder)

        photos: list[ScannedPhoto] = []
        total_files, skipped_objects = 0, 0
        for path in folder.iterdir():
            if not path.is_file():
                skipped_objects += 1
                continue

            total_files += 1
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            photos.append(ScannedPhoto(path=path, size_bytes=path.stat().st_size))

        return ScannedFolder(
            path=folder,
            size_bytes=folder.stat().st_size,
            num_scanned_files=total_files,
            num_selected_files=len(photos),
            num_skipped_files=total_files - len(photos),
            num_skipped_objects=skipped_objects,
            photos=sorted(
                photos, key=lambda photo: photo.path.stat().st_birthtime, reverse=True
            ),
        )
