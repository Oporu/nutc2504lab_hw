def clean_tokens(text: str) -> str:
    return text.replace("<|im_start|>", "").replace("<|im_end|>", "")


__all__ = ["clean_tokens"]
