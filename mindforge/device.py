"""Direct device and dtype selection without backend abstractions."""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class DeviceSpec:
    device: torch.device
    dtype: torch.dtype

    @property
    def name(self) -> str:
        return self.device.type


def available(kind: str) -> bool:
    if kind == "cpu":
        return True
    if kind == "xpu":
        return bool(hasattr(torch, "xpu") and torch.xpu.is_available())
    if kind == "cuda":
        return torch.cuda.is_available()
    raise ValueError(f"unknown device: {kind}")


def resolve_device(requested: str = "auto", dtype: str = "auto") -> DeviceSpec:
    if requested == "auto":
        kind = next(item for item in ("xpu", "cuda", "cpu") if available(item))
    elif requested in {"xpu", "cuda", "cpu"}:
        if not available(requested):
            raise RuntimeError(f"requested device '{requested}' is not available")
        kind = requested
    else:
        raise ValueError("device must be auto, xpu, cuda, or cpu")

    if dtype == "auto":
        resolved_dtype = torch.float32 if kind == "cpu" else torch.bfloat16
    elif dtype == "float32":
        resolved_dtype = torch.float32
    elif dtype == "bfloat16":
        resolved_dtype = torch.bfloat16
    else:
        raise ValueError("dtype must be auto, float32, or bfloat16")
    return DeviceSpec(torch.device(kind), resolved_dtype)


def synchronize(device: torch.device | str) -> None:
    kind = torch.device(device).type
    if kind == "xpu":
        torch.xpu.synchronize()
    elif kind == "cuda":
        torch.cuda.synchronize()


def reset_peak_memory(device: torch.device | str) -> None:
    kind = torch.device(device).type
    if kind == "xpu" and hasattr(torch.xpu, "reset_peak_memory_stats"):
        torch.xpu.reset_peak_memory_stats()
    elif kind == "cuda":
        torch.cuda.reset_peak_memory_stats()


def peak_memory(device: torch.device | str) -> int | None:
    kind = torch.device(device).type
    if kind == "xpu" and hasattr(torch.xpu, "max_memory_allocated"):
        return int(torch.xpu.max_memory_allocated())
    if kind == "cuda":
        return int(torch.cuda.max_memory_allocated())
    return None
