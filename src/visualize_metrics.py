"""Gera os graficos das RQ03, RQ04, RQ05 e RQ06 (Sprint 3).

Uso:
    python src/analyze_metrics.py                 # gera resultados/resultados_metricas_1000.json
    python src/visualize_metrics.py                # gera os PNGs a partir desse JSON

Cada grafico corresponde a uma Questao de Pesquisa e usa o tipo recomendado no
enunciado/relatorio: barras (ranking) para releases e linguagem, histograma
para tempo desde a ultima atualizacao, e barra unica 100% para % de issues
fechadas.
"""

import csv
import json
import os
import statistics
import sys
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "resultados", "resultados_metricas_1000.json")
REPOS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "repositorios_lab01_s02.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "resultados", "graficos")

COR_PRINCIPAL = "#2E5266"
COR_DESTAQUE = "#6CC24A"


def _save(fig, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Grafico salvo em {path}")


def _load_repos(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plot_rq01_idade(repos):
    now = datetime.now(timezone.utc)
    idades_anos = [
        (now - datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))).days / 365
        for r in repos
    ]
    mediana = statistics.median(idades_anos)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(idades_anos, bins=20, color=COR_PRINCIPAL)
    ax.axvline(mediana, color=COR_DESTAQUE, linestyle="--", label=f"Mediana: {mediana:.1f} anos")
    ax.set_title("RQ01 - Sistemas populares sao maduros/antigos?")
    ax.set_xlabel("Idade do repositorio (anos)")
    ax.set_ylabel("Quantidade de repositorios")
    ax.legend()
    _save(fig, "rq01_idade.png")


def plot_rq02_prs(repos):
    prs = [int(r["pull_requests_merged_total"]) for r in repos]
    sem_prs = sum(1 for p in prs if p == 0)
    prs_positivos = [p for p in prs if p > 0]
    mediana = statistics.median(prs)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(prs_positivos, bins=30, color=COR_PRINCIPAL)
    ax.set_xscale("log")
    ax.axvline(mediana, color=COR_DESTAQUE, linestyle="--", label=f"Mediana: {mediana:.0f} PRs")
    ax.set_title("RQ02 - Sistemas populares recebem muita contribuicao externa?")
    ax.set_xlabel("Pull requests aceitas (escala log)")
    ax.set_ylabel("Quantidade de repositorios")
    ax.legend(title=f"{sem_prs} repositorios com 0 PRs aceitas nao\nentram no histograma (escala log)")
    _save(fig, "rq02_prs_aceitas.png")


def plot_rq07_por_linguagem(metrics, min_repos=10):
    por_lang = {
        lang: dados
        for lang, dados in metrics["RQ07_por_linguagem"].items()
        if dados["quantidade_repos"] >= min_repos
    }

    fig, ax = plt.subplots(figsize=(9, 6))
    for i, (lang, dados) in enumerate(por_lang.items()):
        ax.scatter(
            dados["mediana_releases"],
            dados["mediana_prs_aceitas"],
            s=dados["quantidade_repos"] * 2,
            color=COR_PRINCIPAL,
            alpha=0.7,
        )
        offset_y = 10 if i % 2 == 0 else -14
        ax.annotate(lang, (dados["mediana_releases"], dados["mediana_prs_aceitas"]), fontsize=8,
                    xytext=(6, offset_y), textcoords="offset points")

    ax.set_title("RQ07 - Releases vs. PRs aceitas, por linguagem (mediana)")
    ax.set_xlabel("Mediana de releases")
    ax.set_ylabel("Mediana de PRs aceitas")
    _save(fig, "rq07_releases_vs_prs.png")


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


def main(metrics_path, repos_path):
    with open(metrics_path, encoding="utf-8") as f:
        metrics = json.load(f)
    repos = _load_repos(repos_path)

    plot_rq01_idade(repos)
    plot_rq02_prs(repos)
    plot_rq03_releases(metrics)
    plot_rq04_atualizacao(metrics)
    plot_rq05_linguagem(metrics)
    plot_rq06_issues_fechadas(metrics)
    plot_rq07_por_linguagem(metrics)


if __name__ == "__main__":
    main(
        sys.argv[1] if len(sys.argv) > 1 else METRICS_PATH,
        sys.argv[2] if len(sys.argv) > 2 else REPOS_PATH,
    )
