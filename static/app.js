let simData = null;
let currentGenIdx = 0;
let playTimer = null;

const btnRun = document.getElementById("btn-run");
const btnBenchmark = document.getElementById("btn-benchmark");
const slider = document.getElementById("gen-slider");
const btnPrev = document.getElementById("btn-prev");
const btnNext = document.getElementById("btn-next");
const btnPlay = document.getElementById("btn-play");

function getParams() {
  return {
    topology: document.getElementById("topology").value,
    n_nodes: Number(document.getElementById("n_nodes").value),
    budget: Number(document.getElementById("budget").value),
    population_size: Number(document.getElementById("population_size").value),
    generations: Number(document.getElementById("generations").value),
    crossover_prob: Number(document.getElementById("crossover_prob").value),
    mutation_prob: Number(document.getElementById("mutation_prob").value),
    penalty: Number(document.getElementById("penalty").value),
    seed: Number(document.getElementById("seed").value),
  };
}

btnRun.addEventListener("click", async () => {
  stopPlayback();
  btnRun.disabled = true;
  btnRun.textContent = "Ejecutando simulación...";
  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getParams()),
    });
    simData = await res.json();
    renderSummary();
    currentGenIdx = 0;
    slider.max = simData.ga_result.traces.length - 1;
    slider.value = 0;
    document.getElementById("gen-max").textContent = simData.ga_result.traces.length;
    document.getElementById("summary-section").style.display = "block";
    document.getElementById("process-section").style.display = "block";
    renderGeneration(0);
  } finally {
    btnRun.disabled = false;
    btnRun.textContent = "▶ Ejecutar Ejemplo y Ver Proceso";
  }
});

btnBenchmark.addEventListener("click", async () => {
  btnBenchmark.disabled = true;
  btnBenchmark.textContent = "Ejecutando comparativa...";
  try {
    const res = await fetch("/api/benchmark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getParams()),
    });
    const data = await res.json();
    const tbody = document.getElementById("benchmark-tbody");
    tbody.innerHTML = "";
    data.summary.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${row.topologia}</strong></td>
        <td>${row.ag_cobertura_pct}%</td>
        <td>${row.ag_costo} u.</td>
        <td>Gen. ${row.ag_convergencia}</td>
        <td>${row.greedy_cobertura_pct}%</td>
        <td>${row.aleatorio_cobertura_pct}%</td>
      `;
      tbody.appendChild(tr);
    });
    document.getElementById("benchmark-msg").textContent =
      `Resultados exportados en ${data.csv_path} y gráficos PNG guardados en outputs/.`;
    document.getElementById("benchmark-section").style.display = "block";
  } finally {
    btnBenchmark.disabled = false;
    btnBenchmark.textContent = "📊 Comparar 4 Topologías (Exportar CSV/PNG)";
  }
});

slider.addEventListener("input", (e) => {
  stopPlayback();
  renderGeneration(Number(e.target.value));
});

btnPrev.addEventListener("click", () => {
  stopPlayback();
  if (simData && currentGenIdx > 0) renderGeneration(currentGenIdx - 1);
});

btnNext.addEventListener("click", () => {
  stopPlayback();
  if (simData && currentGenIdx < simData.ga_result.traces.length - 1) {
    renderGeneration(currentGenIdx + 1);
  }
});

btnPlay.addEventListener("click", () => {
  if (!simData) return;
  if (playTimer) {
    stopPlayback();
    return;
  }
  if (currentGenIdx >= simData.ga_result.traces.length - 1) {
    currentGenIdx = 0;
  }
  btnPlay.textContent = "⏸ Pausar";
  playTimer = setInterval(() => {
    if (currentGenIdx >= simData.ga_result.traces.length - 1) {
      stopPlayback();
      return;
    }
    renderGeneration(currentGenIdx + 1);
  }, 260);
});

function stopPlayback() {
  if (playTimer) {
    clearInterval(playTimer);
    playTimer = null;
  }
  btnPlay.textContent = "▶ Reproducir Evolución";
}

function renderSummary() {
  const ga = simData.ga_result;
  const cfg = simData.config;
  const gr = simData.baselines.greedy;
  const rd = simData.baselines.random;

  document.getElementById("kpi-cov").textContent = `${ga.coverage_pct}%`;
  document.getElementById("kpi-cov-detail").textContent =
    `${ga.covered} de ${ga.total_critical} enlaces críticos cubiertos`;

  document.getElementById("kpi-cost").textContent = `${ga.cost} / ${cfg.budget} u.`;
  document.getElementById("kpi-sensors").textContent = `${ga.sensors_count} sensores instalados`;

  document.getElementById("kpi-fit").textContent = `${ga.best_fitness}`;
  document.getElementById("kpi-conv").textContent = `Convergencia en generación ${ga.convergence_gen}`;

  document.getElementById("kpi-base").textContent = `${gr.coverage_pct}% / ${rd.coverage_pct}%`;
  document.getElementById("kpi-base-cost").textContent = `Costos: ${gr.cost} u. / ${rd.cost} u.`;

  const chips = document.getElementById("selected-nodes-list");
  chips.innerHTML = "";
  ga.active_nodes.forEach((nodeId) => {
    const node = simData.graph.nodes[nodeId];
    const span = document.createElement("span");
    span.className = "chip";
    span.textContent = `[${node.id}] ${node.label} (${node.cost} u.)`;
    chips.appendChild(span);
  });
}

function renderGeneration(idx) {
  currentGenIdx = idx;
  slider.value = idx;
  const trace = simData.ga_result.traces[idx];
  document.getElementById("gen-label").textContent = trace.generacion;
  document.getElementById("op-gen-num").textContent = trace.generacion;

  document.getElementById("gen-metrics-bar").innerHTML = `
    <span><strong>Mejor Aptitud:</strong> ${trace.mejor_aptitud}</span>
    <span><strong>Cobertura Crítica:</strong> ${trace.enlaces_cubiertos}/${trace.total_criticos} (${trace.cobertura_pct}%)</span>
    <span><strong>Costo Acumulado:</strong> ${trace.costo_total} u. (Presupuesto: ${simData.config.budget} u.)</span>
    <span><strong>Exceso:</strong> ${trace.exceso_presupuesto} u.</span>
    <span><strong>Sensores Activos:</strong> ${trace.sensores_activos}</span>
  `;

  // Cromosoma binario celda por celda
  const cells = document.getElementById("chromosome-cells");
  cells.innerHTML = "";
  trace.mejor_cromosoma.forEach((bit, i) => {
    const node = simData.graph.nodes[i];
    const div = document.createElement("div");
    div.className = `gene-cell ${bit === 1 ? "on" : ""}`;
    div.innerHTML = `<span class="bit">${bit}</span><span>${node.label}</span><small>${node.cost}u</small>`;
    cells.appendChild(div);
  });

  // Operadores genéticos de muestra
  const ev = trace.evento_operadores;
  if (ev) {
    document.getElementById("operators-detail").innerHTML = `
      <p><strong>Ejemplo real de operadores aplicados en esta generación:</strong></p>
      <ul>
        <li><strong>Selección por Torneo:</strong> Candidatos [${ev.torneo_1_candidatos.join(", ")}] → Ganador Padre 1 (ind. #${ev.torneo_1_ganador}); Candidatos [${ev.torneo_2_candidatos.join(", ")}] → Ganador Padre 2 (ind. #${ev.torneo_2_ganador}).</li>
        <li><strong>Cruce de 1 punto:</strong> ${ev.punto_cruce !== null ? `Corte en gen ${ev.punto_cruce}` : "Sin cruce (se conservan padres)"}<br>
            Padre 1: <code>${ev.padre_1.join("")}</code><br>
            Padre 2: <code>${ev.padre_2.join("")}</code><br>
            Hijo resultante: <code>${ev.hijo_tras_cruce.join("")}</code></li>
        <li><strong>Mutación (Bit-Flip):</strong> ${ev.genes_mutados.length > 0 ? `Genes invertidos en posiciones [${ev.genes_mutados.join(", ")}]` : "Ningún gen mutado en este individuo"} → Cromosoma hijo final: <code>${ev.hijo_final.join("")}</code> (Aptitud: <strong>${ev.hijo_aptitud}</strong>, Cobertura: ${ev.hijo_cubiertos}, Costo: ${ev.hijo_costo} u.)</li>
      </ul>
    `;
  }

  drawNetwork(trace.mejor_cromosoma);
  drawChart(idx);
}

function drawNetwork(chromosome) {
  const canvas = document.getElementById("network-canvas");
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const nodes = simData.graph.nodes;
  const edges = simData.graph.edges;

  const xs = nodes.map((n) => n.x);
  const ys = nodes.map((n) => n.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const pad = 42;

  const mapX = (x) => pad + ((x - minX) / (maxX - minX || 1)) * (w - 2 * pad);
  const mapY = (y) => pad + ((y - minY) / (maxY - minY || 1)) * (h - 2 * pad);

  // Dibujar enlaces
  edges.forEach((e) => {
    const uNode = nodes[e.u];
    const vNode = nodes[e.v];
    const isCovered = chromosome[e.u] === 1 || chromosome[e.v] === 1;

    ctx.beginPath();
    ctx.moveTo(mapX(uNode.x), mapY(uNode.y));
    ctx.lineTo(mapX(vNode.x), mapY(vNode.y));

    if (e.critical && isCovered) {
      ctx.strokeStyle = "#16a34a";
      ctx.lineWidth = 3;
    } else if (e.critical && !isCovered) {
      ctx.strokeStyle = "#dc2626";
      ctx.lineWidth = 2.5;
    } else {
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 1.2;
    }
    ctx.stroke();
  });

  // Dibujar nodos
  nodes.forEach((n) => {
    const cx = mapX(n.x);
    const cy = mapY(n.y);
    const active = chromosome[n.id] === 1;

    ctx.beginPath();
    ctx.arc(cx, cy, active ? 13 : 10, 0, Math.PI * 2);
    ctx.fillStyle = active ? "#1d4ed8" : "#e2e8f0";
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = active ? "#1e3a8a" : "#64748b";
    ctx.stroke();

    ctx.fillStyle = active ? "#ffffff" : "#0f172a";
    ctx.font = "bold 10px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(n.id), cx, cy);

    ctx.fillStyle = "#1e293b";
    ctx.font = "10px sans-serif";
    ctx.fillText(n.label, cx, cy + 19);
  });
}

function drawChart(highlightIdx) {
  const canvas = document.getElementById("chart-canvas");
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const bestHist = simData.ga_result.history;
  const meanHist = simData.ga_result.mean_history;
  const allVals = [...bestHist, ...meanHist];
  const minVal = Math.min(...allVals);
  const maxVal = Math.max(...allVals);
  const padL = 46, padR = 18, padT = 20, padB = 34;

  const mapX = (i) => padL + (i / Math.max(1, bestHist.length - 1)) * (w - padL - padR);
  const mapY = (v) => h - padB - ((v - minVal) / (maxVal - minVal || 1)) * (h - padT - padB);

  // Ejes
  ctx.strokeStyle = "#94a3b8";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padL, padT);
  ctx.lineTo(padL, h - padB);
  ctx.lineTo(w - padR, h - padB);
  ctx.stroke();

  // Etiquetas eje Y
  ctx.fillStyle = "#475569";
  ctx.font = "11px sans-serif";
  ctx.textAlign = "right";
  ctx.fillText(maxVal.toFixed(1), padL - 6, padT + 6);
  ctx.fillText(minVal.toFixed(1), padL - 6, h - padB);

  // Línea aptitud promedio
  ctx.save();
  ctx.setLineDash([4, 4]);
  ctx.strokeStyle = "#64748b";
  ctx.lineWidth = 1.6;
  ctx.beginPath();
  meanHist.forEach((v, i) => {
    if (i === 0) ctx.moveTo(mapX(i), mapY(v));
    else ctx.lineTo(mapX(i), mapY(v));
  });
  ctx.stroke();
  ctx.restore();

  // Línea mejor aptitud
  ctx.strokeStyle = "#1d4ed8";
  ctx.lineWidth = 2.4;
  ctx.beginPath();
  bestHist.forEach((v, i) => {
    if (i === 0) ctx.moveTo(mapX(i), mapY(v));
    else ctx.lineTo(mapX(i), mapY(v));
  });
  ctx.stroke();

  // Marcador generación actual
  const hx = mapX(highlightIdx);
  const hy = mapY(bestHist[highlightIdx]);
  ctx.strokeStyle = "#dc2626";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(hx, padT);
  ctx.lineTo(hx, h - padB);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(hx, hy, 5, 0, Math.PI * 2);
  ctx.fillStyle = "#dc2626";
  ctx.fill();
}
