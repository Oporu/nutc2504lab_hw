import aiofiles


async def text_from_file(file_path: str) -> str:
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        return await f.read()
