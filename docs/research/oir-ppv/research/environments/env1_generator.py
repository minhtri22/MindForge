"""
ENV-1: Identity and Style Shift Generator
Keep underlying mechanism fixed while changing style, identity, or presentation variables.
"""

import numpy as np
from typing import Dict, Any, List
from environments.base import BaseEnvironment, EnvironmentConfig, GeneratedData, EnvironmentRegistry


@EnvironmentRegistry.register("ENV-1")
class Env1IdentityStyleShift(BaseEnvironment):
    """ENV-1: Identity and Style Shift Environment Generator."""
    
    def _validate_config(self) -> None:
        required = ["context_variables", "nuisance_variables", "structural_variables", "outcome"]
        for req in required:
            if req not in self.config.raw_config:
                raise ValueError(f"ENV-1 config missing required section: {req}")
    
    def generate(self) -> GeneratedData:
        gen_cfg = self.config.generation
        n_samples = gen_cfg.get("num_samples", 10000)
        train_ratio = gen_cfg.get("train_ratio", 0.7)
        val_ratio = gen_cfg.get("val_ratio", 0.15)
        test_ratio = gen_cfg.get("test_ratio", 0.15)
        
        # Parse context variables (Z)
        context_vars = self.config.raw_config.get("context_variables", [])
        contexts = self._sample_contexts(context_vars, n_samples)
        
        # Parse nuisance variables (N)
        nuisance_vars = self.config.raw_config.get("nuisance_variables", [])
        nuisances = self._sample_nuisances(nuisance_vars, n_samples)
        
        # Parse structural variables (invariant mechanism)
        structural_vars = self.config.raw_config.get("structural_variables", [])
        structural = self._sample_structural(structural_vars, n_samples)
        
        # Compute outcome (Y) from structural variables only
        outcome_cfg = self.config.raw_config.get("outcome", {})
        labels = self._compute_outcome(structural, outcome_cfg)
        
        # Build observations: combine all variables
        observations = self._build_observations(structural, contexts, nuisances)
        
        # Create splits
        splits = self._split_indices(n_samples, train_ratio, val_ratio, test_ratio)
        
        # Handle OOD splits
        ood_splits = self._create_ood_splits(contexts, structural, splits)
        if ood_splits:
            held_out = np.unique(np.concatenate(list(ood_splits.values())))
            for split_name in ("train", "val", "test"):
                splits[split_name] = np.setdiff1d(
                    splits[split_name], held_out, assume_unique=False
                )
        splits.update(ood_splits)
        
        metadata = {
            "context_variables": contexts,
            "nuisance_variables": nuisances,
            "structural_variables": structural,
            "context_names": [v["name"] for v in context_vars],
            "nuisance_names": [v["name"] for v in nuisance_vars],
            "structural_names": [v["name"] for v in structural_vars],
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
    
    def _sample_contexts(self, context_vars: List[Dict], n: int) -> Dict[str, np.ndarray]:
        """Sample context variables (Z)."""
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
            elif vtype == "continuous":
                if dist == "uniform":
                    params = var.get("params", {"low": 0, "high": 1})
                    contexts[name] = self.rng.uniform(params["low"], params["high"], size=n)
                elif dist == "normal":
                    params = var.get("params", {"mean": 0, "std": 1})
                    contexts[name] = self.rng.normal(params["mean"], params["std"], size=n)
        return contexts
    
    def _sample_nuisances(self, nuisance_vars: List[Dict], n: int) -> Dict[str, np.ndarray]:
        """Sample nuisance variables (N)."""
        nuisances = {}
        for var in nuisance_vars:
            name = var["name"]
            vtype = var["type"]
            dist = var.get("distribution", "normal")
            
            if vtype == "continuous":
                if dist == "normal":
                    params = var.get("params", {"mean": 0.0, "std": 0.1})
                    nuisances[name] = self.rng.normal(params["mean"], params["std"], size=n)
                elif dist == "uniform":
                    params = var.get("params", {"low": 0.5, "high": 1.5})
                    nuisances[name] = self.rng.uniform(params["low"], params["high"], size=n)
            elif vtype == "categorical":
                values = var.get("values", [])
                probs = var.get("probs", [1.0/len(values)] * len(values))
                nuisances[name] = self.rng.choice(values, size=n, p=probs)
        return nuisances
    
    def _sample_structural(self, structural_vars: List[Dict], n: int) -> Dict[str, np.ndarray]:
        """Sample structural/invariant variables."""
        structural = {}
        for var in structural_vars:
            name = var["name"]
            vtype = var["type"]
            
            if vtype == "categorical":
                values = var.get("values", [])
                structural[name] = self.rng.choice(values, size=n)
            elif vtype == "continuous":
                dist = var.get("distribution", "uniform")
                params = var.get("params", {"low": 0.3, "high": 1.0})
                if dist == "uniform":
                    structural[name] = self.rng.uniform(params["low"], params["high"], size=n)
                elif dist == "normal":
                    structural[name] = self.rng.normal(params["mean"], params["std"], size=n)
        return structural
    
    def _compute_outcome(self, structural: Dict[str, np.ndarray], outcome_cfg: Dict) -> np.ndarray:
        """Compute labels from structural variables only (invariant mechanism)."""
        determined_by = outcome_cfg.get("determined_by", [])
        mapping = outcome_cfg.get("mapping", {})
        
        if not determined_by:
            return np.zeros(len(next(iter(structural.values()))), dtype=int)
        
        # Use first determining variable
        key_var = determined_by[0]
        values = structural[key_var]
        
        # Map to labels
        labels = np.array([mapping.get(v, 0) for v in values], dtype=int)
        return labels
    
    def _build_observations(self, structural: Dict, contexts: Dict, nuisances: Dict) -> np.ndarray:
        """Build observation matrix from all variables."""
        # Order: structural, context, nuisance
        all_arrays = []
        feature_names = []
        
        for name, arr in structural.items():
            if arr.ndim == 1:
                arr = arr.reshape(-1, 1)
            all_arrays.append(arr)
            feature_names.append(f"struct_{name}")
        
        for name, arr in contexts.items():
            if arr.ndim == 1:
                if arr.dtype.kind in 'SU':  # string/unicode
                    # One-hot encode categorical
                    definition = next(
                        (item for item in self.config.raw_config.get("context_variables", [])
                         if item.get("name") == name), {}
                    )
                    unique = definition.get("values", np.unique(arr))
                    for u in unique:
                        all_arrays.append((arr == u).astype(float).reshape(-1, 1))
                        feature_names.append(f"ctx_{name}_{u}")
                else:
                    all_arrays.append(arr.reshape(-1, 1))
                    feature_names.append(f"ctx_{name}")
            else:
                all_arrays.append(arr)
                feature_names.append(f"ctx_{name}")
        
        for name, arr in nuisances.items():
            if arr.ndim == 1:
                if arr.dtype.kind in 'SU':
                    definition = next(
                        (item for item in self.config.raw_config.get("nuisance_variables", [])
                         if item.get("name") == name), {}
                    )
                    unique = definition.get("values", np.unique(arr))
                    for u in unique:
                        all_arrays.append((arr == u).astype(float).reshape(-1, 1))
                        feature_names.append(f"nuis_{name}_{u}")
                else:
                    all_arrays.append(arr.reshape(-1, 1))
                    feature_names.append(f"nuis_{name}")
            else:
                all_arrays.append(arr)
                feature_names.append(f"nuis_{name}")
        
        if all_arrays:
            obs = np.hstack(all_arrays)
        else:
            obs = np.empty((len(next(iter(structural.values()))), 0))
        
        return obs
    
    def _create_ood_splits(self, contexts: Dict, structural: Dict, splits: Dict) -> Dict[str, np.ndarray]:
        """Create OOD test splits based on config."""
        ood_splits = {}
        ood_config = self.config.raw_config.get("ood_splits", [])
        
        for ood in ood_config:
            name = ood.get("name", "ood")
            holdout = ood.get("holdout", [])
            
            if not holdout:
                continue
            
            # Find indices matching holdout criteria
            mask = np.ones(len(next(iter(contexts.values()))), dtype=bool)
            
            for criterion in holdout:
                if isinstance(criterion, list):
                    # Combination holdout
                    for c in criterion:
                        # Parse "style_c" format
                        for ctx_name, ctx_vals in contexts.items():
                            if c in ctx_vals:
                                mask &= (ctx_vals == c)
                else:
                    # Single value holdout
                    for ctx_name, ctx_vals in contexts.items():
                        if criterion in ctx_vals:
                            mask &= (ctx_vals == criterion)
            
            ood_indices = np.where(mask)[0]
            if len(ood_indices) > 0:
                ood_splits[f"ood_{name}"] = ood_indices
        
        return ood_splits
    
    def get_intervention_targets(self) -> List[str]:
        return self.config.raw_config.get("intervention_targets", [])
    
    def intervene(self, data: GeneratedData, target: str, value: Any) -> GeneratedData:
        """Apply intervention do(target=value)."""
        import copy
        new_metadata = copy.deepcopy(data.metadata)
        
        if target in new_metadata.get("context_variables", {}):
            new_metadata["context_variables"][target] = np.full_like(
                new_metadata["context_variables"][target], value
            )
        elif target in new_metadata.get("nuisance_variables", {}):
            new_metadata["nuisance_variables"][target] = np.full_like(
                new_metadata["nuisance_variables"][target], value
            )
        
        # Rebuild observations with intervened value
        new_obs = self._build_observations(
            new_metadata["structural_variables"],
            new_metadata["context_variables"],
            new_metadata["nuisance_variables"]
        )
        
        return GeneratedData(
            observations=new_obs,
            labels=data.labels.copy(),
            metadata=new_metadata,
            splits=data.splits.copy(),
            config_hash=data.config_hash,
            seed=data.seed,
            timestamp=datetime.now().isoformat()
        )


# Import datetime for intervene method
from datetime import datetime
