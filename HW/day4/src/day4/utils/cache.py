from ..config import config
from ..logger import logger

import json
import aiofiles
import aiopath


async def load_cache() -> dict[str, str]:
    cache_file_path: str = config.cache_file_path
    if not await aiopath.AsyncPath(cache_file_path).exists():
        default_data = {"嗨": "嗨", "快取": "快取了"}
        logger.info("using default cache!")
        await save_cache(default_data)
        return default_data

    async with aiofiles.open(cache_file_path, "r", encoding="utf-8") as f:
        return json.loads(await f.read())


async def save_cache(cache: dict[str, str]) -> None:
    cache_file_path: str = config.cache_file_path
    logger.info("saving cache...")

    async with aiofiles.open(cache_file_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(cache, ensure_ascii=False))

    logger.info("cache saved")


__all__ = ["load_cache", "save_cache"]
