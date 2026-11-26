# Prototipo Web y Experimental: Ubicación de Sensores IDS/IPS con Algoritmos Genéticos

Aplicación en Python con interfaz web HTML/CSS/JS para visualizar paso a paso cómo un Algoritmo Genético (AG) determina la ubicación óptima de sensores IDS/IPS en redes de campus universitario y topologías de referencia, maximizando la cobertura de enlaces críticos dentro de un presupuesto definido.

## Estructura de carpetas y archivos

```text
ids_ips_ga_campus_web/
├── app.py                  # Servidor web Flask que conecta el AG con la interfaz HTML
├── config.py               # Parámetros del AG, costos, presupuesto y semillas
├── topologies.py           # Generadores de topologías (Campus, Libre de Escala, Mundo Pequeño, Aleatoria)
├── ga_core.py              # Algoritmo Genético con traza detallada por generación (torneo, cruce, mutación)
├── baselines.py            # Heurística Greedy y Búsqueda Aleatoria para comparación
├── experiments.py          # Simulación individual detallada y experimentos multi-semilla
├── plots.py                # Generación de gráficos estáticos PNG para informes
├── main.py                 # Ejecución directa por consola sin interfaz web
├── requirements.txt        # Dependencias Python
├── README.md               # Instrucciones de uso
├── templates/
│   └── index.html          # Interfaz web simple y funcional
├── static/
│   ├── style.css           # Estilos de la interfaz
│   └── app.js              # Renderizado interactivo del grafo, cromosoma, operadores y convergencia
└── outputs/                # Carpeta donde se guardan resultados CSV y gráficos PNG
```

## Cómo ejecutar la interfaz web

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Iniciar el servidor web:
   ```bash
   python app.py
   ```
3. Abrir en el navegador:
   ```text
   http://127.0.0.1:5000
   ```

## Qué muestra la interfaz

1. **Resultado final y comparación:** porcentaje de enlaces críticos cubiertos, costo acumulado frente al presupuesto $B$, nodos seleccionados (`gen = 1`) y comparación contra Greedy y Búsqueda Aleatoria.
2. **Proceso paso a paso (Generación 1 a N):**
   - Control deslizante y botón *Reproducir Evolución*.
   - **Grafo de red en tiempo real:** muestra qué nodos activan sensor en cada generación y qué enlaces críticos pasan de rojo (sin cubrir) a verde (cubiertos).
   - **Cromosoma binario celda por celda:** visualización de cada gen (`0` o `1`), nombre del nodo (Core, Facultades, Data Center, Labs) y costo.
   - **Operadores genéticos reales:** selección por torneo, punto de cruce entre padres y bits mutados en esa generación.
   - **Curva de convergencia:** evolución de la mejor aptitud y de la aptitud promedio.
