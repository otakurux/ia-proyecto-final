from flask import Flask, jsonify, render_template, request
import numpy as np
from config import GAConfig
from experiments import TOPOLOGIES, run_all_experiments, run_single_demo
from plots import plot_campus_placement, plot_convergence, plot_method_comparison

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    data = request.get_json(silent=True) or {}
    cfg = GAConfig(
        n_nodes=int(data.get("n_nodes", 16)),
        population_size=int(data.get("population_size", 40)),
        generations=int(data.get("generations", 50)),
        crossover_prob=float(data.get("crossover_prob", 0.85)),
        mutation_prob=float(data.get("mutation_prob", 0.03)),
        tournament_size=int(data.get("tournament_size", 3)),
        elitism=int(data.get("elitism", 2)),
        penalty=float(data.get("penalty", 10.0)),
        budget=float(data.get("budget", 110.0)),
        critical_ratio=float(data.get("critical_ratio", 0.40)),
        seed=int(data.get("seed", 42)),
    )
    topology = data.get("topology", "campus_jerarquica")
    result = run_single_demo(cfg, kind=topology)
    return jsonify(result)


@app.route("/api/benchmark", methods=["POST"])
def api_benchmark():
    data = request.get_json(silent=True) or {}
    cfg = GAConfig(
        n_nodes=int(data.get("n_nodes", 24)),
        population_size=int(data.get("population_size", 60)),
        generations=int(data.get("generations", 80)),
        budget=float(data.get("budget", 120.0)),
        runs_per_topology=int(data.get("runs_per_topology", 15)),
        seed=int(data.get("seed", 42)),
    )
    rows, convergence_curves, sample_solutions, csv_path = run_all_experiments(cfg)
    plot_convergence(convergence_curves, cfg.output_dir)
    plot_method_comparison(rows, cfg.output_dir)
    plot_campus_placement(sample_solutions["campus_jerarquica"], cfg.output_dir)

    summary = []
    for kind in TOPOLOGIES:
        subset = [r for r in rows if r["topologia"] == kind]
        summary.append(
            {
                "topologia": kind,
                "ag_cobertura_pct": round(float(np.mean([r["ag_cobertura_pct"] for r in subset])), 2),
                "ag_costo": round(float(np.mean([r["ag_costo"] for r in subset])), 2),
                "ag_convergencia": round(float(np.mean([r["ag_gen_convergencia"] for r in subset])), 1),
                "greedy_cobertura_pct": round(float(np.mean([r["greedy_cobertura_pct"] for r in subset])), 2),
                "aleatorio_cobertura_pct": round(float(np.mean([r["aleatorio_cobertura_pct"] for r in subset])), 2),
            }
        )

    return jsonify({"summary": summary, "csv_path": csv_path})


if __name__ == "__main__":
    print("Servidor web iniciado en http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
