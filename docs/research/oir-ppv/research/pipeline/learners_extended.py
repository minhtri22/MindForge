"""Reference learners for EXP-LRN-001.

All implementations use the existing ``EncoderLearner`` contract and expose
their implementation fidelity in fit metadata. Adapted/surrogate learners are
never reported as canonical implementations.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

import numpy as np
import torch
from torch import nn
from torch.autograd import Function

from pipeline.learners import EncoderLearner, LearnerRegistry


torch.set_num_threads(1)


def _seed_everything(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass


def _as_float_matrix(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float32)
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    return array


def _domain_ids(context: np.ndarray | None, n: int) -> tuple[np.ndarray, int]:
    """Map frozen context rows to deterministic integer domain identifiers."""
    if context is None:
        return np.zeros(n, dtype=np.int64), 1
    context = np.asarray(context)
    if context.ndim == 1:
        context = context.reshape(-1, 1)
    if len(context) != n:
        raise ValueError("context length must match observations")
    _, inverse = np.unique(context.astype(str), axis=0, return_inverse=True)
    count = int(inverse.max() + 1) if len(inverse) else 1
    return inverse.astype(np.int64), count


class _TorchEncoderBase(EncoderLearner):
    fidelity = "adapted"

    def __init__(self, output_dim: int = 16, learning_rate: float = 0.01,
                 epochs: int = 8, seed: int = 42):
        self.output_dim = int(output_dim)
        self.learning_rate = float(learning_rate)
        self.epochs = int(epochs)
        self.seed = int(seed)
        self._fitted = False
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None

    def _prepare_fit(self, observations: np.ndarray) -> torch.Tensor:
        _seed_everything(self.seed)
        X = _as_float_matrix(observations)
        self._mean = X.mean(axis=0)
        self._std = X.std(axis=0) + 1e-6
        Xn = (X - self._mean) / self._std
        return torch.from_numpy(Xn.astype(np.float32))

    def _prepare_encode(self, observations: np.ndarray) -> torch.Tensor:
        if not self._fitted or self._mean is None or self._std is None:
            raise RuntimeError("Encoder not fitted")
        X = _as_float_matrix(observations)
        Xn = (X - self._mean) / self._std
        return torch.from_numpy(Xn.astype(np.float32))

    def get_output_dim(self) -> int:
        return self.output_dim

    @staticmethod
    def _config_hash(config: dict) -> str:
        return hashlib.sha256(
            json.dumps(config, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]


class MLPEncoderTrainable(_TorchEncoderBase):
    """Adapted supervised MLP representation baseline with prediction head."""

    fidelity = "adapted"

    def __init__(self, output_dim: int = 16, hidden_dims: List[int] | None = None,
                 learning_rate: float = 0.01, epochs: int = 8, seed: int = 42):
        super().__init__(output_dim, learning_rate, epochs, seed)
        self.hidden_dims = hidden_dims or [64]
        self.encoder: nn.Module | None = None
        self.classifier: nn.Module | None = None

    def fit(self, observations: np.ndarray, context: np.ndarray = None,
            labels: np.ndarray = None, nuisance: np.ndarray = None) -> Dict[str, Any]:
        if labels is None:
            raise ValueError("MLPEncoderTrainable requires labels")
        X = self._prepare_fit(observations)
        y_np = np.asarray(labels, dtype=np.int64)
        y = torch.from_numpy(y_np)
        n_classes = int(np.max(y_np)) + 1
        hidden = int(self.hidden_dims[0])
        self.encoder = nn.Sequential(
            nn.Linear(X.shape[1], hidden), nn.ReLU(),
            nn.Linear(hidden, self.output_dim),
        )
        self.classifier = nn.Linear(self.output_dim, n_classes)
        optimizer = torch.optim.Adam(
            list(self.encoder.parameters()) + list(self.classifier.parameters()),
            lr=self.learning_rate,
        )
        history = []
        for _ in range(self.epochs):
            optimizer.zero_grad()
            logits = self.classifier(self.encoder(X))
            loss = nn.functional.cross_entropy(logits, y)
            loss.backward()
            optimizer.step()
            history.append(float(loss.detach()))
        self._fitted = True
        return {
            "status": "fitted", "fidelity": self.fidelity,
            "method": "supervised MLP encoder + classification head",
            "objective": "cross_entropy", "epochs": self.epochs,
            "initial_loss": history[0], "final_loss": history[-1],
        }

    def encode(self, observations: np.ndarray) -> np.ndarray:
        assert self.encoder is not None
        with torch.no_grad():
            return self.encoder(self._prepare_encode(observations)).cpu().numpy()

    def get_config_hash(self) -> str:
        return self._config_hash({
            "type": type(self).__name__, "output_dim": self.output_dim,
            "hidden_dims": self.hidden_dims, "learning_rate": self.learning_rate,
            "epochs": self.epochs, "seed": self.seed,
        })


class VAEEncoder(_TorchEncoderBase):
    """Adapted VAE with reconstruction + KL and posterior-mean evaluation."""

    fidelity = "adapted"

    def __init__(self, output_dim: int = 16, hidden_dim: int = 64,
                 learning_rate: float = 0.005, epochs: int = 8,
                 beta: float = 1.0, seed: int = 42):
        super().__init__(output_dim, learning_rate, epochs, seed)
        self.hidden_dim = int(hidden_dim)
        self.beta = float(beta)
        self.encoder_body: nn.Module | None = None
        self.mu_head: nn.Module | None = None
        self.logvar_head: nn.Module | None = None
        self.decoder: nn.Module | None = None

    def fit(self, observations: np.ndarray, context: np.ndarray = None,
            labels: np.ndarray = None, nuisance: np.ndarray = None) -> Dict[str, Any]:
        X = self._prepare_fit(observations)
        self.encoder_body = nn.Sequential(nn.Linear(X.shape[1], self.hidden_dim), nn.Tanh())
        self.mu_head = nn.Linear(self.hidden_dim, self.output_dim)
        self.logvar_head = nn.Linear(self.hidden_dim, self.output_dim)
        self.decoder = nn.Sequential(
            nn.Linear(self.output_dim, self.hidden_dim), nn.Tanh(),
            nn.Linear(self.hidden_dim, X.shape[1]),
        )
        parameters = (
            list(self.encoder_body.parameters()) + list(self.mu_head.parameters()) +
            list(self.logvar_head.parameters()) + list(self.decoder.parameters())
        )
        optimizer = torch.optim.Adam(parameters, lr=self.learning_rate)
        history, recon_history, kl_history = [], [], []
        for _ in range(self.epochs):
            optimizer.zero_grad()
            h = self.encoder_body(X)
            mu = self.mu_head(h)
            logvar = torch.clamp(self.logvar_head(h), -8.0, 8.0)
            eps = torch.randn_like(mu)
            z = mu + torch.exp(0.5 * logvar) * eps
            reconstruction = self.decoder(z)
            recon = nn.functional.mse_loss(reconstruction, X)
            kl = -0.5 * torch.mean(1.0 + logvar - mu.pow(2) - logvar.exp())
            loss = recon + self.beta * kl
            loss.backward()
            optimizer.step()
            history.append(float(loss.detach()))
            recon_history.append(float(recon.detach()))
            kl_history.append(float(kl.detach()))
        self._fitted = True
        return {
            "status": "fitted", "fidelity": self.fidelity,
            "method": "VAE (reconstruction + KL; posterior mean evaluation)",
            "objective": "mse_reconstruction + beta*KL", "beta": self.beta,
            "epochs": self.epochs, "initial_loss": history[0],
            "final_loss": history[-1], "final_reconstruction": recon_history[-1],
            "final_kl": kl_history[-1],
        }

    def encode(self, observations: np.ndarray) -> np.ndarray:
        assert self.encoder_body is not None and self.mu_head is not None
        with torch.no_grad():
            h = self.encoder_body(self._prepare_encode(observations))
            return self.mu_head(h).cpu().numpy()

    def get_config_hash(self) -> str:
        return self._config_hash({
            "type": type(self).__name__, "output_dim": self.output_dim,
            "hidden_dim": self.hidden_dim, "learning_rate": self.learning_rate,
            "epochs": self.epochs, "beta": self.beta, "seed": self.seed,
        })


class IRMStyleEncoderSurrogate(_TorchEncoderBase):
    """IRM-style surrogate using cross-domain risk-variance regularization.

    This is deliberately not canonical IRM. Frozen context rows are consumed
    as explicit training-domain identifiers and task-risk variance is penalized
    across those domains.
    """

    fidelity = "surrogate"

    def __init__(self, output_dim: int = 16, hidden_dim: int = 64,
                 irm_penalty_weight: float = 1.0, learning_rate: float = 0.01,
                 epochs: int = 8, seed: int = 42):
        super().__init__(output_dim, learning_rate, epochs, seed)
        self.hidden_dim = int(hidden_dim)
        self.irm_penalty_weight = float(irm_penalty_weight)
        self.encoder: nn.Module | None = None
        self.classifier: nn.Module | None = None

    def fit(self, observations: np.ndarray, context: np.ndarray = None,
            labels: np.ndarray = None, nuisance: np.ndarray = None) -> Dict[str, Any]:
        if labels is None:
            raise ValueError("IRMStyleEncoderSurrogate requires labels")
        X = self._prepare_fit(observations)
        y_np = np.asarray(labels, dtype=np.int64)
        y = torch.from_numpy(y_np)
        domains_np, n_domains = _domain_ids(context, len(X))
        domains = torch.from_numpy(domains_np)
        n_classes = int(np.max(y_np)) + 1
        self.encoder = nn.Sequential(
            nn.Linear(X.shape[1], self.hidden_dim), nn.ReLU(),
            nn.Linear(self.hidden_dim, self.output_dim),
        )
        self.classifier = nn.Linear(self.output_dim, n_classes)
        optimizer = torch.optim.Adam(
            list(self.encoder.parameters()) + list(self.classifier.parameters()),
            lr=self.learning_rate,
        )
        history = []
        for _ in range(self.epochs):
            optimizer.zero_grad()
            logits = self.classifier(self.encoder(X))
            risks = []
            for domain in range(n_domains):
                mask = domains == domain
                if bool(mask.any()):
                    risks.append(nn.functional.cross_entropy(logits[mask], y[mask]))
            risk_stack = torch.stack(risks)
            mean_risk = risk_stack.mean()
            penalty = risk_stack.var(unbiased=False) if len(risks) > 1 else mean_risk * 0.0
            loss = mean_risk + self.irm_penalty_weight * penalty
            loss.backward()
            optimizer.step()
            history.append(float(loss.detach()))
        self._fitted = True
        return {
            "status": "fitted", "fidelity": self.fidelity,
            "method": "IRM-style surrogate (cross-domain risk variance penalty)",
            "canonical_irm": False, "domain_source": "frozen context rows",
            "domain_count": n_domains, "domain_signal_available": n_domains > 1,
            "irm_penalty_weight": self.irm_penalty_weight,
            "epochs": self.epochs, "initial_loss": history[0], "final_loss": history[-1],
        }

    def encode(self, observations: np.ndarray) -> np.ndarray:
        assert self.encoder is not None
        with torch.no_grad():
            return self.encoder(self._prepare_encode(observations)).cpu().numpy()

    def get_config_hash(self) -> str:
        return self._config_hash({
            "type": type(self).__name__, "output_dim": self.output_dim,
            "hidden_dim": self.hidden_dim, "irm_penalty_weight": self.irm_penalty_weight,
            "learning_rate": self.learning_rate, "epochs": self.epochs, "seed": self.seed,
        })


class _GradientReverse(Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor, strength: float):
        ctx.strength = strength
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor):
        return -ctx.strength * grad_output, None


class DANNSurrogateEncoder(_TorchEncoderBase):
    """Adapted DANN with task head, domain head, and gradient reversal."""

    fidelity = "adapted"

    def __init__(self, output_dim: int = 16, hidden_dim: int = 64,
                 domain_penalty_weight: float = 0.5, learning_rate: float = 0.01,
                 epochs: int = 8, seed: int = 42):
        super().__init__(output_dim, learning_rate, epochs, seed)
        self.hidden_dim = int(hidden_dim)
        self.domain_penalty_weight = float(domain_penalty_weight)
        self.encoder: nn.Module | None = None
        self.task_head: nn.Module | None = None
        self.domain_head: nn.Module | None = None

    def fit(self, observations: np.ndarray, context: np.ndarray = None,
            labels: np.ndarray = None, nuisance: np.ndarray = None) -> Dict[str, Any]:
        if labels is None:
            raise ValueError("DANNSurrogateEncoder requires task labels")
        X = self._prepare_fit(observations)
        y_np = np.asarray(labels, dtype=np.int64)
        y = torch.from_numpy(y_np)
        domains_np, n_domains = _domain_ids(context, len(X))
        domains = torch.from_numpy(domains_np)
        n_classes = int(np.max(y_np)) + 1
        self.encoder = nn.Sequential(
            nn.Linear(X.shape[1], self.hidden_dim), nn.ReLU(),
            nn.Linear(self.hidden_dim, self.output_dim),
        )
        self.task_head = nn.Linear(self.output_dim, n_classes)
        domain_hidden = max(8, self.output_dim // 2)
        self.domain_head = nn.Sequential(
            nn.Linear(self.output_dim, domain_hidden), nn.ReLU(),
            nn.Linear(domain_hidden, n_domains),
        )
        optimizer = torch.optim.Adam(
            list(self.encoder.parameters()) + list(self.task_head.parameters()) +
            list(self.domain_head.parameters()), lr=self.learning_rate,
        )
        history = []
        for _ in range(self.epochs):
            optimizer.zero_grad()
            z = self.encoder(X)
            task_loss = nn.functional.cross_entropy(self.task_head(z), y)
            reversed_z = _GradientReverse.apply(z, self.domain_penalty_weight)
            domain_loss = nn.functional.cross_entropy(self.domain_head(reversed_z), domains)
            loss = task_loss + domain_loss
            loss.backward()
            optimizer.step()
            history.append(float(loss.detach()))
        self._fitted = True
        return {
            "status": "fitted", "fidelity": self.fidelity,
            "method": "DANN adaptation (task head + domain head + gradient reversal)",
            "domain_source": "frozen context rows", "domain_count": n_domains,
            "domain_signal_available": n_domains > 1,
            "domain_penalty_weight": self.domain_penalty_weight,
            "epochs": self.epochs, "initial_loss": history[0], "final_loss": history[-1],
        }

    def encode(self, observations: np.ndarray) -> np.ndarray:
        assert self.encoder is not None
        with torch.no_grad():
            return self.encoder(self._prepare_encode(observations)).cpu().numpy()

    def get_config_hash(self) -> str:
        return self._config_hash({
            "type": type(self).__name__, "output_dim": self.output_dim,
            "hidden_dim": self.hidden_dim, "domain_penalty_weight": self.domain_penalty_weight,
            "learning_rate": self.learning_rate, "epochs": self.epochs, "seed": self.seed,
        })


LearnerRegistry.register_encoder("MLPTrainable")(MLPEncoderTrainable)
LearnerRegistry.register_encoder("VAE")(VAEEncoder)
LearnerRegistry.register_encoder("IRMStyle")(IRMStyleEncoderSurrogate)
LearnerRegistry.register_encoder("DANN")(DANNSurrogateEncoder)
