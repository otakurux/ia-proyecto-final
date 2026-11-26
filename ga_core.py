import random
from config import GAConfig


def evaluate_chromosome(chromosome, critical_edges, node_costs, budget, penalty):
    """Calcula aptitud, enlaces críticos cubiertos y costo total del cromosoma."""
    covered = sum(1 for u, v in critical_edges if chromosome[u] or chromosome[v])
    total_cost = sum(c for gene, c in zip(chromosome, node_costs) if gene)
    excess = max(0.0, total_cost - budget)
    fitness = covered - penalty * excess
    return fitness, covered, total_cost, excess


def create_individual(n_nodes: int, rng: random.Random):
    p_on = min(0.5, 3.0 / max(1, n_nodes))
    return [1 if rng.random() < p_on else 0 for _ in range(n_nodes)]


def tournament_selection(population, fitnesses, k: int, rng: random.Random):
    aspirants = rng.sample(range(len(population)), min(k, len(population)))
    best_idx = max(aspirants, key=lambda idx: fitnesses[idx])
    return population[best_idx][:], aspirants, best_idx


def crossover(parent1, parent2, prob: float, rng: random.Random):
    if rng.random() > prob or len(parent1) < 2:
        return parent1[:], parent2[:], None
    point = rng.randint(1, len(parent1) - 1)
    return parent1[:point] + parent2[point:], parent2[:point] + parent1[point:], point


def mutate(chromosome, prob: float, rng: random.Random):
    mutated = []
    flipped_indices = []
    for idx, g in enumerate(chromosome):
        if rng.random() < prob:
            mutated.append(1 - g)
            flipped_indices.append(idx)
        else:
            mutated.append(g)
    return mutated, flipped_indices


def run_ga(critical_edges, node_costs, cfg: GAConfig, rng: random.Random, record_trace: bool = False):
    """Ejecuta el ciclo completo del algoritmo genético y opcionalmente guarda la traza paso a paso."""
    n_nodes = len(node_costs)
    population = [create_individual(n_nodes, rng) for _ in range(cfg.population_size)]
    history_best_fitness = []
    history_mean_fitness = []
    best_ever_fitness = float("-inf")
    convergence_gen = 0
    generation_traces = []

    for gen in range(cfg.generations):
        evals = [
            evaluate_chromosome(ind, critical_edges, node_costs, cfg.budget, cfg.penalty)
            for ind in population
        ]
        fitnesses = [e[0] for e in evals]

        ranked_indices = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
        best_idx_gen = ranked_indices[0]
        gen_best_fit, gen_best_cov, gen_best_cost, gen_best_excess = evals[best_idx_gen]
        gen_mean_fit = sum(fitnesses) / len(fitnesses)

        history_best_fitness.append(round(gen_best_fit, 4))
        history_mean_fitness.append(round(gen_mean_fit, 4))

        if gen_best_fit > best_ever_fitness + 1e-9:
            best_ever_fitness = gen_best_fit
            convergence_gen = gen + 1

        next_population = [population[i][:] for i in ranked_indices[: cfg.elitism]]
        sample_operator_event = None

        while len(next_population) < cfg.population_size:
            p1, asp1, win1 = tournament_selection(population, fitnesses, cfg.tournament_size, rng)
            p2, asp2, win2 = tournament_selection(population, fitnesses, cfg.tournament_size, rng)
            c1, c2, cut_point = crossover(p1, p2, cfg.crossover_prob, rng)
            c1_mut, flipped1 = mutate(c1, cfg.mutation_prob, rng)
            c2_mut, flipped2 = mutate(c2, cfg.mutation_prob, rng)

            if sample_operator_event is None:
                c1_fit, c1_cov, c1_cost, c1_exc = evaluate_chromosome(
                    c1_mut, critical_edges, node_costs, cfg.budget, cfg.penalty
                )
                sample_operator_event = {
                    "torneo_1_candidatos": asp1,
                    "torneo_1_ganador": win1,
                    "torneo_2_candidatos": asp2,
                    "torneo_2_ganador": win2,
                    "padre_1": p1,
                    "padre_2": p2,
                    "punto_cruce": cut_point,
                    "hijo_tras_cruce": c1,
                    "genes_mutados": flipped1,
                    "hijo_final": c1_mut,
                    "hijo_aptitud": round(c1_fit, 4),
                    "hijo_cubiertos": c1_cov,
                    "hijo_costo": round(c1_cost, 2),
                }

            next_population.append(c1_mut)
            if len(next_population) < cfg.population_size:
                next_population.append(c2_mut)

        if record_trace:
            generation_traces.append(
                {
                    "generacion": gen + 1,
                    "mejor_cromosoma": population[best_idx_gen][:],
                    "mejor_aptitud": round(gen_best_fit, 4),
                    "aptitud_promedio": round(gen_mean_fit, 4),
                    "enlaces_cubiertos": gen_best_cov,
                    "total_criticos": len(critical_edges),
                    "cobertura_pct": round(100.0 * gen_best_cov / max(1, len(critical_edges)), 2),
                    "costo_total": round(gen_best_cost, 2),
                    "exceso_presupuesto": round(gen_best_excess, 2),
                    "sensores_activos": sum(population[best_idx_gen]),
                    "nodos_activos": [i for i, g in enumerate(population[best_idx_gen]) if g == 1],
                    "evento_operadores": sample_operator_event,
                }
            )

        population = next_population

    final_evals = [
        evaluate_chromosome(ind, critical_edges, node_costs, cfg.budget, cfg.penalty)
        for ind in population
    ]
    best_idx = max(range(len(population)), key=lambda i: final_evals[i][0])
    best_chrom = population[best_idx]
    best_fit, best_cov, best_cost, best_excess = final_evals[best_idx]

    return {
        "best_chromosome": best_chrom,
        "best_fitness": round(best_fit, 4),
        "covered": best_cov,
        "total_critical": len(critical_edges),
        "coverage_pct": round(100.0 * best_cov / max(1, len(critical_edges)), 2),
        "cost": round(best_cost, 2),
        "excess": round(best_excess, 2),
        "sensors_count": sum(best_chrom),
        "active_nodes": [i for i, g in enumerate(best_chrom) if g == 1],
        "convergence_gen": convergence_gen,
        "history": history_best_fitness,
        "mean_history": history_mean_fitness,
        "traces": generation_traces,
    }
