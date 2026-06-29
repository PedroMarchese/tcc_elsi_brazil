"""
Gera o fluxograma de elegibilidade (Figura 1) — do N bruto de cada onda até a
amostra elegível após a derivação da marcha.

Reconstrói a contagem de cada etapa de exclusão replicando EXATAMENTE os filtros
de `derivar_marcha_e_indices` (script principal) e faz tie-out com o N final
autoritativo (assert), garantindo fidelidade (W1 = 8.746; W2 = 7.205).

Saídas em images/:
  - fluxograma_elegibilidade.png        (painel duplo Wave 1 | Wave 2 — Figura 1)
  - fluxograma_elegibilidade_w1.png      (painel único Wave 1)
  - fluxograma_elegibilidade_w2.png      (painel único Wave 2)
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elsi_tcc_wave2 as elsi  # noqa: E402


def fmt(n):
    return f"{int(n):,}".replace(",", ".")


# ── Contagem das etapas (réplica fiel do pipeline + tie-out) ─────────────────
def contar_etapas(wave):
    elsi.WAVE_NUM = wave
    elsi.DATA_FILE = elsi.DATA_DIR / f"ELSI_wave_{wave}.csv"
    df = elsi.carregar_dados()
    n0 = len(df)

    if wave == 2:
        mask_altura = ~df["mf13"].isin([888, 999])
    else:
        mask_altura = df["mf13"] != elsi.SENTINELA_ALTURA_W1
    f = df[mask_altura].copy()
    n1 = len(f)

    if wave == 2:
        f["altura_cm"] = f["mf13"]
        f["SSWS"] = elsi._ssws_wave2(f)
    else:
        f["altura_cm"] = f["mf13"] * 100
        f["SSWS"] = elsi._ssws_wave1(f)
    n_marcha = int(f["SSWS"].notna().sum())

    lll = elsi.get_lll(f["altura_cm"])
    f["MAX"] = np.sqrt(elsi.FR_RUNNING * elsi.G * (lll / 100))
    n_final = int((f["SSWS"] <= f["MAX"]).sum())

    # Tie-out com o N autoritativo do pipeline.
    autoritativo = len(elsi.derivar_marcha_e_indices(df))
    assert n_final == autoritativo, f"wave {wave}: {n_final} != {autoritativo}"

    return {
        "wave": wave, "n0": n0, "n1": n1, "n_marcha": n_marcha, "n_final": n_final,
        "excl_altura": n0 - n1, "excl_marcha": n1 - n_marcha,
        "excl_impl": n_marcha - n_final,
    }


# ── Desenho de um painel (uma onda) ─────────────────────────────────────────
def _caixa(ax, x, y, texto, face, edge, bold=False, fontsize=9.5):
    ax.text(x, y, texto, ha="center", va="center", fontsize=fontsize,
            color="#2B2B2B", fontweight="bold" if bold else "normal",
            bbox=dict(boxstyle="round,pad=0.6", facecolor=face, edgecolor=edge,
                      linewidth=1.4))


def _seta_baixo(ax, x, y0, y1):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="-|>", color=elsi.COR_PRIMARIA, lw=1.6))


def _seta_lado(ax, x0, x1, y):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", color=elsi.COR_CINZA, lw=1.3,
                                linestyle=(0, (4, 2))))


def desenhar_painel(ax, s, titulo):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(titulo, fontsize=12, fontweight="semibold", color="#2B2B2B", pad=6)

    xm, xe = 0.30, 0.77                      # x dos boxes principais / de exclusão
    y_tot, y_alt, y_mar, y_fin = 0.90, 0.64, 0.38, 0.11
    e1, e2, e3 = 0.77, 0.51, 0.25            # y dos boxes de exclusão
    half = 0.075                              # meia-altura aprox. do box principal

    branco, primaria = "white", elsi.COR_PRIMARIA
    excl_face, excl_edge = "#F0F1F3", elsi.COR_CINZA
    fin_face, fin_edge = "#E3ECE8", elsi.COR_VERDE

    # Boxes principais
    _caixa(ax, xm, y_tot, f"Registros na Wave {s['wave']}\n(N = {fmt(s['n0'])})", branco, primaria)
    _caixa(ax, xm, y_alt, f"Com altura válida\n(N = {fmt(s['n1'])})", branco, primaria)
    _caixa(ax, xm, y_mar, f"Com marcha válida\n(N = {fmt(s['n_marcha'])})", branco, primaria)
    _caixa(ax, xm, y_fin, f"Amostra elegível\n(N = {fmt(s['n_final'])})", fin_face, fin_edge, bold=True)

    # Boxes de exclusão
    _caixa(ax, xe, e1, f"Excluídos — altura\nausente/inválida\n(n = {fmt(s['excl_altura'])})",
           excl_face, excl_edge, fontsize=8.8)
    _caixa(ax, xe, e2, f"Excluídos — tempo de marcha\nausente/inválido\n(n = {fmt(s['excl_marcha'])})",
           excl_face, excl_edge, fontsize=8.8)
    _caixa(ax, xe, e3, f"Excluídos — SSWS acima do\nmáximo plausível\n(n = {fmt(s['excl_impl'])})",
           excl_face, excl_edge, fontsize=8.8)

    # Setas verticais (caminho principal)
    _seta_baixo(ax, xm, y_tot - half, y_alt + half)
    _seta_baixo(ax, xm, y_alt - half, y_mar + half)
    _seta_baixo(ax, xm, y_mar - half, y_fin + half)

    # Setas laterais (exclusões)
    _seta_lado(ax, xm, 0.56, e1)
    _seta_lado(ax, xm, 0.56, e2)
    _seta_lado(ax, xm, 0.56, e3)


def gerar():
    s1 = contar_etapas(1)
    s2 = contar_etapas(2)
    elsi.configurar_estilo()

    # Painel duplo (Figura 1)
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    desenhar_painel(axes[0], s1, "Wave 1 (2015–2016)")
    desenhar_painel(axes[1], s2, "Wave 2 (2019–2021)")
    fig.suptitle("Fluxograma de seleção da amostra (derivação da marcha)",
                 fontsize=14, fontweight="semibold", color="#2B2B2B", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = elsi.IMAGES_DIR / "fluxograma_elegibilidade.png"
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[figura] {p.name}")

    # Painéis individuais
    for s, tit in ((s1, "Wave 1 (2015–2016)"), (s2, "Wave 2 (2019–2021)")):
        fig, ax = plt.subplots(figsize=(7.5, 8))
        desenhar_painel(ax, s, tit)
        fig.tight_layout()
        p = elsi.IMAGES_DIR / f"fluxograma_elegibilidade_w{s['wave']}.png"
        fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[figura] {p.name}")

    print("\nContagens:")
    for s in (s1, s2):
        print(f"  Wave {s['wave']}: N0={s['n0']}  altura->{s['n1']} "
              f"(-{s['excl_altura']})  marcha->{s['n_marcha']} (-{s['excl_marcha']})  "
              f"elegivel->{s['n_final']} (-{s['excl_impl']})")


if __name__ == "__main__":
    gerar()
