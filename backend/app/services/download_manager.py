from __future__ import annotations

from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import HfHubHTTPError

from app.services.events import EventBus


class DownloadManager:
    def __init__(self, cache_dir: Path, event_bus: EventBus):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.api = HfApi()
        self.events = event_bus

    def set_cache_dir(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def repo_files_with_sizes(self, repo_id: str, token: str | None = None) -> list[dict]:
        info = self.api.model_info(repo_id=repo_id, token=token)
        files: list[dict] = []
        for sibling in info.siblings:
            size = sibling.size or 0
            files.append({"path": sibling.rfilename, "size": int(size)})
        return files

    def estimate_repo_size(
        self,
        repo_id: str,
        token: str | None = None,
        include_file: str | None = None,
    ) -> dict:
        files = self.repo_files_with_sizes(repo_id, token)
        if include_file:
            files = [f for f in files if f["path"] == include_file]
        total = sum(item["size"] for item in files)
        return {
            "repo_id": repo_id,
            "total_bytes": total,
            "total_gb": round(total / (1024**3), 3),
            "files": files,
        }

    def probe_repo(self, repo_id: str, token: str | None = None) -> dict:
        try:
            files = self.repo_files_with_sizes(repo_id=repo_id, token=token)
            total = sum(item["size"] for item in files)
            return {
                "available": True,
                "auth_required": False,
                "error": None,
                "total_bytes": total,
                "total_gb": round(total / (1024**3), 3),
                "files": files,
            }
        except HfHubHTTPError as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in (401, 403):
                return {
                    "available": False,
                    "auth_required": True,
                    "error": "HF token required or access not granted for this repository.",
                    "total_bytes": 0,
                    "total_gb": 0,
                    "files": [],
                }
            return {
                "available": False,
                "auth_required": False,
                "error": f"HF error ({status}): {exc}",
                "total_bytes": 0,
                "total_gb": 0,
                "files": [],
            }

    async def download_variant(
        self,
        repo_id: str,
        include_file: str | None,
        token: str | None,
    ) -> dict:
        files = self.repo_files_with_sizes(repo_id, token)
        if include_file:
            files = [f for f in files if f["path"] == include_file]
        if not files:
            raise ValueError("No files selected for download")

        out_files: list[dict] = []
        for index, item in enumerate(files, start=1):
            await self.events.publish(
                {
                    "type": "download_progress",
                    "repo_id": repo_id,
                    "file": item["path"],
                    "status": "starting",
                    "index": index,
                    "total_files": len(files),
                    "file_bytes": item["size"],
                }
            )
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=item["path"],
                token=token,
                local_dir=self.cache_dir / repo_id.replace("/", "__"),
                local_dir_use_symlinks=False,
            )
            out_files.append({"path": item["path"], "size": Path(local_path).stat().st_size})
            await self.events.publish(
                {
                    "type": "download_progress",
                    "repo_id": repo_id,
                    "file": item["path"],
                    "status": "completed",
                    "index": index,
                    "total_files": len(files),
                    "file_bytes": item["size"],
                }
            )

        total = sum(i["size"] for i in out_files)
        await self.events.publish(
            {
                "type": "download_complete",
                "repo_id": repo_id,
                "total_bytes": total,
                "total_gb": round(total / (1024**3), 3),
            }
        )
        return {"repo_id": repo_id, "files": out_files, "total_bytes": total}
