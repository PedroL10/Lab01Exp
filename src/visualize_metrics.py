"""Gera os graficos das RQ03, RQ04, RQ05 e RQ06 (Sprint 3).

Uso:
    python src/analyze_metrics.py                 # gera resultados/resultados_metricas_1000.json
    python src/visualize_metrics.py                # gera os PNGs a partir desse JSON

Cada grafico corresponde a uma Questao de Pesquisa e usa o tipo recomendado no
enunciado/relatorio: barras (ranking) para releases e linguagem, histograma
para tempo desde a ultima atualizacao, e barra unica 100% para % de issues
fechadas.
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "resultados", "resultados_metricas_1000.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "resultados", "graficos")

COR_PRINCIPAL = "#2E5266"
COR_DESTAQUE = "#6CC24A"


def _save(fig, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Grafico salvo em {path}")


def plot_rq03_releases(metrics):
    rq03 = metrics["RQ03_releases"]
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Mediana", "Media", "Sem release (%)"]
    valores = [rq03["mediana"], rq03["media"], rq03["sem_release_percentual"]]
    ax.bar(labels, valores, color=[COR_PRINCIPAL, COR_PRINCIPAL, COR_DESTAQUE])
    ax.set_title("RQ03 - Sistemas populares lancam releases com frequencia?")
    ax.set_ylabel("Total de releases / percentual (%)")
    for i, v in enumerate(valores):
        ax.text(i, v, str(v), ha="center", va="bottom")
    _save(fig, "rq03_releases.png")


def plot_rq04_atualizacao(metrics):
    rq04 = metrics["RQ04_atualizacao"]
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Mediana", "Media"]
    valores = [rq04["mediana_dias"], rq04["media_dias"]]
    ax.bar(labels, valores, color=COR_PRINCIPAL)
    ax.set_title("RQ04 - Sistemas populares sao atualizados com frequencia?")
    ax.set_ylabel("Dias desde o ultimo push")
    for i, v in enumerate(valores):
        ax.text(i, v, str(v), ha="center", va="bottom")
    _save(fig, "rq04_atualizacao.png")


def plot_rq05_linguagem(metrics):
    distribuicao = metrics["RQ05_linguagem"]["distribuicao_top10"]
    linguagens = [d["linguagem"] for d in distribuicao][::-1]
    quantidades = [d["quantidade"] for d in distribuicao][::-1]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(linguagens, quantidades, color=COR_PRINCIPAL)
    ax.set_title("RQ05 - Linguagens primarias mais usadas (top 10)")
    ax.set_xlabel("Quantidade de repositorios")
    for i, v in enumerate(quantidades):
        ax.text(v, i, f" {v}", va="center")
    _save(fig, "rq05_linguagem.png")


def plot_rq06_issues_fechadas(metrics):
    rq06 = metrics["RQ06_issues_fechadas"]
    mediana = rq06["mediana_percentual"]

    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.barh(["% issues fechadas"], [100], color="#DDDDDD")
    ax.barh(["% issues fechadas"], [mediana], color=COR_DESTAQUE)
    ax.set_xlim(0, 100)
    ax.set_title("RQ06 - Sistemas populares possuem alto % de issues fechadas?")
    ax.set_xlabel("Percentual de issues fechadas (mediana por repositorio)")
    ax.text(mediana, 0, f" {mediana}%", va="center")
    _save(fig, "rq06_issues_fechadas.png")


def main(metrics_path):
    with open(metrics_path, encoding="utf-8") as f:
        metrics = json.load(f)

    plot_rq03_releases(metrics)
    plot_rq04_atualizacao(metrics)
    plot_rq05_linguagem(metrics)
    plot_rq06_issues_fechadas(metrics)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else METRICS_PATH)
