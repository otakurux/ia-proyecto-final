import random
from ga_core import evaluate_chromosome


def greedy_placement(n_nodes: int, critical_edges, node_costs, budget: float, penalty: float):
    """Selecciona nodos iterativamente por mayor ganancia de enlaces críticos por unidad de costo."""
    chromosome = [0] * n_nodes
    uncovered = set(tuple(sorted(e)) for e in critical_edges)
    current_cost = 0.0

    while uncovered:
        best_node = None
        best_ratio = 0.0

        for node in range(n_nodes):
            if chromosome[node] == 1:
                continue
            if current_cost + node_costs[node] > budget:
                continue

            gain = sum(1 for u, v in uncovered if u == node or v == node)
            if gain > 0:
                ratio = gain / node_costs[node]
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_node = node

        if best_node is None:
            break

        chromosome[best_node] = 1
        current_cost += node_costs[best_node]
        uncovered = {e for e in uncovered if best_node not in e}

    fit, cov, cost, _ = evaluate_chromosome(chromosome, critical_edges, node_costs, budget, penalty)
    return {
        "chromosome": chromosome,
        "fitness": round(fit, 4),
        "covered": cov,
        "coverage_pct": round(100.0 * cov / max(1, len(critical_edges)), 2),
        "cost": round(cost, 2),
        "sensors_count": sum(chromosome),
        "active_nodes": [i for i, g in enumerate(chromosome) if g == 1],
    }


def random_placement(
    n_nodes: int, critical_edges, node_costs, budget: float, penalty: float, rng: random.Random, samples: int = 200
):
    """Evalúa muestras aleatorias factibles y devuelve la mejor encontrada."""
    best_res = None

    for _ in range(samples):
        order = list(range(n_nodes))
        rng.shuffle(order)
        chromosome = [0] * n_nodes
        current_cost = 0.0

        for node in order:
            if current_cost + node_costs[node] <= budget:
                chromosome[node] = 1
                current_cost += node_costs[node]

        fit, cov, cost, _ = evaluate_chromosome(chromosome, critical_edges, node_costs, budget, penalty)
        if best_res is None or fit > best_res["fitness"]:
            best_res = {
                "chromosome": chromosome,
                "fitness": round(fit, 4),
                "covered": cov,
                "coverage_pct": round(100.0 * cov / max(1, len(critical_edges)), 2),
                "cost": round(cost, 2),
                "sensors_count": sum(chromosome),
                "active_nodes": [i for i, g in enumerate(chromosome) if g == 1],
            }

    return best_res
