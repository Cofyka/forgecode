import os
from .code_persistence import CodePersistence

class ForgeCache(CodePersistence):
    CACHE_DIR = "__forgecache__"

    def __init__(self, base_dir: str = None):
        """
        Initializes the cache persistence.

        If no base_dir is provided, the default base directory is used.
        Cached files will be stored in a subdirectory (__forgecache__) inside base_dir.
        """
        if base_dir is None:
            base_dir = os.getcwd()
        self.base_dir = os.path.abspath(base_dir)

    def _get_cache_path(self, id: str, create: bool = False) -> str:
        """
        Returns the directory where the cache file should be stored.
        
        If `create` is True, ensures that the cache directory exists.
        """
        cache_dir = os.path.join(self.base_dir, self.CACHE_DIR)
        if create and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def save(self, id: str, code: str) -> None:
        """Saves the given code into a cache file inside __forgecache__."""
        cache_dir = self._get_cache_path(id, create=True)
        filename = f"{os.path.basename(id)}.py"
        cache_path = os.path.join(cache_dir, filename)

        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(code)

    def load(self, id: str) -> str | None:
        """Loads the cached code if available."""
        cache_dir = self._get_cache_path(id)
        filename = f"{os.path.basename(id)}.py"
        cache_path = os.path.join(cache_dir, filename)

        if not os.path.exists(cache_path):
            return None

        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()