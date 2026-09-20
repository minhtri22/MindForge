"""M1 qualification tokenizer, packing, deterministic sampling and ResumeCursor simulation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable

from .canonical import sha256_object
from .data_policy import ProcessedDocument
from .errors import DataIntegrityError
from .models import PhaseSpec


@dataclass(frozen=True)
class PackedSequence:
    sequence_id: str
    phase_id: str
    token_count: int
    token_hash: str
    document_ids: tuple[str, ...]

    def descriptor(self) -> dict[str, Any]:
        return {
            "sequence_id": self.sequence_id,
            "phase_id": self.phase_id,
            "token_count": self.token_count,
            "token_hash": self.token_hash,
            "document_ids": list(self.document_ids),
        }


@dataclass(frozen=True)
class ResumeCursor:
    resume_fidelity: str
    dataset_or_shard_id: str
    document_index: int
    token_offset: int
    packed_sequence_index: int
    consumed_tokens: int
    sampler_cycle: int
    shuffle_state: dict[str, Any]
    worker_states: tuple[dict[str, Any], ...]
    mixture_state: dict[str, Any]
    gradient_accumulation_micro_step: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "resume_fidelity": self.resume_fidelity,
            "dataset_or_shard_id": self.dataset_or_shard_id,
            "document_index": self.document_index,
            "token_offset": self.token_offset,
            "packed_sequence_index": self.packed_sequence_index,
            "consumed_tokens": self.consumed_tokens,
            "sampler_cycle": self.sampler_cycle,
            "shuffle_state": self.shuffle_state,
            "worker_states": list(self.worker_states),
            "mixture_state": self.mixture_state,
            "gradient_accumulation_micro_step": self.gradient_accumulation_micro_step,
        }


class QualificationByteTokenizer:
    """Deterministic M1-only tokenizer.

    It deliberately does not pretend to be the model tokenizer. Its only job is
    to prove phase-scoped tokenize/pack/sampler/resume mechanics before M2 is
    allowed to load model assets.
    """

    BOS = 256
    EOS = 257
    PAD = 258

    @property
    def identity(self) -> dict[str, Any]:
        return {
            "id": "m1-utf8-byte-tokenizer",
            "version": "1",
            "vocab": "utf8-bytes+bos/eos/pad",
            "bos_id": self.BOS,
            "eos_id": self.EOS,
            "pad_id": self.PAD,
            "qualification_only": True,
        }

    @property
    def sha256(self) -> str:
        return sha256_object(self.identity)

    def encode(self, value: str) -> list[int]:
        return list(value.encode("utf-8"))


class XorShift64:
    def __init__(self, state: int):
        state &= (1 << 64) - 1
        self.state = state or 0x9E3779B97F4A7C15

    def next_u64(self) -> int:
        x = self.state
        x ^= (x << 13) & ((1 << 64) - 1)
        x ^= x >> 7
        x ^= (x << 17) & ((1 << 64) - 1)
        self.state = x & ((1 << 64) - 1)
        return self.state

    def randbelow(self, n: int) -> int:
        if n <= 0:
            raise ValueError("n must be positive")
        return self.next_u64() % n


class BufferedSampler:
    def __init__(
        self,
        item_count: int,
        seed: int,
        buffer_size: int,
        mode: str,
        *,
        state: dict[str, Any] | None = None,
    ):
        if item_count <= 0:
            raise DataIntegrityError("sampler requires at least one item")
        self.item_count = item_count
        self.mode = mode
        self.limit = item_count
        if state is None:
            self.rng = XorShift64(seed)
            self.input_index = 0
            self.emitted = 0
            self.buffer: list[int] = []
            if mode == "without_replacement":
                while self.input_index < item_count and len(self.buffer) < max(1, buffer_size):
                    self.buffer.append(self.input_index)
                    self.input_index += 1
            elif mode != "with_replacement":
                raise DataIntegrityError(f"unsupported sampling mode {mode}")
        else:
            self.rng = XorShift64(int(state["rng_state"]))
            self.input_index = int(state["input_index"])
            self.emitted = int(state["emitted"])
            self.buffer = [int(value) for value in state["buffer"]]
            self.limit = int(state["limit"])

    def __iter__(self) -> "BufferedSampler":
        return self

    def __next__(self) -> int:
        if self.emitted >= self.limit:
            raise StopIteration
        if self.mode == "with_replacement":
            index = self.rng.randbelow(self.item_count)
            self.emitted += 1
            return index
        if not self.buffer:
            raise StopIteration
        position = self.rng.randbelow(len(self.buffer))
        index = self.buffer[position]
        if self.input_index < self.item_count:
            self.buffer[position] = self.input_index
            self.input_index += 1
        else:
            self.buffer.pop(position)
        self.emitted += 1
        return index

    def state_dict(self) -> dict[str, Any]:
        return {
            "algorithm": "xorshift64-buffered-v1",
            "mode": self.mode,
            "rng_state": self.rng.state,
            "input_index": self.input_index,
            "emitted": self.emitted,
            "buffer": list(self.buffer),
            "limit": self.limit,
        }


def build_phase_stream(
    phase: PhaseSpec,
    documents: Iterable[ProcessedDocument],
    tokenizer: QualificationByteTokenizer | None = None,
) -> tuple[list[PackedSequence], dict[str, Any]]:
    tokenizer = tokenizer or QualificationByteTokenizer()
    selected = [
        document
        for document in documents
        if document.dataset_id in phase.datasets and document.split == "train"
    ]
    selected.sort(key=lambda item: item.identity)
    if not selected:
        raise DataIntegrityError(f"phase {phase.id}: no train documents after M1 policy/split")

    packed = _pack_documents(phase, selected, tokenizer)
    if not packed:
        raise DataIntegrityError(f"phase {phase.id}: packing produced zero sequences")

    sampling = phase.token_stream.sampling
    sampler = BufferedSampler(
        len(packed),
        int(sampling["seed"]),
        int(sampling["shuffle_buffer_size"]),
        str(sampling["mode"]),
    )
    order = list(iter(sampler))
    ordered = [packed[index] for index in order]
    stream_hash = sha256_object([sequence.descriptor() for sequence in ordered])
    contract = {
        "phase_id": phase.id,
        "tokenizer_hash": tokenizer.sha256,
        "sequence_length": phase.token_stream.sequence_length,
        "packing": dict(phase.token_stream.packing),
        "sampling": {
            **dict(sampling),
            "resolved_algorithm": "xorshift64-buffered-v1",
        },
        "stream_hash": stream_hash,
    }
    return ordered, contract


def simulate_resume(
    phase: PhaseSpec,
    ordered: list[PackedSequence],
) -> dict[str, Any]:
    if not ordered:
        raise DataIntegrityError(f"phase {phase.id}: cannot simulate resume on empty stream")
    sampling = phase.token_stream.sampling
    # Rebuild the natural packed list index space from the already materialized order
    # by using sequence descriptors as the items to replay. The simulation validates
    # sampler-state restoration itself, not re-packing.
    item_count = len(ordered)
    sampler = BufferedSampler(
        item_count,
        int(sampling["seed"]),
        int(sampling["shuffle_buffer_size"]),
        str(sampling["mode"]),
    )
    cut = max(1, item_count // 2)
    prefix_indices: list[int] = []
    for _ in range(cut):
        prefix_indices.append(next(sampler))
    state = sampler.state_dict()
    suffix_direct = list(sampler)
    restored = BufferedSampler(
        item_count,
        int(sampling["seed"]),
        int(sampling["shuffle_buffer_size"]),
        str(sampling["mode"]),
        state=state,
    )
    suffix_resumed = list(restored)
    consumed_tokens = sum(ordered[index].token_count for index in prefix_indices if index < len(ordered))
    cursor = ResumeCursor(
        resume_fidelity="exact",
        dataset_or_shard_id="+".join(phase.datasets),
        document_index=state["input_index"],
        token_offset=0,
        packed_sequence_index=state["emitted"],
        consumed_tokens=consumed_tokens,
        sampler_cycle=0,
        shuffle_state=state,
        worker_states=tuple({"worker_id": worker, "logical_state": "deterministic"} for worker in range(phase.token_stream.workers)),
        mixture_state={"datasets": list(phase.datasets), "policy": "phase_declared_order_v1"},
        gradient_accumulation_micro_step=0,
    )
    return {
        "phase_id": phase.id,
        "cut": cut,
        "suffix_match": suffix_direct == suffix_resumed,
        "direct_suffix_hash": sha256_object(suffix_direct),
        "resumed_suffix_hash": sha256_object(suffix_resumed),
        "cursor": cursor.to_dict(),
        "cursor_hash": sha256_object(cursor.to_dict()),
    }


def _pack_documents(
    phase: PhaseSpec,
    documents: list[ProcessedDocument],
    tokenizer: QualificationByteTokenizer,
) -> list[PackedSequence]:
    length = phase.token_stream.sequence_length
    packing = phase.token_stream.packing
    cross_document = bool(packing["cross_document"])
    remainder_policy = str(packing["remainder_policy"])

    encoded: list[tuple[str, list[int]]] = []
    for document in documents:
        tokens = tokenizer.encode(document.content)
        if phase.token_stream.add_bos:
            tokens = [tokenizer.BOS, *tokens]
        if phase.token_stream.add_eos:
            tokens = [*tokens, tokenizer.EOS]
        encoded.append((document.identity, tokens))

    chunks: list[tuple[list[int], tuple[str, ...]]] = []
    if cross_document:
        token_pairs: list[tuple[int, str]] = []
        for document_id, tokens in encoded:
            token_pairs.extend((token, document_id) for token in tokens)
        cursor = 0
        while cursor < len(token_pairs):
            part = token_pairs[cursor : cursor + length]
            cursor += length
            if len(part) < length:
                if remainder_policy == "drop":
                    break
                if remainder_policy == "pad":
                    padded = [token for token, _ in part] + [tokenizer.PAD] * (length - len(part))
                    ids = tuple(dict.fromkeys(document_id for _, document_id in part))
                    chunks.append((padded, ids))
                    break
            tokens = [token for token, _ in part]
            ids = tuple(dict.fromkeys(document_id for _, document_id in part))
            chunks.append((tokens, ids))
    else:
        for document_id, tokens in encoded:
            cursor = 0
            while cursor < len(tokens):
                part = tokens[cursor : cursor + length]
                cursor += length
                if len(part) < length:
                    if remainder_policy == "drop":
                        break
                    if remainder_policy == "pad":
                        part = [*part, *([tokenizer.PAD] * (length - len(part)))]
                chunks.append((part, (document_id,)))

    result: list[PackedSequence] = []
    for index, (tokens, document_ids) in enumerate(chunks):
        token_bytes = b"".join(int(token).to_bytes(2, "big") for token in tokens)
        token_hash = hashlib.sha256(token_bytes).hexdigest()
        sequence_id = hashlib.sha256(
            f"{phase.id}\0{index}\0{token_hash}".encode("utf-8")
        ).hexdigest()
        result.append(
            PackedSequence(
                sequence_id=sequence_id,
                phase_id=phase.id,
                token_count=len(tokens),
                token_hash=token_hash,
                document_ids=document_ids,
            )
        )
    return result
