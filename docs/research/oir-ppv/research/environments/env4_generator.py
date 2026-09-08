"""
ENV-4: Adversarial Shortcut Generator
Introduce training correlations between nuisance variables and outcomes,
then test shortcut resistance.
"""

import numpy as np
from typing import Dict, Any, List
from environments.base import BaseEnvironment, EnvironmentConfig, GeneratedData, EnvironmentRegistry


@EnvironmentRegistry.register("ENV-4")
class Env4AdversarialShortcut(BaseEnvironment):
    """ENV-4: Adversarial Shortcut Environment Generator."""
    
    def _validate_config(self) -> None:
        required = ["true_mechanism", "shortcut", "other_nuisance", "context_variables"]
        for req in required:
            if req not in self.config.raw_config:
                raise ValueError(f"ENV-4 config missing required section: {req}")
        
        # Check for outcome either at root or in true_mechanism
        if "outcome" not in self.config.raw_config and "outcome" not in self.config.raw_config.get("true_mechanism", {}):
            raise ValueError("ENV-4 config missing outcome section (root or true_mechanism.outcome)")
    
    def generate(self) -> GeneratedData:
        gen_cfg = self.config.generation
        n_samples = gen_cfg.get("num_samples", 10000)
        train_ratio = gen_cfg.get("train_ratio", 0.7)
        val_ratio = gen_cfg.get("val_ratio", 0.15)
        test_ratio = gen_cfg.get("test_ratio", 0.15)
        
        # True mechanism
        true_mech = self.config.raw_config.get("true_mechanism", {})
        structural_vars = true_mech.get("structural_variables", [])
        outcome_cfg = true_mech.get("outcome", {})
        
        # Shortcut config
        shortcut_cfg = self.config.raw_config.get("shortcut", {})
        correlation_strength = shortcut_cfg.get("correlation_strength", 0.9)
        nuisance_name = shortcut_cfg.get("nuisance_variable", {}).get("name", "spurious_feature")
        
        # Domain context
        context_vars = self.config.raw_config.get("context_variables", [])
        
        # Generate structural variables (invariant)
        structural = self._sample_structural(structural_vars, n_samples)
        
        # Compute true labels from structural only
        labels = self._compute_true_labels(structural, outcome_cfg)
        
        # Generate context
        contexts = self._sample_contexts(context_vars, n_samples)
        
        # Generate spurious feature with correlation (training) or without (test)
        # We'll generate all data, then split with different correlation
        spurious_feature = self._generate_spurious_feature(labels, shortcut_cfg, n_samples)
        
        # Other nuisance variables
        other_nuisance_cfg = self.config.raw_config.get("other_nuisance", [])
        other_nuisances = self._sample_other_nuisances(other_nuisance_cfg, n_samples)
        other_nuisances[nuisance_name] = spurious_feature
        
        # Build observations
        observations = self._build_observations(structural, contexts, other_nuisances)
        
        # Create splits
        splits = self._split_indices(n_samples, train_ratio, val_ratio, test_ratio)
        
        # Apply different shortcut strengths per split
        self._apply_split_shortcuts(splits, labels, nuisance_name, shortcut_cfg, other_nuisances, observations, contexts, structural)
        
        # Add OOD splits
        ood_splits = self._create_ood_splits(contexts, labels, splits, shortcut_cfg)
        splits.update(ood_splits)
        
        metadata = {
            "structural_variables": structural,
            "context_variables": contexts,
            "nuisance_variables": other_nuisances,
            "true_labels": labels,
            "shortcut_feature": nuisance_name,
        }
        
        return GeneratedData(
            observations=observations,
            labels=labels,
            metadata=metadata,
            splits=splits,
            config_hash=self.get_config_hash(),
            seed=self.seed,
            timestamp=datetime.now().isoformat()
        )
    
    def _sample_structural(self, structural_vars: List[Dict], n: int) -> Dict[str, np.ndarray]:
        """Sample structural/invariant variables."""
        structural = {}
        for var in structural_vars:
            name = var["name"]
            vtype = var["type"]
            
            if vtype == "continuous":
                dist = var.get("distribution", "normal")
                params = var.get("params", {"mean": 0.0, "std": 1.0})
                if dist == "normal":
                    structural[name] = self.rng.normal(params["mean"], params["std"], size=n)
                elif dist == "uniform":
                    structural[name] = self.rng.uniform(params["low"], params["high"], size=n)
            elif vtype == "categorical":
                values = var.get("values", [])
                dist = var.get("distribution", "uniform")
                if dist == "uniform":
                    structural[name] = self.rng.choice(values, size=n)
                else:
                    probs = var.get("probs", [1.0/len(values)] * len(values))
                    structural[name] = self.rng.choice(values, size=n, p=probs)
        return structural
    
    def _compute_true_labels(self, structural: Dict, outcome_cfg: Dict) -> np.ndarray:
        """Compute true labels from structural variables only."""
        determined_by = outcome_cfg.get("determined_by", [])
        mapping = outcome_cfg.get("mapping", {})
        
        if not determined_by:
            return np.zeros(len(next(iter(structural.values()))), dtype=int)
        
        key_var = determined_by[0]
        values = structural[key_var]
        labels = np.array([mapping.get(v, 0) for v in values], dtype=int)
        return labels
    
    def _sample_contexts(self, context_vars: List[Dict], n: int) -> Dict[str, np.ndarray]:
        """Sample context variables."""
        contexts = {}
        for var in context_vars:
            name = var["name"]
            vtype = var["type"]
            values = var.get("values", [])
            dist = var.get("distribution", "uniform")
            
            if vtype == "categorical":
                if dist == "uniform":
                    contexts[name] = self.rng.choice(values, size=n)
                else:
                    probs = var.get("probs", [1.0/len(values)] * len(values))
                    contexts[name] = self.rng.choice(values, size=n, p=probs)
        return contexts
    
    def _generate_spurious_feature(self, labels: np.ndarray, shortcut_cfg: Dict, n: int) -> np.ndarray:
        """Generate spurious feature with configurable correlation to labels."""
        injection_method = shortcut_cfg.get("injection_method", "conditional")
        
        if injection_method == "conditional":
            train_means = shortcut_cfg.get("train_conditional_means", {})
            # Default: use train means for all (will be overridden per split)
            default_means = {0: -1.5, 1: 0.0, 2: 1.5}
            means = {**default_means, **train_means}
            
            strength = float(shortcut_cfg.get("correlation_strength", 1.0))
            spurious = np.zeros(n)
            for label_val in np.unique(labels):
                mask = (labels == label_val)
                mean = strength * float(means.get(int(label_val), 0.0))
                spurious[mask] = self.rng.normal(mean, 1.0, size=mask.sum())
            
            return spurious
        
        return self.rng.normal(0, 1, size=n)
    
    def _sample_other_nuisances(self, other_nuisance_cfg: List[Dict], n: int) -> Dict[str, np.ndarray]:
        """Sample other nuisance variables (not correlated with label)."""
        nuisances = {}
        for var in other_nuisance_cfg:
            name = var["name"]
            vtype = var["type"]
            dist = var.get("distribution", "uniform")
            
            if vtype == "categorical":
                values = var.get("values", [])
                probs = var.get("probs", [1.0/len(values)] * len(values))
                nuisances[name] = self.rng.choice(values, size=n, p=probs)
            elif vtype == "continuous":
                if dist == "uniform":
                    params = var.get("params", {"low": -3.14, "high": 3.14})
                    nuisances[name] = self.rng.uniform(params["low"], params["high"], size=n)
                elif dist == "normal":
                    params = var.get("params", {"mean": 0.0, "std": 1.0})
                    nuisances[name] = self.rng.normal(params["mean"], params["std"], size=n)
        return nuisances
    
    def _build_observations(self, structural: Dict, contexts: Dict, nuisances: Dict) -> np.ndarray:
        """Build observation matrix."""
        all_arrays = []
        
        # Structural
        for name, arr in structural.items():
            if arr.ndim == 1:
                if arr.dtype.kind in 'SU':
                    definition = next(
                        (item for item in self.config.raw_config.get("true_mechanism", {}).get("structural_variables", [])
                         if item.get("name") == name), {}
                    )
                    unique = definition.get("values", np.unique(arr))
                    for u in unique:
                        all_arrays.append((arr == u).astype(float).reshape(-1, 1))
                else:
                    all_arrays.append(arr.reshape(-1, 1))
        
        # Contexts
        for name, arr in contexts.items():
            if arr.ndim == 1:
                if arr.dtype.kind in 'SU':
                    definition = next(
                        (item for item in self.config.raw_config.get("context_variables", [])
                         if item.get("name") == name), {}
                    )
                    unique = definition.get("values", np.unique(arr))
                    for u in unique:
                        all_arrays.append((arr == u).astype(float).reshape(-1, 1))
                else:
                    all_arrays.append(arr.reshape(-1, 1))
        
        # Nuisances
        for name, arr in nuisances.items():
            if arr.ndim == 1:
                if arr.dtype.kind in 'SU':
                    definition = next(
                        (item for item in self.config.raw_config.get("other_nuisance", [])
                         if item.get("name") == name), {}
                    )
                    unique = definition.get("values", np.unique(arr))
                    for u in unique:
                        all_arrays.append((arr == u).astype(float).reshape(-1, 1))
                else:
                    all_arrays.append(arr.reshape(-1, 1))
        
        if all_arrays:
            return np.hstack(all_arrays)
        return np.empty((len(next(iter(structural.values()))), 0))
    
    def _apply_split_shortcuts(self, splits: Dict, labels: np.ndarray, nuisance_name: str,
                               shortcut_cfg: Dict, nuisances: Dict, observations: np.ndarray,
                               contexts: Dict, structural: Dict) -> None:
        """Apply different shortcut correlations per split."""
        test_means = shortcut_cfg.get("test_conditional_means")
        if not test_means:
            return

        strength = float(shortcut_cfg.get("correlation_strength", 1.0))
        values = nuisances[nuisance_name]
        deployment = np.concatenate(
            [np.asarray(splits.get("val", [])), np.asarray(splits.get("test", []))]
        ).astype(int)
        for label_value in np.unique(labels[deployment]):
            indices = deployment[labels[deployment] == label_value]
            mean = strength * float(
                test_means.get(int(label_value), test_means.get(str(int(label_value)), 0.0))
            )
            values[indices] = self.rng.normal(mean, 1.0, size=len(indices))

        nuisances[nuisance_name] = values
        observations[:] = self._build_observations(structural, contexts, nuisances)
    
    def _create_ood_splits(self, contexts: Dict, labels: np.ndarray, 
                           splits: Dict, shortcut_cfg: Dict) -> Dict[str, np.ndarray]:
        """Create OOD splits with broken/reversed shortcuts."""
        ood_splits = {}
        ood_config = self.config.raw_config.get("ood_splits", [])
        
        for ood in ood_config:
            name = ood.get("name", "ood")
            
            if name == "shortcut_broken":
                # All test samples are shortcut-broken
                ood_splits[f"ood_{name}"] = splits["test"].copy()
            
            elif name == "reversed_shortcut":
                # Subset of test with reversed correlation
                # For simplicity, use half of test
                test_indices = splits["test"]
                mid = len(test_indices) // 2
                ood_splits[f"ood_{name}"] = test_indices[mid:]
            
            elif name == "unseen_domain" and "domain" in contexts:
                holdout = ood.get("holdout", [])
                if holdout:
                    domain_vals = contexts["domain"]
                    mask = np.isin(domain_vals[list(splits["test"])], holdout)
                    ood_indices = splits["test"][mask]
                    if len(ood_indices) > 0:
                        ood_splits[f"ood_{name}"] = ood_indices
        
        return ood_splits
    
    def get_intervention_targets(self) -> List[str]:
        return self.config.raw_config.get("intervention_targets", [])
    
    def intervene(self, data: GeneratedData, target: str, value: Any) -> GeneratedData:
        """Apply intervention on shortcut or nuisance feature."""
        import copy
        new_metadata = copy.deepcopy(data.metadata)
        
        if target in new_metadata.get("nuisance_variables", {}):
            new_metadata["nuisance_variables"][target] = np.full_like(
                new_metadata["nuisance_variables"][target], value
            )
        elif target in new_metadata.get("context_variables", {}):
            new_metadata["context_variables"][target] = np.full_like(
                new_metadata["context_variables"][target], value
            )
        
        # Rebuild observations
        new_obs = self._build_observations(
            new_metadata["structural_variables"],
            new_metadata["context_variables"],
            new_metadata["nuisance_variables"]
        )
        
        return GeneratedData(
            observations=new_obs,
            labels=data.labels.copy(),  # True labels unchanged by intervention on nuisance
            metadata=new_metadata,
            splits=data.splits.copy(),
            config_hash=data.config_hash,
            seed=data.seed,
            timestamp=datetime.now().isoformat()
        )


from datetime import datetime
