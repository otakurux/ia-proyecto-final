import numpy as np
from config import GAConfig
from experiments import TOPOLOGIES, run_all_experiments
from plots import plot_campus_placement, plot_convergence, plot_method_comparison


def main():
    cfg = GAConfig()
    rows, convergence_curves, sample_solutions, csv_path = run_all_experiments(cfg)

    print("=== RESUMEN DE RESULTADOS EXPERIMENTALES ===")
    for kind in TOPOLOGIES:
        subset = [r for r in rows if r["topologia"] == kind]
        ag_cov = np.mean([r["ag_cobertura_pct"] for r in subset])
        gr_cov = np.mean([r["greedy_cobertura_pct"] for r in subset])
        rd_cov = np.mean([r["aleatorio_cobertura_pct"] for r in subset])
        ag_cost = np.mean([r["ag_costo"] for r in subset])
        ag_conv = np.mean([r["ag_gen_convergencia"] for r in subset])

        print(
            f"{kind:18s} | AG: {ag_cov:5.1f}% (Costo: {ag_cost:6.2f}, Conv. gen: {ag_conv:4.1f}) "
            f"| Greedy: {gr_cov:5.1f}% | Aleatorio: {rd_cov:5.1f}%"
        )

    plot_convergence(convergence_curves, cfg.output_dir)
    plot_method_comparison(rows, cfg.output_dir)
    plot_campus_placement(sample_solutions["campus_jerarquica"], cfg.output_dir)

    print(f"\nCSV exportado en: {csv_path}")
    print(f"Gráficos guardados en la carpeta: {cfg.output_dir}/")


if __name__ == "__main__":
    main()
