"""Standalone tokenizer inspector for M5.1.

Runs inside the exact pinned llama.cpp converter environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from typing import Any


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def _hash(value: Any) -> str:
    payload = json.dumps(_jsonable(value), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True)
    args = parser.parse_args()

    result: dict[str, Any] = {"model_dir": args.model_dir}
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            args.model_dir,
            local_files_only=True,
            trust_remote_code=False,
        )
        result["load_ok"] = True
        result["tokenizer_class"] = tokenizer.__class__.__name__

        try:
            vocab = tokenizer.vocab
            result["vocab_access_ok"] = True
            result["tokenizer_vocab_type"] = type(vocab).__name__
            result["tokenizer_vocab_size"] = len(vocab)
            result["tokenizer_vocab_hash"] = _hash(vocab)
            if isinstance(vocab, Mapping):
                result["vocab_mapping_keys"] = True
                result["vocab_max_id"] = max(vocab.values()) if vocab else None
            else:
                result["vocab_mapping_keys"] = False
        except Exception as error:
            result["vocab_access_ok"] = False
            result["vocab_error_type"] = type(error).__name__
            result["vocab_error"] = str(error)

        special_map = getattr(tokenizer, "special_tokens_map", None)
        result["special_tokens_map"] = _jsonable(special_map)
        result["special_tokens_map_hash"] = _hash(special_map)

        chat_template = getattr(tokenizer, "chat_template", None)
        result["chat_template_type"] = type(chat_template).__name__
        result["chat_template_hash"] = _hash(chat_template)

        probe_text = "M5.1 tokenizer probe: café 17 + 25 = 42 🚀"
        token_ids = tokenizer.encode(probe_text, add_special_tokens=False)
        decoded = tokenizer.decode(token_ids, skip_special_tokens=False)
        result["encode_decode_probe"] = {
            "text_hash": hashlib.sha256(probe_text.encode("utf-8")).hexdigest(),
            "token_ids": token_ids,
            "token_ids_hash": _hash(token_ids),
            "decoded": decoded,
            "decoded_hash": hashlib.sha256(decoded.encode("utf-8")).hexdigest(),
            "roundtrip_equal": decoded == probe_text,
        }
    except Exception as error:
        result["load_ok"] = False
        result["load_error_type"] = type(error).__name__
        result["load_error"] = str(error)

    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
