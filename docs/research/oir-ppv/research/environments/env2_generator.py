"""
ENV-2: Compositional Generation Generator
Evaluate unseen combinations of character, style, and context factors.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from environments.base import BaseEnvironment, EnvironmentConfig, GeneratedData, EnvironmentRegistry


@EnvironmentRegistry.register("ENV-2")
class Env2CompositionalGeneration(BaseEnvironment):
    """ENV-2: Compositional Generation Environment Generator."""
    
    def _validate_config(self) -> None:
        required = ["factors", "train_combinations", "test_combinations", "nuisance_variables", "outcome"]
        for req in required:
            if req not in self.config.raw_config:
                raise ValueError(f"ENV-2 config missing required section: {req}")
    
    def generate(self) -> GeneratedData:
        gen_cfg = self.config.generation
        n_samples = gen_cfg.get("num_samples", 15000)
        train_ratio = gen_cfg.get("train_ratio", 0.7)
        val_ratio = gen_cfg.get("val_ratio", 0.15)
        test_ratio = gen_cfg.get("test_ratio", 0.15)
        
        # Get factors
        factors_cfg = self.config.raw_config.get("factors", [])
        factor_names = [f["name"] for f in factors_cfg]
        
        # Get train/test combinations
        train_combos = self.config.raw_config.get("train_combinations", [])
        test_combos = self.config.raw_config.get("test_combinations", [])
        all_combos = train_combos + test_combos
        
        # Sample data for each combination proportionally
        n_combos = len(all_combos)
        samples_per_combo = n_samples // n_combos
        remainder = n_samples % n_combos
        
        observations_list = []
        labels_list = []
        metadata_list = {"factor_values": {name: [] for name in factor_names}}
        combo_indices = {"train": [], "val": [], "test": [], "ood": []}
        current_idx = 0
        
        for combo_idx, combo in enumerate(all_combos):
            n_combo_samples = samples_per_combo + (1 if combo_idx < remainder else 0)
            
            # Sample nuisance for this combination
            nuisance_vars = self.config.raw_config.get("nuisance_variables", [])
            nuisances = self._sample_nuisances(nuisance_vars, n_combo_samples)
            
            # Build observations for this combination
            combo_obs = self._build_observations(combo, nuisances, factors_cfg)
            observations_list.append(combo_obs)
            
            # Compute labels (determined by character factor)
            outcome_cfg = self.config.raw_config.get("outcome", {})
            determined_by = outcome_cfg.get("determined_by", ["character"])
            mapping = outcome_cfg.get("mapping", {})
            key_factor = determined_by[0]
            key_idx = factor_names.index(key_factor)
            label_value = mapping.get(combo[key_idx], 0)
            labels_list.append(np.full(n_combo_samples, label_value, dtype=int))
            
            # Track metadata
            for fname, fval in zip(factor_names, combo):
                metadata_list["factor_values"][fname].extend([fval] * n_combo_samples)
            
            # Track combo indices
            is_train = combo in train_combos
            indices = np.arange(current_idx, current_idx + n_combo_samples)
            if is_train:
                combo_indices["train"].extend(indices)
            else:
                combo_indices["test"].extend(indices)
            
            current_idx += n_combo_samples
        
        # Concatenate all
        observations = np.vstack(observations_list) if observations_list else np.empty((0, 0))
        labels = np.concatenate(labels_list) if labels_list else np.empty(0, dtype=int)
        
        # Shuffle within train/test
        train_indices = np.array(combo_indices["train"])
        test_indices = np.array(combo_indices["test"])
        self.rng.shuffle(train_indices)
        self.rng.shuffle(test_indices)
        
        # Split train into train/val
        n_train = len(train_indices)
        n_val = int(n_train * val_ratio / train_ratio)
        val_indices = train_indices[:n_val]
        train_indices = train_indices[n_val:]
        
        splits = {
            "train": train_indices,
            "val": val_indices,
            "test": test_indices,
            "ood": np.array(combo_indices["ood"])
        }
        
        # Add OOD splits
        ood_splits = self._create_ood_splits(metadata_list["factor_values"], splits)
        splits.update(ood_splits)
        
        # Convert metadata lists to arrays
        for fname in metadata_list["factor_values"]:
            metadata_list["factor_values"][fname] = np.array(metadata_list["factor_values"][fname])
        
        return GeneratedData(
            observations=observations,
            labels=labels,
            metadata=metadata_list,
            splits=splits,
            config_hash=self.get_config_hash(),
            seed=self.seed,
            timestamp=datetime.now().isoformat()
        )
    
    def _sample_nuisances(self, nuisance_vars: List[Dict], n: int) -> Dict[str, np.ndarray]:
        """Sample nuisance variables."""
        nuisances = {}
        for var in nuisance_vars:
            name = var["name"]
            vtype = var["type"]
            dist = var.get("distribution", "normal")
            
            if vtype == "continuous":
                if dist == "normal":
                    params = var.get("params", {"mean": 0.0, "std": 0.05})
                    nuisances[name] = self.rng.normal(params["mean"], params["std"], size=n)
                elif dist == "uniform":
                    params = var.get("params", {"low": 0, "high": 1})
                    nuisances[name] = self.rng.uniform(params["low"], params["high"], size=n)
            elif vtype == "categorical":
                values = var.get("values", [])
                probs = var.get("probs", [1.0/len(values)] * len(values))
                nuisances[name] = self.rng.choice(values, size=n, p=probs)
        return nuisances
    
    def _build_observations(self, combo: Tuple, nuisances: Dict, factors_cfg: List[Dict]) -> np.ndarray:
        """Build observation matrix from factor combination and nuisances."""
        # Get n_samples from first nuisance array
        n_samples = len(next(iter(nuisances.values()))) if nuisances else 1
        
        all_arrays = []
        factor_names = [f["name"] for f in factors_cfg]
        
        # Factor variables (one-hot encoded) - repeat for n_samples
        for fname, fval in zip(factor_names, combo):
            factor_cfg = next(f for f in factors_cfg if f["name"] == fname)
            values = factor_cfg.get("values", [])
            # One-hot encoding
            for v in values:
                all_arrays.append(np.full((n_samples,), 1.0 if v == fval else 0.0))
        
        # Nuisance variables
        for name, arr in nuisances.items():
            if arr.ndim == 1:
                if arr.dtype.kind in 'SU':
                    unique = np.unique(arr)
                    for u in unique:
                        all_arrays.append((arr == u).astype(float))
                else:
                    all_arrays.append(arr)
        
        if all_arrays:
            obs = np.column_stack(all_arrays)
        else:
            obs = np.empty((n_samples, 0))
        
        return obs
    
    def _create_ood_splits(self, factor_values: Dict, splits: Dict) -> Dict[str, np.ndarray]:
        """Create OOD splits for compositional generalization."""
        ood_splits = {}
        ood_config = self.config.raw_config.get("ood_splits", [])
        
        for ood in ood_config:
            name = ood.get("name", "ood")
            
            if "holdout_factor" in ood:
                holdout_factor = ood["holdout_factor"]
                holdout_values = ood.get("holdout_values", [])
                
                mask = np.zeros(len(factor_values[holdout_factor]), dtype=bool)
                for val in holdout_values:
                    mask |= (factor_values[holdout_factor] == val)
                
                ood_indices = np.where(mask)[0]
                if len(ood_indices) > 0:
                    ood_splits[f"ood_{name}"] = ood_indices
            
            elif "holdout_combinations" in ood:
                # For fully unseen combinations - already in test split
                pass
        
        return ood_splits
    
    def get_intervention_targets(self) -> List[str]:
        return self.config.raw_config.get("intervention_targets", [])
    
    def intervene(self, data: GeneratedData, target: str, value: Any) -> GeneratedData:
        """Apply intervention on factor or nuisance variable."""
        new_metadata = {k: v.copy() if isinstance(v, dict) else v for k, v in data.metadata.items()}
        
        if target in new_metadata.get("factor_values", {}):
            new_metadata["factor_values"][target] = np.full_like(
                new_metadata["factor_values"][target], value
            )
        
        # Rebuild observations (simplified - full rebuild would need factor configs)
        # For now, return copy with metadata updated
        return GeneratedData(
            observations=data.observations.copy(),
            labels=data.labels.copy(),
            metadata=new_metadata,
            splits=data.splits.copy(),
            config_hash=data.config_hash,
            seed=data.seed,
            timestamp=datetime.now().isoformat()
        )


from datetime import datetime