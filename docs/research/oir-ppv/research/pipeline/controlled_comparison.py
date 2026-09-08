"""Controlled trained, untrained, and placeholder learner comparison."""

import argparse
import json
from pathlib import Path
import sys
from typing import Dict, Tuple

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).parent.parent))

from environments import EnvironmentRegistry
from pipeline.learners import AutoencoderEncoder, MLPDecoder


def _context_tables(train: np.ndarray, test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    categories = [str(value) for value in np.unique(train)]
    mapping = {value: index for index, value in enumerate(categories)}

    def encode(values: np.ndarray) -> np.ndarray:
        table = np.zeros((len(values), len(categories)), dtype=float)
        for row, value in enumerate(values):
            index = mapping.get(str(value))
            if index is not None:
                table[row, index] = 1.0
        return table

    return encode(train), encode(test)


def _predictive_accuracy(
    train_i: np.ndarray, train_y: np.ndarray, test_i: np.ndarray, test_y: np.ndarray,
    seed: int
) -> float:
    model = LogisticRegression(max_iter=1000, random_state=seed)
    model.fit(train_i, train_y)
    return float(model.score(test_i, test_y))


def _mse(generated: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean((generated - target) ** 2))


def _random_forward(
    train_obs: np.ndarray, test_obs: np.ndarray, train_context: np.ndarray,
    test_context: np.ndarray, train_nuisance: np.ndarray,
    test_nuisance: np.ndarray, latent_dim: int, seed: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluation-only initialized forward pass; no fitted production API is used."""
    rng = np.random.default_rng(seed)
    mean = train_obs.mean(axis=0)
    std = train_obs.std(axis=0) + 1e-8
    weight = rng.normal(0.0, 1.0 / np.sqrt(train_obs.shape[1]),
                        size=(train_obs.shape[1], latent_dim))
    train_i = np.tanh(((train_obs - mean) / std) @ weight)
    test_i = np.tanh(((test_obs - mean) / std) @ weight)
    decoder_input_dim = latent_dim + train_context.shape[1] + train_nuisance.shape[1]
    decoder_weight = rng.normal(0.0, 1.0 / np.sqrt(decoder_input_dim),
                                size=(decoder_input_dim, train_obs.shape[1]))
    test_input = np.hstack([test_i, test_context, test_nuisance])
    generated = (test_input @ decoder_weight) * std + mean
    return train_i, test_i, generated


def run_comparison(
    output_dir: Path = Path("artifacts/stress_test"),
    max_train: int = 1000,
    max_test: int = 500,
    epochs: int = 25,
    seed: int = 42,
    tolerance: float = 1e-9,
) -> Dict:
    env = EnvironmentRegistry.create_from_config_path(
        "environments/env3_config.yaml", seed
    )
    data = env.generate()
    train_idx = np.asarray(data.splits["train"][:max_train], dtype=int)
    test_idx = np.asarray(data.splits["test"][:max_test], dtype=int)
    train_obs = data.observations[train_idx].astype(float)
    test_obs = data.observations[test_idx].astype(float)
    train_labels = data.labels[train_idx]
    test_labels = data.labels[test_idx]
    train_context, test_context = _context_tables(
        data.metadata["Z"][train_idx], data.metadata["Z"][test_idx]
    )
    train_nuisance = data.metadata["N"][train_idx].reshape(-1, 1).astype(float)
    test_nuisance = data.metadata["N"][test_idx].reshape(-1, 1).astype(float)
    latent_dim = min(8, train_obs.shape[1])

    placeholder_encoder = PCA(n_components=latent_dim, random_state=seed)
    placeholder_train_i = placeholder_encoder.fit_transform(train_obs)
    placeholder_test_i = placeholder_encoder.transform(test_obs)
    placeholder_rng = np.random.default_rng(seed)
    placeholder_generated = placeholder_rng.normal(
        train_obs.mean(axis=0), train_obs.std(axis=0) + 1e-8,
        size=test_obs.shape,
    )

    untrained_train_i, untrained_test_i, untrained_generated = _random_forward(
        train_obs, test_obs, train_context, test_context, train_nuisance,
        test_nuisance, latent_dim, seed
    )

    trained_encoder = AutoencoderEncoder(
        output_dim=latent_dim, hidden_dim=16, learning_rate=0.01,
        epochs=epochs, seed=seed
    )
    encoder_fit = trained_encoder.fit(train_obs, train_context, train_labels)
    trained_train_i = trained_encoder.encode(train_obs)
    trained_test_i = trained_encoder.encode(test_obs)
    trained_decoder = MLPDecoder(
        output_dim=train_obs.shape[1], hidden_dims=[16], learning_rate=0.01,
        epochs=epochs, seed=seed
    )
    decoder_fit = trained_decoder.fit(
        trained_train_i, train_context, train_nuisance, train_obs
    )
    trained_generated = trained_decoder.decode(
        trained_test_i, test_context, test_nuisance
    )

    metrics = {
        "placeholder": {
            "definition": "PCA representation plus seeded random manifestation generator",
            "reconstruction_mse": _mse(placeholder_generated, test_obs),
            "predictive_accuracy": _predictive_accuracy(
                placeholder_train_i, train_labels, placeholder_test_i,
                test_labels, seed
            ),
        },
        "untrained": {
            "definition": "evaluation-only initialized random encoder and decoder forward pass",
            "reconstruction_mse": _mse(untrained_generated, test_obs),
            "predictive_accuracy": _predictive_accuracy(
                untrained_train_i, train_labels, untrained_test_i,
                test_labels, seed
            ),
        },
        "trained": {
            "definition": "AutoencoderEncoder and MLPDecoder fitted on the training split",
            "reconstruction_mse": _mse(trained_generated, test_obs),
            "predictive_accuracy": _predictive_accuracy(
                trained_train_i, train_labels, trained_test_i, test_labels, seed
            ),
            "encoder_initial_loss": encoder_fit["initial_loss"],
            "encoder_final_loss": encoder_fit["final_loss"],
            "decoder_initial_loss": decoder_fit["initial_loss"],
            "decoder_final_loss": decoder_fit["final_loss"],
        },
    }
    checks = {
        "encoder_loss_decreased": metrics["trained"]["encoder_final_loss"]
        < metrics["trained"]["encoder_initial_loss"] - tolerance,
        "decoder_loss_decreased": metrics["trained"]["decoder_final_loss"]
        < metrics["trained"]["decoder_initial_loss"] - tolerance,
        "trained_mse_below_untrained": metrics["trained"]["reconstruction_mse"]
        < metrics["untrained"]["reconstruction_mse"] - tolerance,
        "trained_mse_below_placeholder": metrics["trained"]["reconstruction_mse"]
        < metrics["placeholder"]["reconstruction_mse"] - tolerance,
    }
    comparison = {
        "protocol": "controlled_comparison_v1",
        "seed": seed,
        "tolerance": tolerance,
        "split_identifiers": {
            "environment": "ENV-3",
            "train_split": "train",
            "test_split": "test",
            "train_samples": len(train_idx),
            "test_samples": len(test_idx),
        },
        "metrics": metrics,
        "checks": checks,
        "learning_demonstrated": bool(
            checks["encoder_loss_decreased"]
            and checks["decoder_loss_decreased"]
            and checks["trained_mse_below_untrained"]
        ),
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "controlled_comparison.json"
    markdown_path = output_dir / "controlled_comparison.md"
    json_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    rows = [
        "# Controlled Comparison",
        "",
        f"Seed: `{seed}`. Numerical tolerance: `{tolerance}`.",
        "",
        "| Variant | Reconstruction MSE | Predictive accuracy |",
        "| --- | ---: | ---: |",
    ]
    for name in ("placeholder", "untrained", "trained"):
        rows.append(
            f"| {name} | {metrics[name]['reconstruction_mse']:.8f} | "
            f"{metrics[name]['predictive_accuracy']:.8f} |"
        )
    rows.extend([
        "",
        "## Derived checks",
        "",
        *[f"- {name}: `{value}`" for name, value in checks.items()],
        "",
        f"Learning demonstrated: `{comparison['learning_demonstrated']}`.",
    ])
    markdown_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return comparison


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifacts/stress_test")
    parser.add_argument("--max-train", type=int, default=1000)
    parser.add_argument("--max-test", type=int, default=500)
    parser.add_argument("--epochs", type=int, default=25)
    args = parser.parse_args()
    result = run_comparison(
        Path(args.output), args.max_train, args.max_test, args.epochs
    )
    print(json.dumps({
        "learning_demonstrated": result["learning_demonstrated"],
        "output": str(Path(args.output)),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
