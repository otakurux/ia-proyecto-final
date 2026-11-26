import random
import networkx as nx
import numpy as np
from config import GAConfig


def build_campus_hierarchy(n_nodes: int, rng: random.Random) -> nx.Graph:
    """Topología jerárquica inspirada en campus (Core -> Facultades/Distribución -> Labs/Servicios)."""
    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))
    if n_nodes < 4:
        for i in range(n_nodes - 1):
            G.add_edge(i, i + 1)
        return G

    core = 0
    n_dist = max(2, n_nodes // 4)
    dist_nodes = list(range(1, 1 + n_dist))
    access_nodes = list(range(1 + n_dist, n_nodes))

    for d in dist_nodes:
        G.add_edge(core, d)

    for idx, acc in enumerate(access_nodes):
        primary_d = dist_nodes[idx % len(dist_nodes)]
        G.add_edge(primary_d, acc)
        if len(dist_nodes) > 1 and rng.random() < 0.25:
            secondary_d = dist_nodes[(idx + 1) % len(dist_nodes)]
            G.add_edge(secondary_d, acc)

    for i in range(len(access_nodes) - 1):
        if rng.random() < 0.35:
            G.add_edge(access_nodes[i], access_nodes[i + 1])

    return G


def get_campus_node_labels(n_nodes: int, kind: str) -> dict:
    """Devuelve nombres descriptivos para los nodos de la red."""
    if kind != "campus_jerarquica":
        return {i: f"N{i}" for i in range(n_nodes)}

    labels = {0: "Core Central"}
    n_dist = max(2, n_nodes // 4)
    dist_names = [
        "Dist. Cs. Puras",
        "Dist. Ingeniería",
        "Dist. Admin/RRHH",
        "Dist. Medicina",
        "Dist. Derecho",
        "Dist. Humanidades",
    ]
    access_names = [
        "Sis. Académico",
        "Data Center",
        "Lab. Redes",
        "Lab. IA",
        "Biblioteca",
        "Serv. Web/Portal",
        "Finanzas/Kardex",
        "Lab. Física",
        "Lab. Química",
        "DNS/Proxy Campus",
        "VPN/Remoto",
        "Serv. Correo",
    ]

    for idx in range(n_dist):
        node_id = 1 + idx
        if node_id < n_nodes:
            labels[node_id] = dist_names[idx] if idx < len(dist_names) else f"Dist. Fac. {idx + 1}"

    for idx, node_id in enumerate(range(1 + n_dist, n_nodes)):
        labels[node_id] = access_names[idx] if idx < len(access_names) else f"Subred {idx + 1}"

    return labels


def generate_topology(kind: str, cfg: GAConfig, rng: random.Random):
    """Genera el grafo G, la lista de enlaces críticos C, costos c(v) y etiquetas."""
    np_rng = np.random.default_rng(rng.randint(0, 10**9))

    if kind == "aleatoria":
        G = nx.erdos_renyi_graph(cfg.n_nodes, p=0.14, seed=int(np_rng.integers(0, 10**9)))
    elif kind == "libre_escala":
        G = nx.barabasi_albert_graph(cfg.n_nodes, m=2, seed=int(np_rng.integers(0, 10**9)))
    elif kind == "mundo_pequeno":
        k = min(4, cfg.n_nodes - 1 if cfg.n_nodes % 2 == 1 else cfg.n_nodes - 2)
        k = max(2, k)
        G = nx.watts_strogatz_graph(cfg.n_nodes, k=k, p=0.25, seed=int(np_rng.integers(0, 10**9)))
    elif kind == "campus_jerarquica":
        G = build_campus_hierarchy(cfg.n_nodes, rng)
    else:
        raise ValueError(f"Topología no soportada: {kind}")

    if not nx.is_connected(G):
        comps = list(nx.connected_components(G))
        for i in range(len(comps) - 1):
            u = next(iter(comps[i]))
            v = next(iter(comps[i + 1]))
            G.add_edge(u, v)

    edges = list(G.edges())
    n_critical = max(1, int(round(len(edges) * cfg.critical_ratio)))
    critical_edges = rng.sample(edges, min(n_critical, len(edges)))
    node_costs = [round(rng.uniform(cfg.cost_min, cfg.cost_max), 2) for _ in range(cfg.n_nodes)]
    node_labels = get_campus_node_labels(cfg.n_nodes, kind)

    return G, critical_edges, node_costs, node_labels
