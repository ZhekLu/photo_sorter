import time
from pathlib import Path

import pytest

from photo_sorter.services.folder_scanner import FolderScanner, ScannedPhoto


class TestFolderScannerBasicFunctionality:
    """Test basic scanning functionality"""

    def test_scan_returns_supported_images(self, tmp_path: Path) -> None:
        """Test that scanner correctly identifies supported image formats"""
        # Arrange
        (tmp_path / "photo.JPG").write_bytes(b"abc")
        (tmp_path / "image.png").write_bytes(b"12345")
        (tmp_path / "photo.jpeg").write_bytes(b"xyz")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        photo_names = {photo.path.name for photo in folder.photos}
        assert photo_names == {"photo.JPG", "image.png", "photo.jpeg"}
        assert folder.num_selected_files == 3

    def test_scan_filters_unsupported_formats(self, tmp_path: Path) -> None:
        """Test that non-image files are excluded from results"""
        # Arrange
        (tmp_path / "photo.jpg").write_bytes(b"abc")
        (tmp_path / "notes.txt").write_bytes(b"text")
        (tmp_path / "document.pdf").write_bytes(b"pdf")
        (tmp_path / "video.mp4").write_bytes(b"video")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_selected_files == 1
        assert folder.photos[0].path.name == "photo.jpg"
        assert folder.num_skipped_files == 3

    def test_scan_ignores_directories(self, tmp_path: Path) -> None:
        """Test that directories in the folder are skipped"""
        # Arrange
        (tmp_path / "photo.jpg").write_bytes(b"abc")
        (tmp_path / "subfolder").mkdir()
        (tmp_path / "subfolder" / "nested.jpg").write_bytes(b"xyz")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_selected_files == 1
        assert folder.photos[0].path.name == "photo.jpg"
        assert folder.num_skipped_objects == 1

    def test_scan_ignores_symlinks_and_special_files(self, tmp_path: Path) -> None:
        """Test that symlinks and non-file objects are skipped"""
        # Arrange
        (tmp_path / "photo.jpg").write_bytes(b"abc")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "link").symlink_to(subdir)

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_selected_files == 1
        assert folder.num_skipped_objects == 2  # directory + symlink

    def test_scan_returns_correct_file_sizes(self, tmp_path: Path) -> None:
        """Test that file sizes are correctly reported"""
        # Arrange
        (tmp_path / "small.jpg").write_bytes(b"small")
        (tmp_path / "medium.png").write_bytes(b"medium_file")
        (tmp_path / "large.jpeg").write_bytes(b"x" * 1000)

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        size_map = {photo.path.name: photo.size_bytes for photo in folder.photos}
        assert size_map["small.jpg"] == 5
        assert size_map["medium.png"] == 11
        assert size_map["large.jpeg"] == 1000

    def test_scan_returns_folder_size(self, tmp_path: Path) -> None:
        """Test that total folder size is reported"""
        # Arrange
        (tmp_path / "photo1.jpg").write_bytes(b"x" * 100)
        (tmp_path / "photo2.jpg").write_bytes(b"x" * 200)

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.size_bytes > 0


class TestFolderScannerPhotoSorting:
    """Test photo sorting functionality"""

    def test_scan_sorts_photos_by_creation_date_newest_first(
        self, tmp_path: Path
    ) -> None:
        """Test that photos are sorted by creation date (birthtime) in descending order"""
        # Arrange
        photo1 = tmp_path / "photo1.jpg"
        photo1.write_bytes(b"abc")
        time.sleep(0.1)

        photo2 = tmp_path / "photo2.jpg"
        photo2.write_bytes(b"def")
        time.sleep(0.1)

        photo3 = tmp_path / "photo3.jpg"
        photo3.write_bytes(b"ghi")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        photo_names = [photo.path.name for photo in folder.photos]
        assert photo_names == ["photo3.jpg", "photo2.jpg", "photo1.jpg"]

    def test_scan_handles_single_photo(self, tmp_path: Path) -> None:
        """Test scanning with a single photo"""
        # Arrange
        (tmp_path / "only.jpg").write_bytes(b"single")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert len(folder.photos) == 1
        assert folder.photos[0].path.name == "only.jpg"


class TestFolderScannerStatistics:
    """Test statistics and counting functionality"""

    def test_scan_counts_correctly(self, tmp_path: Path) -> None:
        """Test that all counts are accurate"""
        # Arrange
        (tmp_path / "photo1.jpg").write_bytes(b"1")
        (tmp_path / "photo2.jpeg").write_bytes(b"2")
        (tmp_path / "image.png").write_bytes(b"3")
        (tmp_path / "document.pdf").write_bytes(b"4")
        (tmp_path / "notes.txt").write_bytes(b"5")
        (tmp_path / "subfolder").mkdir()

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_scanned_files == 5  # all files
        assert folder.num_selected_files == 3  # photos
        assert folder.num_skipped_files == 2  # non-image files
        assert folder.num_skipped_objects == 1  # directories

    def test_scan_with_empty_folder(self, tmp_path: Path) -> None:
        """Test scanning an empty folder"""
        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_scanned_files == 0
        assert folder.num_selected_files == 0
        assert folder.num_skipped_files == 0
        assert folder.num_skipped_objects == 0
        assert len(folder.photos) == 0

    def test_scan_with_only_unsupported_files(self, tmp_path: Path) -> None:
        """Test scanning folder with only unsupported files"""
        # Arrange
        (tmp_path / "file1.txt").write_bytes(b"text")
        (tmp_path / "file2.pdf").write_bytes(b"pdf")
        (tmp_path / "file3.doc").write_bytes(b"doc")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_scanned_files == 3
        assert folder.num_selected_files == 0
        assert folder.num_skipped_files == 3
        assert len(folder.photos) == 0

    def test_scan_with_only_directories(self, tmp_path: Path) -> None:
        """Test scanning folder with only directories"""
        # Arrange
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "dir3").mkdir()

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_scanned_files == 0
        assert folder.num_selected_files == 0
        assert folder.num_skipped_objects == 3
        assert len(folder.photos) == 0


class TestFolderScannerErrorHandling:
    """Test error handling and edge cases"""

    def test_scan_raises_file_not_found_error_for_nonexistent_folder(
        self,
    ) -> None:
        """Test that FileNotFoundError is raised for non-existent folders"""
        # Arrange
        nonexistent = Path("/nonexistent/folder/path")

        # Act & Assert
        scanner = FolderScanner()
        with pytest.raises(FileNotFoundError):
            scanner.scan(nonexistent)

    def test_scan_raises_not_a_directory_error_for_file(self, tmp_path: Path) -> None:
        """Test that NotADirectoryError is raised when path is a file"""
        # Arrange
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        # Act & Assert
        scanner = FolderScanner()
        with pytest.raises(NotADirectoryError):
            scanner.scan(file_path)

    def test_scan_handles_case_insensitive_extensions(self, tmp_path: Path) -> None:
        """Test that file extensions are matched case-insensitively"""
        # Arrange
        (tmp_path / "photo.JPG").write_bytes(b"1")
        (tmp_path / "image.Png").write_bytes(b"2")
        (tmp_path / "photo.JpEg").write_bytes(b"3")
        (tmp_path / "picture.JPEG").write_bytes(b"4")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.num_selected_files == 4
        assert len(folder.photos) == 4


class TestFolderScannerDataStructures:
    """Test data structure integrity"""

    def test_scanned_folder_contains_correct_path(self, tmp_path: Path) -> None:
        """Test that ScannedFolder contains the correct path"""
        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert folder.path == tmp_path

    def test_scanned_photos_are_scanned_photo_instances(self, tmp_path: Path) -> None:
        """Test that photos in the result are ScannedPhoto instances"""
        # Arrange
        (tmp_path / "photo.jpg").write_bytes(b"data")

        # Act
        scanner = FolderScanner()
        folder = scanner.scan(tmp_path)

        # Assert
        assert len(folder.photos) == 1
        assert isinstance(folder.photos[0], ScannedPhoto)
        assert hasattr(folder.photos[0], "path")
        assert hasattr(folder.photos[0], "size_bytes")

    def test_scanner_is_stateless(self, tmp_path: Path) -> None:
        """Test that FolderScanner can be reused for multiple scans"""
        # Arrange
        folder1 = tmp_path / "folder1"
        folder1.mkdir()
        (folder1 / "photo1.jpg").write_bytes(b"1")

        folder2 = tmp_path / "folder2"
        folder2.mkdir()
        (folder2 / "photo2.jpg").write_bytes(b"2")
        (folder2 / "photo3.jpg").write_bytes(b"3")

        # Act
        scanner = FolderScanner()
        result1 = scanner.scan(folder1)
        result2 = scanner.scan(folder2)

        # Assert
        assert len(result1.photos) == 1
        assert len(result2.photos) == 2
        assert result1.path == folder1
        assert result2.path == folder2
