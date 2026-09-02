"""The single MindForge byte-level BPE tokenizer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

from tokenizers import Tokenizer, decoders, normalizers, pre_tokenizers
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer


SPECIAL_TOKENS = ("<|endoftext|>", "<|unk|>")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def train_tokenizer(inputs: Iterable[str | Path], output: str | Path, vocab_size: int = 16_384) -> Tokenizer:
    paths = [Path(path) for path in inputs]
    if not paths or any(not path.is_file() for path in paths):
        raise FileNotFoundError("all tokenizer input files must exist")
    if vocab_size < len(pre_tokenizers.ByteLevel.alphabet()) + len(SPECIAL_TOKENS):
        raise ValueError("vocab_size is too small for byte-level coverage")
    tokenizer = Tokenizer(BPE(unk_token=SPECIAL_TOKENS[1]))
    tokenizer.normalizer = normalizers.NFC()
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=1,
        special_tokens=list(SPECIAL_TOKENS),
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=False,
    )
    tokenizer.train([str(path) for path in paths], trainer)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(destination))
    return tokenizer


def load_tokenizer(path: str | Path) -> Tokenizer:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"missing tokenizer: {source}")
    tokenizer = Tokenizer.from_file(str(source))
    config = json.loads(tokenizer.to_str())
    if config.get("model", {}).get("type") != "BPE":
        raise ValueError("tokenizer must use BPE")
    if config.get("normalizer", {}).get("type") != "NFC":
        raise ValueError("tokenizer must use NFC normalization")
    for token in SPECIAL_TOKENS:
        if tokenizer.token_to_id(token) is None:
            raise ValueError(f"tokenizer is missing special token {token}")
    return tokenizer


def encode(tokenizer: Tokenizer, text: str) -> list[int]:
    ids = tokenizer.encode(text).ids
    if ids and (min(ids) < 0 or max(ids) >= tokenizer.get_vocab_size()):
        raise ValueError("tokenizer produced an out-of-range ID")
    return ids


def decode(tokenizer: Tokenizer, ids: Iterable[int]) -> str:
    values = list(ids)
    if values and (min(values) < 0 or max(values) >= tokenizer.get_vocab_size()):
        raise ValueError("token ID is outside tokenizer vocabulary")
    return tokenizer.decode(values, skip_special_tokens=False)


def metadata(path: str | Path, tokenizer: Tokenizer | None = None) -> dict[str, object]:
    tokenizer = tokenizer or load_tokenizer(path)
    config = json.loads(tokenizer.to_str())
    return {
        "sha256": sha256_file(path),
        "vocab_size": tokenizer.get_vocab_size(),
        "model": "BPE",
        "normalizer": config.get("normalizer"),
        "pre_tokenizer": config.get("pre_tokenizer"),
        "decoder": config.get("decoder"),
        "special_tokens": list(SPECIAL_TOKENS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MindForge tokenizer")
    sub = parser.add_subparsers(dest="command", required=True)
    train = sub.add_parser("train")
    train.add_argument("--input", action="append", required=True)
    train.add_argument("--output", required=True)
    train.add_argument("--vocab-size", type=int, default=16_384)
    args = parser.parse_args()
    tokenizer = train_tokenizer(args.input, args.output, args.vocab_size)
    print(json.dumps(metadata(args.output, tokenizer), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
