import csv
import os
import random
import networkx as nx
import numpy as np
from baselines import greedy_placement, random_placement
from config import GAConfig
from ga_core import run_ga
from topologies import generate_topology

TOPOLOGIES = ["campus_jerarquica", "libre_escala", "mundo_pequeno", "aleatoria"]


def run_single_demo(cfg: GAConfig, kind: str = "campus_jerarquica"):
    """Ejecuta una simulación individual detallada con traza paso a paso para la interfaz web."""
    rng = random.Random(cfg.seed)
    G, critical_edges, node_costs, node_labels = generate_topology(kind, cfg, rng)

    ga_rng = random.Random(cfg.seed + 100)
    ga_res = run_ga(critical_edges, node_costs, cfg, ga_rng, record_trace=True)
    greedy_res = greedy_placement(cfg.n_nodes, critical_edges, node_costs, cfg.budget, cfg.penalty)
    rand_res = random_placement(
        cfg.n_nodes, critical_edges, node_costs, cfg.budget, cfg.penalty, random.Random(cfg.seed + 200)
    )

    pos = nx.spring_layout(G, seed=42)
    nodes_data = []
    for n in G.nodes():
        x, y = pos[n]
        nodes_data.append(
            {
                "id": int(n),
                "label": node_labels[n],
                "cost": node_costs[n],
                "x": round(float(x), 4),
                "y": round(float(y), 4),
                "selected_final": int(ga_res["best_chromosome"][n]),
            }
        )

    crit_set = {tuple(sorted(e)) for e in critical_edges}
    edges_data = []
    for u, v in G.edges():
        edge_key = tuple(sorted((u, v)))
        is_crit = edge_key in crit_set
        covered_final = bool(ga_res["best_chromosome"][u] or ga_res["best_chromosome"][v])
        edges_data.append(
            {
                "u": int(u),
                "v": int(v),
                "u_label": node_labels[u],
                "v_label": node_labels[v],
                "critical": is_crit,
                "covered_final": covered_final,
            }
        )

    return {
        "config": {
            "topology": kind,
            "n_nodes": cfg.n_nodes,
            "population_size": cfg.population_size,
            "generations": cfg.generations,
            "crossover_prob": cfg.crossover_prob,
            "mutation_prob": cfg.mutation_prob,
            "tournament_size": cfg.tournament_size,
            "elitism": cfg.elitism,
            "penalty": cfg.penalty,
            "budget": cfg.budget,
            "seed": cfg.seed,
        },
        "graph": {
            "nodes": nodes_data,
            "edges": edges_data,
            "total_edges": len(edges_data),
            "critical_edges_count": len(critical_edges),
        },
        "ga_result": ga_res,
        "baselines": {
            "greedy": greedy_res,
            "random": rand_res,
        },
    }


def run_all_experiments(cfg: GAConfig):
    os.makedirs(cfg.output_dir, exist_ok=True)
    all_rows = []
    convergence_curves = {}
    sample_solutions = {}

    for kind in TOPOLOGIES:
        curves = []
        for run in range(cfg.runs_per_topology):
            run_seed = cfg.seed + run
            rng = random.Random(run_seed)

            G, critical_edges, node_costs, _ = generate_topology(kind, cfg, rng)
            ga_res = run_ga(critical_edges, node_costs, cfg, rng, record_trace=False)
            greedy_res = greedy_placement(cfg.n_nodes, critical_edges, node_costs, cfg.budget, cfg.penalty)
            rand_res = random_placement(cfg.n_nodes, critical_edges, node_costs, cfg.budget, cfg.penalty, rng)

            curves.append(ga_res["history"])

            if run == 0:
                sample_solutions[kind] = {
                    "graph": G,
                    "critical_edges": critical_edges,
                    "chromosome": ga_res["best_chromosome"],
                    "coverage_pct": ga_res["coverage_pct"],
                    "cost": ga_res["cost"],
                }

            all_rows.append(
                {
                    "topologia": kind,
                    "ejecucion": run + 1,
                    "semilla": run_seed,
                    "ag_aptitud": ga_res["best_fitness"],
                    "ag_cubiertos": ga_res["covered"],
                    "total_criticos": ga_res["total_critical"],
                    "ag_cobertura_pct": ga_res["coverage_pct"],
                    "ag_costo": ga_res["cost"],
                    "ag_sensores": ga_res["sensors_count"],
                    "ag_gen_convergencia": ga_res["convergence_gen"],
                    "greedy_cobertura_pct": greedy_res["coverage_pct"],
                    "greedy_costo": greedy_res["cost"],
                    "aleatorio_cobertura_pct": rand_res["coverage_pct"],
                    "aleatorio_costo": rand_res["cost"],
                }
            )

        convergence_curves[kind] = {
            "mean": np.mean(curves, axis=0),
            "std": np.std(curves, axis=0),
        }

    csv_path = os.path.join(cfg.output_dir, "resultados_experimentos.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    return all_rows, convergence_curves, sample_solutions, csv_path
