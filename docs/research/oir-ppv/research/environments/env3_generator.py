"""
ENV-3: Causal Dynamics Generator
Structural Causal Model with state, action, outcome and intervention variables.
"""

import numpy as np
from typing import Dict, Any, List
from environments.base import BaseEnvironment, EnvironmentConfig, GeneratedData, EnvironmentRegistry


@EnvironmentRegistry.register("ENV-3")
class Env3CausalDynamics(BaseEnvironment):
    """ENV-3: Causal Dynamics Environment Generator (SCM-based)."""
    
    def _validate_config(self) -> None:
        required = ["scm", "intervention_targets", "counterfactual_queries"]
        for req in required:
            if req not in self.config.raw_config:
                raise ValueError(f"ENV-3 config missing required section: {req}")
    
    def generate(self) -> GeneratedData:
        gen_cfg = self.config.generation
        n_episodes = gen_cfg.get("num_episodes", 5000)
        episode_length = gen_cfg.get("episode_length", 10)
        train_ratio = gen_cfg.get("train_ratio", 0.7)
        val_ratio = gen_cfg.get("val_ratio", 0.15)
        test_ratio = gen_cfg.get("test_ratio", 0.15)
        
        n_samples = n_episodes * episode_length
        
        scm_cfg = self.config.raw_config.get("scm", {})
        exogenous_cfg = scm_cfg.get("exogenous", [])
        endogenous_cfg = scm_cfg.get("endogenous", [])
        
        # Generate exogenous variables
        exogenous = self._sample_exogenous(exogenous_cfg, n_episodes)
        
        # Compute endogenous variables per episode
        data_list = []
        
        for ep in range(n_episodes):
            ep_data = self._generate_episode(ep, episode_length, n_episodes, exogenous, endogenous_cfg)
            data_list.append(ep_data)
        
        # Concatenate episodes
        observations = np.vstack([d["observations"] for d in data_list])
        labels = np.concatenate([d["labels"] for d in data_list])
        
        # Build metadata
        metadata = {
            "episodes": np.repeat(np.arange(n_episodes), episode_length),
            "timesteps": np.tile(np.arange(episode_length), n_episodes),
            "S": np.concatenate([d["S"] for d in data_list]),
            "A": np.concatenate([d["A"] for d in data_list]),
            "Z": np.concatenate([d["Z"] for d in data_list]),
            "N": np.concatenate([d["N"] for d in data_list]),
            "Y": np.concatenate([d["Y"] for d in data_list]),
        }
        
        # Create splits (by episode)
        episode_indices = np.arange(n_episodes)
        self.rng.shuffle(episode_indices)
        
        n_train_ep = int(n_episodes * train_ratio)
        n_val_ep = int(n_episodes * val_ratio)
        n_test_ep = int(n_episodes * test_ratio)
        
        train_ep = episode_indices[:n_train_ep]
        val_ep = episode_indices[n_train_ep:n_train_ep + n_val_ep]
        test_ep = episode_indices[n_train_ep + n_val_ep:n_train_ep + n_val_ep + n_test_ep]
        ood_ep = episode_indices[n_train_ep + n_val_ep + n_test_ep:]
        
        # Convert episode indices to sample indices
        def ep_to_samples(eps):
            if len(eps) == 0:
                return np.array([], dtype=int)
            return np.concatenate([np.arange(ep * episode_length, (ep + 1) * episode_length) for ep in eps])
        
        splits = {
            "train": ep_to_samples(train_ep),
            "val": ep_to_samples(val_ep),
            "test": ep_to_samples(test_ep),
            "ood": ep_to_samples(ood_ep)
        }
        
        # Add OOD splits
        ood_splits = self._create_ood_splits(metadata, splits, episode_length)
        if ood_splits:
            held_out = np.unique(np.concatenate(list(ood_splits.values())))
            for split_name in ("train", "val", "test", "ood"):
                splits[split_name] = np.setdiff1d(
                    splits[split_name], held_out, assume_unique=False
                )
        splits.update(ood_splits)
        
        return GeneratedData(
            observations=observations,
            labels=labels,
            metadata=metadata,
            splits=splits,
            config_hash=self.get_config_hash(),
            seed=self.seed,
            timestamp=datetime.now().isoformat()
        )
    
    def _sample_exogenous(self, exogenous_cfg: List[Dict], n_episodes: int) -> Dict[str, np.ndarray]:
        """Sample exogenous variables (U)."""
        exogenous = {}
        for var in exogenous_cfg:
            name = var["name"]
            vtype = var["type"]
            dist = var.get("distribution", "normal")
            params = var.get("params", {"mean": 0.0, "std": 1.0})
            
            if dist == "normal":
                exogenous[name] = self.rng.normal(params["mean"], params["std"], size=n_episodes)
            elif dist == "uniform":
                exogenous[name] = self.rng.uniform(params["low"], params["high"], size=n_episodes)
        return exogenous
    
    def _generate_episode(self, ep_idx: int, episode_length: int, n_episodes: int,
                          exogenous: Dict, endogenous_cfg: List[Dict]) -> Dict[str, Any]:
        """Generate single episode using SCM equations."""
        # Sample context Z for this episode (constant within episode)
        z_vars = [v for v in endogenous_cfg if v["name"] == "Z"]
        if z_vars:
            z_cfg = z_vars[0]
            values = z_cfg.get("values", ["ctx_1", "ctx_2", "ctx_3"])
            Z_ep = self.rng.choice(values)
        else:
            Z_ep = "ctx_1"
        
        # Sample nuisance N for each timestep
        n_vars = [v for v in endogenous_cfg if v["name"] == "N"]
        if n_vars:
            n_cfg = n_vars[0]
            params = n_cfg.get("params", {"mean": 0.0, "std": 0.2})
            N_ep = self.rng.normal(params["mean"], params["std"], size=episode_length)
        else:
            N_ep = np.zeros(episode_length)
        
        # Get exogenous for this episode
        U_state = exogenous.get("U_state", np.zeros(n_episodes))[ep_idx]
        U_action = exogenous.get("U_action", np.zeros(n_episodes))[ep_idx]
        U_outcome = exogenous.get("U_outcome", np.zeros(n_episodes))[ep_idx]
        
        # Compute endogenous variables per timestep
        S = np.full(episode_length, U_state)  # S = U_state
        A = 0.5 * S + U_action  # A = 0.5 * S + U_action
        
        # Context effects
        context_effects = {"ctx_1": 0.0, "ctx_2": 0.5, "ctx_3": -0.5}
        ctx_effect = context_effects.get(Z_ep, 0.0)
        
        # Y = 1.0 * S + 0.8 * A + context_effect(Z) + N
        Y = 1.0 * S + 0.8 * A + ctx_effect + N_ep
        
        # Build observations: [S, A, Z_onehot, N]
        Z_onehot = np.eye(3)[["ctx_1", "ctx_2", "ctx_3"].index(Z_ep)] if Z_ep in ["ctx_1", "ctx_2", "ctx_3"] else np.zeros(3)
        Z_onehot = np.tile(Z_onehot, (episode_length, 1))
        
        observations = np.column_stack([
            S.reshape(-1, 1),
            A.reshape(-1, 1),
            Z_onehot,
            N_ep.reshape(-1, 1)
        ])
        
        # Labels: discretize Y for classification
        labels = np.digitize(Y, bins=[-1, 0, 1, 2]) - 1  # Rough discretization
        labels = np.clip(labels, 0, 4)
        
        return {
            "observations": observations,
            "labels": labels,
            "S": S,
            "A": A,
            "Z": np.full(episode_length, Z_ep),
            "N": N_ep,
            "Y": Y
        }
    
    def _create_ood_splits(self, metadata: Dict, splits: Dict, episode_length: int) -> Dict[str, np.ndarray]:
        """Create OOD splits for causal dynamics."""
        ood_splits = {}
        ood_config = self.config.raw_config.get("ood_splits", [])
        
        for ood in ood_config:
            name = ood.get("name", "ood")
            
            if "holdout" in ood:
                holdout = ood["holdout"]
                # Holdout by context
                if isinstance(holdout, list):
                    mask = np.isin(metadata["Z"], holdout)
                    ood_indices = np.where(mask)[0]
                    if len(ood_indices) > 0:
                        ood_splits[f"ood_{name}"] = ood_indices
            
            elif "action_range" in ood:
                # Extrapolated action range - mark samples with action outside training range
                action_range = ood["action_range"]
                mask = (metadata["A"] < action_range[0]) | (metadata["A"] > action_range[1])
                ood_indices = np.where(mask)[0]
                if len(ood_indices) > 0:
                    ood_splits[f"ood_{name}"] = ood_indices
            
            elif "nuisance_std" in ood:
                # Higher nuisance - would need separate generation, mark as note
                pass
        
        return ood_splits
    
    def get_intervention_targets(self) -> List[str]:
        targets = []
        for target in self.config.raw_config.get("intervention_targets", []):
            targets.append(target.get("name", ""))
        return [t for t in targets if t]
    
    def intervene(self, data: GeneratedData, target: str, value: Any) -> GeneratedData:
        """Apply SCM intervention do(target=value)."""
        new_metadata = {k: v.copy() for k, v in data.metadata.items()}
        new_obs = data.observations.copy()
        
        if target == "do(A)":
            # Intervene on action: set A to value, recompute Y
            new_metadata["A"] = np.full_like(new_metadata["A"], value)
            # Recompute Y = 1.0*S + 0.8*A + ctx_effect(Z) + N
            context_effects = {"ctx_1": 0.0, "ctx_2": 0.5, "ctx_3": -0.5}
            ctx_effect = np.array([context_effects.get(z, 0.0) for z in new_metadata["Z"]])
            new_Y = 1.0 * new_metadata["S"] + 0.8 * new_metadata["A"] + ctx_effect + new_metadata["N"]
            new_metadata["Y"] = new_Y
            
            # Update observations
            new_obs[:, 1] = value  # A column
            # Recompute labels
            new_labels = np.digitize(new_Y, bins=[-1, 0, 1, 2]) - 1
            new_labels = np.clip(new_labels, 0, 4)
            
        elif target == "do(Z)":
            # Intervene on context
            new_metadata["Z"] = np.full_like(new_metadata["Z"], value)
            context_effects = {"ctx_1": 0.0, "ctx_2": 0.5, "ctx_3": -0.5}
            ctx_effect = context_effects.get(value, 0.0)
            new_Y = 1.0 * new_metadata["S"] + 0.8 * new_metadata["A"] + ctx_effect + new_metadata["N"]
            new_metadata["Y"] = new_Y
            
            # Update observations (Z one-hot columns 2,3,4)
            z_idx = ["ctx_1", "ctx_2", "ctx_3"].index(value) if value in ["ctx_1", "ctx_2", "ctx_3"] else 0
            new_obs[:, 2:5] = 0
            new_obs[:, 2 + z_idx] = 1
            
            new_labels = np.digitize(new_Y, bins=[-1, 0, 1, 2]) - 1
            new_labels = np.clip(new_labels, 0, 4)
            
        elif target == "do(N)":
            # Intervene on nuisance
            new_metadata["N"] = np.full_like(new_metadata["N"], value)
            context_effects = {"ctx_1": 0.0, "ctx_2": 0.5, "ctx_3": -0.5}
            ctx_effect = np.array([context_effects.get(z, 0.0) for z in new_metadata["Z"]])
            new_Y = 1.0 * new_metadata["S"] + 0.8 * new_metadata["A"] + ctx_effect + new_metadata["N"]
            new_metadata["Y"] = new_Y
            
            # Update observations (N is last column)
            new_obs[:, -1] = value
            
            new_labels = np.digitize(new_Y, bins=[-1, 0, 1, 2]) - 1
            new_labels = np.clip(new_labels, 0, 4)
        
        else:
            new_labels = data.labels.copy()
        
        return GeneratedData(
            observations=new_obs,
            labels=new_labels,
            metadata=new_metadata,
            splits=data.splits.copy(),
            config_hash=data.config_hash,
            seed=data.seed,
            timestamp=datetime.now().isoformat()
        )


from datetime import datetime
