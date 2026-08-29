import os
from pathlib import Path
from typing import List, Optional

class MockBlob:
    def __init__(self, name: str, bucket_path: Path):
        self.name = name
        self.path = bucket_path / name

    def upload_from_string(self, data: str, content_type: str = "text/plain"):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(data, encoding="utf-8")

    def upload_from_filename(self, filename: str):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = Path(filename).read_text(encoding="utf-8")
        self.path.write_text(content, encoding="utf-8")

    def download_as_text(self) -> str:
        if self.path.exists():
            return self.path.read_text(encoding="utf-8")
        return ""

    def download_to_filename(self, filename: str):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        Path(filename).write_text(self.download_as_text(), encoding="utf-8")

    def exists(self) -> bool:
        return self.path.exists()

class MockBucket:
    def __init__(self, name: str, root_dir: Path):
        self.name = name
        self.bucket_path = root_dir / name
        self.bucket_path.mkdir(parents=True, exist_ok=True)

    def blob(self, blob_name: str) -> MockBlob:
        return MockBlob(blob_name, self.bucket_path)

    def list_blobs(self, prefix: Optional[str] = None) -> List[MockBlob]:
        blobs = []
        for file_path in self.bucket_path.rglob("*"):
            if file_path.is_file():
                rel_name = str(file_path.relative_to(self.bucket_path)).replace("\\", "/")
                if not prefix or rel_name.startswith(prefix):
                    blobs.append(MockBlob(rel_name, self.bucket_path))
        return blobs

class MockStorageClient:
    """Mock GCS client for local zero-credential execution."""
    def __init__(self, storage_dir: Optional[Path] = None):
        self.root_dir = storage_dir or (Path.cwd() / "data" / "mock_gcs")
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def bucket(self, bucket_name: str) -> MockBucket:
        return MockBucket(bucket_name, self.root_dir)

    def get_bucket(self, bucket_name: str) -> MockBucket:
        return self.bucket(bucket_name)

    def create_bucket(self, bucket_name: str) -> MockBucket:
        return self.bucket(bucket_name)
