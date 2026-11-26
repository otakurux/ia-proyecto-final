from dataclasses import dataclass


@dataclass
class GAConfig:
    n_nodes: int = 24
    population_size: int = 60
    generations: int = 80
    crossover_prob: float = 0.85
    mutation_prob: float = 0.02
    tournament_size: int = 3
    elitism: int = 2
    penalty: float = 10.0
    budget: float = 120.0
    critical_ratio: float = 0.35
    cost_min: float = 20.0
    cost_max: float = 45.0
    runs_per_topology: int = 30
    seed: int = 42
    output_dir: str = "outputs"
