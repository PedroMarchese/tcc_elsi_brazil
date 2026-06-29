"""
Gera a Tabela 1 — Caracterização da amostra elegível, consolidada Wave 1 × Wave 2,
em formato APA 7ª edição (.xlsx).

Reutiliza a derivação de variáveis do script principal (`elsi_tcc_wave2.py`),
de modo que o N e as variáveis sejam EXATAMENTE os mesmos da análise
(W1 = 8.746; W2 = 7.205), e o estilo APA de `gerar_tabelas_apa.py`.

Saída: tables/tabelas_apa/tabela1_caracterizacao_apa.xlsx
"""

import sys
from pathlib import Path

import numpy as np
from openpyxl import Workbook

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elsi_tcc_wave2 as elsi  # noqa: E402  (pipeline de derivação)
from gerar_tabelas_apa import (  # noqa: E402  (helpers de estilo APA)
    _celula, _cabecalho, _nota, _ajustar_colunas, _ultima_linha_borda, APA_DIR,
)


# ── Formatação pt-BR ────────────────────────────────────────────────────────
def vdec(x, c=1):
    return f"{x:.{c}f}".replace(".", ",")


def vint(n):
    return f"{int(n):,}".replace(",", ".")


def vmsd(s, c=1):
    return f"{vdec(s.mean(), c)} ({vdec(s.std(), c)})"


def vnp(n, tot, c=1):
    return f"{vint(n)} ({vdec(100 * n / tot, c)})"


# ── Coleta das estatísticas de uma onda ─────────────────────────────────────
def coletar_stats(wave):
    """Roda a derivação completa da onda e devolve os valores já formatados."""
    elsi.WAVE_NUM = wave
    elsi.DATA_FILE = elsi.DATA_DIR / f"ELSI_wave_{wave}.csv"

    df = elsi.carregar_dados()
    f = elsi.derivar_marcha_e_indices(df)
    f = elsi.derivar_morbidades(f)
    f = elsi.derivar_variaveis_secundarias(f)
    g = elsi.preparar_grupos_morbidade(f)

    n = len(f)
    ec = f["escolaridade_categorizada"]
    nm = f["n_morbidades"]
    med, q1, q3 = nm.median(), nm.quantile(0.25), nm.quantile(0.75)

    d = {
        "n_eleg":  vint(n),
        "idade":   vmsd(f["idade"], 1),
        "sexo_f":  vnp((f["sexo"] == 0).sum(), n),  # 0 = feminino (ver verificação bloco M)
        "esc_1":   vnp((ec == 1).sum(), n),
        "esc_2":   vnp((ec == 2).sum(), n),
        "esc_3":   vnp((ec == 3).sum(), n),
        "esc_4":   vnp((ec == 4).sum(), n),
        "esc_9":   vnp((ec == 9).sum(), n),
        "esc_na":  vnp(ec.isna().sum(), n),
        "_esc_na_count": int(ec.isna().sum()),
        "altura":  vmsd(f["altura_cm"], 1),
        "lll":     vmsd(f["lower_limb_length"], 1),
        "ows":     vmsd(f["OWS"], 2),
        "ssws":    vmsd(f["SSWS"], 2),
        "lri":     vmsd(f["LRI"], 1),
        "nmorb_msd": vmsd(nm, 1),
        "nmorb_med": f"{med:.0f} ({q1:.0f}–{q3:.0f})",
        "multi":   vnp((nm >= 2).sum(), n),
        "g0":      vnp((g["grupo_0_neuro_oftalmo_musculoesqueleticas"] == 1).sum(), n),
        "g1":      vnp((g["grupo_1_cardiorrespiratorias"] == 1).sum(), n),
        "g2":      vnp((g["grupo_2_outras"] == 1).sum(), n),
    }
    return d


# ── Montagem das linhas da tabela ───────────────────────────────────────────
def montar_linhas(d1, d2):
    """Lista de dicts {label, w1, w2, sub}. sub=True → subcabeçalho (negrito)."""
    L = [
        {"label": "N elegível", "w1": d1["n_eleg"], "w2": d2["n_eleg"], "sub": False, "bold": True},

        {"label": "Variáveis demográficas", "sub": True},
        {"label": "Idade, anos", "w1": d1["idade"], "w2": d2["idade"]},
        {"label": "Sexo feminino", "w1": d1["sexo_f"], "w2": d2["sexo_f"]},
        {"label": "Escolaridade — fundamental incompleto ou menos (níveis 1–3)",
         "w1": d1["esc_1"], "w2": d2["esc_1"]},
        {"label": "Escolaridade — ginásio completo (nível 4)", "w1": d1["esc_2"], "w2": d2["esc_2"]},
        {"label": "Escolaridade — colegial completo (nível 5)", "w1": d1["esc_3"], "w2": d2["esc_3"]},
        {"label": "Escolaridade — superior (nível 6)", "w1": d1["esc_4"], "w2": d2["esc_4"]},
        {"label": "Escolaridade — não sabe/não respondeu (código 9)", "w1": d1["esc_9"], "w2": d2["esc_9"]},

        {"label": "Antropometria e marcha", "sub": True},
        {"label": "Altura, cm", "w1": d1["altura"], "w2": d2["altura"]},
        {"label": "Comprimento do membro inferior (LLL), cm", "w1": d1["lll"], "w2": d2["lll"]},
        {"label": "Velocidade ótima de caminhada (OWS), m/s", "w1": d1["ows"], "w2": d2["ows"]},
        {"label": "Velocidade auto-selecionada (SSWS), m/s", "w1": d1["ssws"], "w2": d2["ssws"]},
        {"label": "Índice de reabilitação locomotor (LRI), %", "w1": d1["lri"], "w2": d2["lri"]},

        {"label": "Morbidade", "sub": True},
        {"label": "N.º de morbidades — M (DP)", "w1": d1["nmorb_msd"], "w2": d2["nmorb_msd"]},
        {"label": "N.º de morbidades — Mediana (IIQ)", "w1": d1["nmorb_med"], "w2": d2["nmorb_med"]},
        {"label": "Multimorbidade (≥ 2 morbidades), n (%)", "w1": d1["multi"], "w2": d2["multi"]},
        {"label": "Grupo 0 — neuro/oftalmo/musculoesq. (≥ 1), n (%)", "w1": d1["g0"], "w2": d2["g0"]},
        {"label": "Grupo 1 — cardiorrespiratório (≥ 1), n (%)", "w1": d1["g1"], "w2": d2["g1"]},
        {"label": "Grupo 2 — outras (≥ 1), n (%)", "w1": d1["g2"], "w2": d2["g2"]},
    ]
    # Inclui a linha de escolaridade "sem informação" só se houver casos.
    if d1["_esc_na_count"] or d2["_esc_na_count"]:
        idx = next(i for i, x in enumerate(L) if x["label"].endswith("(código 9)"))
        L.insert(idx + 1, {"label": "Escolaridade — sem informação",
                           "w1": d1["esc_na"], "w2": d2["esc_na"]})
    return L


COLUNAS = ["Característica", "Wave 1 (2015–16)", "Wave 2 (2019–21)"]
LARGURAS = [52, 18, 18]

NOTA = (
    "Valores em M (DP) para variáveis contínuas e n (%) para categóricas, salvo "
    "indicação. N = amostra elegível após a derivação da marcha (exclusão por altura "
    "ausente/inválida, tempo de marcha ausente/inválido e velocidade implausível). "
    "IIQ = intervalo interquartil (P25–P75). Multimorbidade = ≥ 2 morbidades. "
    "SSWS = velocidade de marcha auto-selecionada; LRI = índice de reabilitação "
    "locomotor; OWS = velocidade ótima de caminhada; LLL = comprimento do membro "
    "inferior, estimado por 0,54 × altura. Escolaridade recategorizada de e21; os "
    "rótulos dos níveis 1–3 seguem o agrupamento do script (confirmação no codebook "
    "pendente). Sexo masculino = complemento de feminino. Análise não-ponderada "
    "(sem correção para o desenho amostral complexo do ELSI)."
)


def gerar():
    d1 = coletar_stats(1)
    d2 = coletar_stats(2)
    linhas = montar_linhas(d1, d2)
    nc = len(COLUNAS)

    wb = Workbook()
    ws = wb.active
    ws.title = "Caracterização"
    ws.sheet_view.showGridLines = False

    _celula(ws, 1, 1, "Tabela 1", bold=True)
    ws.row_dimensions[1].height = 16

    titulo = "Caracterização da Amostra Elegível, por Onda do ELSI-Brasil"
    _celula(ws, 2, 1, titulo, italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=nc)
    ws.row_dimensions[2].height = 20

    _cabecalho(ws, 3, COLUNAS)
    ws.row_dimensions[3].height = 26

    r = 4
    for ln in linhas:
        if ln.get("sub"):
            _celula(ws, r, 1, ln["label"], bold=True)
        else:
            _celula(ws, r, 1, ("    " + ln["label"]) if not ln.get("bold") else ln["label"],
                    bold=ln.get("bold", False))
            _celula(ws, r, 2, ln["w1"], bold=ln.get("bold", False), alinhamento="center")
            _celula(ws, r, 3, ln["w2"], bold=ln.get("bold", False), alinhamento="center")
        ws.row_dimensions[r].height = 14
        r += 1

    ultima = r - 1
    _ultima_linha_borda(ws, ultima, nc)
    _nota(ws, ultima + 2, NOTA, nc)
    _ajustar_colunas(ws, LARGURAS)

    caminho = APA_DIR / "tabela1_caracterizacao_apa.xlsx"
    wb.save(caminho)
    print(f"[APA] {caminho}")


if __name__ == "__main__":
    gerar()
