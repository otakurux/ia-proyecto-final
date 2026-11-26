import os
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def plot_convergence(convergence_curves: dict, output_dir: str):
    plt.figure(figsize=(8.5, 5))
    for kind, stats in convergence_curves.items():
        mean = stats["mean"]
        std = stats["std"]
        gens = np.arange(1, len(mean) + 1)
        plt.plot(gens, mean, linewidth=2, label=kind)
        plt.fill_between(gens, mean - std, mean + std, alpha=0.15)

    plt.title("Convergencia de aptitud por topología (media ± desv. estándar)")
    plt.xlabel("Generación")
    plt.ylabel("Mejor aptitud")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "convergencia_topologias.png"), dpi=200)
    plt.close()


def plot_method_comparison(rows: list, output_dir: str):
    topologies = list(dict.fromkeys(r["topologia"] for r in rows))
    ag_means = [np.mean([r["ag_cobertura_pct"] for r in rows if r["topologia"] == t]) for t in topologies]
    greedy_means = [np.mean([r["greedy_cobertura_pct"] for r in rows if r["topologia"] == t]) for t in topologies]
    rand_means = [np.mean([r["aleatorio_cobertura_pct"] for r in rows if r["topologia"] == t]) for t in topologies]

    x = np.arange(len(topologies))
    width = 0.25

    plt.figure(figsize=(9, 5))
    plt.bar(x - width, ag_means, width, label="Algoritmo Genético")
    plt.bar(x, greedy_means, width, label="Heurística Greedy")
    plt.bar(x + width, rand_means, width, label="Búsqueda Aleatoria")

    plt.xticks(x, topologies)
    plt.ylabel("Cobertura promedio de enlaces críticos (%)")
    plt.title("Comparativa de cobertura: AG vs. Greedy vs. Aleatorio")
    plt.ylim(0, 105)
    plt.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "comparativa_metodos.png"), dpi=200)
    plt.close()


def plot_campus_placement(sample_campus: dict, output_dir: str):
    G = sample_campus["graph"]
    critical_set = {tuple(sorted(e)) for e in sample_campus["critical_edges"]}
    chrom = sample_campus["chromosome"]

    pos = nx.spring_layout(G, seed=42)
    node_colors = ["#1d4ed8" if chrom[n] == 1 else "#e2e8f0" for n in G.nodes()]
    edge_colors = ["#dc2626" if tuple(sorted(e)) in critical_set else "#94a3b8" for e in G.edges()]
    edge_widths = [2.4 if tuple(sorted(e)) in critical_set else 1.0 for e in G.edges()]

    plt.figure(figsize=(8.5, 6))
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, alpha=0.85)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, edgecolors="#1e293b", node_size=420)
    nx.draw_networkx_labels(G, pos, font_size=8, font_color="#0f172a")

    plt.title(
        f"Ubicación IDS/IPS en Campus | Cobertura: {sample_campus['coverage_pct']:.1f}% | "
        f"Costo: {sample_campus['cost']:.2f} u."
    )
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ubicacion_campus.png"), dpi=200)
    plt.close()
