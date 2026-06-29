# -*- coding: utf-8 -*-
"""
Análise estatística — TCC ELSI (Waves 1 e 2)
============================================

Investiga a associação entre velocidade de marcha auto-selecionada (SSWS) e o
Índice de Reabilitação Locomotora (LRI) com multimorbidade em idosos do
ELSI-Brasil. A MESMA análise é rodada para as DUAS ondas (waves 1 e 2); as
saídas recebem um sufixo `_w1` / `_w2` para distinguir cada onda.

Diferenças entre as ondas tratadas pelo código:

  * SSWS (teste de marcha de 3 m):
      - Wave 2: o banco traz o tempo já em segundos (`mf35s`, `mf38s`);
      - Wave 1: NÃO há variável em segundos — o tempo é decomposto em minutos
        (`mf33`/`mf36`), segundos (`mf34`/`mf37`) e centésimos (`mf35`/`mf38`);
        reconstrói-se o tempo total em segundos e daí a velocidade.
  * Altura (`mf13`): Wave 2 em centímetros; Wave 1 em metros. O código normaliza
    ambas para centímetros antes de derivar o comprimento do membro inferior.
  * `l10_2` (tempo de atividade física) só existe na Wave 2 — ausência tratada.

Refatorado a partir do notebook original do Colab (mantido em
`elsi_tcc_wave2_colab_original.py`). As fórmulas e os filtros estatísticos foram
preservados; o que mudou foi a organização:

  * lê os dados localmente de `banco_elsi/ELSI_wave_{1,2}.csv`;
  * salva TODAS as figuras em `images/` (com sufixo da onda);
  * salva TODAS as tabelas/resultados em `tables/` (com sufixo da onda);
  * remove código específico do Colab (`drive.mount`, `display`) e duplicações.

Documentação das variáveis: ver `VARIAVEIS.md` (raiz do projeto).

Como rodar:
    python codigos/elsi_tcc_wave2.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # backend sem janela: apenas salva as figuras em arquivo

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

from scipy import constants, stats
from sklearn.metrics import roc_curve, auc, roc_auc_score


# =========================================================
# 1. CONFIGURAÇÃO — CAMINHOS E CONSTANTES
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent          # .../tcc_elsi/codigos
PROJECT_DIR = SCRIPT_DIR.parent                        # .../tcc_elsi
DATA_DIR = PROJECT_DIR / "banco_elsi"
IMAGES_DIR = PROJECT_DIR / "images"
TABLES_DIR = PROJECT_DIR / "tables"

# ---- Paleta e identidade visual dos gráficos (sóbria, p/ uso acadêmico) -----
COR_PRIMARIA = "#3C4A5A"     # ardósia escura — barras / distribuições
COR_SECUNDARIA = "#9AA7B4"   # cinza-azulado claro — nuvens de pontos
COR_DESTAQUE = "#7B3030"     # vinho discreto — média / reta de regressão
COR_REALCE = "#566573"       # cinza-ardósia — mediana / marcadores de referência
COR_CINZA = "#6B7280"        # cinza neutro — texto auxiliar e diagonais
COR_VERDE = "#42685C"        # verde acinzentado
PALETA_SEQUENCIAL = "crest"  # gradiente sóbrio (azul-esverdeado) p/ faixas (ROC)

# Ondas a analisar. A mesma análise roda para cada uma; as saídas ganham sufixo.
WAVES = [1, 2]

# Onda corrente do processamento (reatribuída a cada iteração em rodar_wave).
# Define o sufixo `_w{WAVE_NUM}` aplicado a todas as figuras e tabelas.
WAVE_NUM = 2
DATA_FILE = DATA_DIR / f"ELSI_wave_{WAVE_NUM}.csv"

# Códigos-sentinela (ausência) dos componentes de tempo da marcha na Wave 1
# (minutos/segundos/centésimos): 8888/9888 = não se aplica, 9666 = não realizou,
# 9999 = NS/NR. Sentinela da altura (mf13) na Wave 1: 99999.
SENTINELAS_TEMPO_W1 = [8888, 9666, 9888, 9999]
SENTINELA_ALTURA_W1 = 99999

# Constantes físicas / parâmetros do estudo
G = constants.g           # aceleração da gravidade (CODATA, ~9.80665 m/s²)
FR_WALKING = 0.25         # número de Froude para caminhada (velocidade ótima)
FR_RUNNING = 0.5          # número de Froude limite (velocidade máxima / cutoff)
LLL_RATIO = 0.54          # fração da altura que estima o comprimento do membro inferior

# Códigos individuais de doenças crônicas do ELSI (21 condições).
ELSI_DISEASE_CODES = {
    "HAS": "n28",
    "BACK_PROBLEM": "n58",
    "DISLIPIDEMIA": "n44",
    "CATARATA": "n12",
    "ARTRITE_OU_REUMATISMO": "n56",
    "DEPRESSAO": "n59",
    "DIABETES_MELLITUS": "n35",
    "OSTEOPOROSE": "n57",
    "INFARTO_DO_MIOCARDIO": "n46",
    "ANGINA_DO_PEITO": "n48",
    "INSUFICIENCIA_CARDIACA": "n50",
    "GLAUCOMA": "n9",
    "ENFISEMA_BRONQUITE_DPOC": "n55",
    "AVC_DERRAME": "n52",
    "CANCER": "n60",
    "ASMA": "n54",
    "INSUFICIENCIA_RENAL_CRONICA": "n61",
    "RETINOPATIA_DIABETICA": "n10",
    "DEGENERACAO_MACULAR": "n11",
    "DOENCA_DE_PARKINSON": "n62",
    "DOENCA_DE_ALZHEIMER_OU_DEMENCIA": "n63",
}
MULTIMORBIDADES_KEYS = sorted(ELSI_DISEASE_CODES.values())

# Grupos de doenças para estratificação.
GRUPO_0 = {  # neuro / oftalmo / musculoesqueléticas
    "n9": "glaucoma",
    "n10": "retinopatia_diabetica",
    "n11": "degeneracao_macular",
    "n12": "catarata",
    "n52": "avc_derrame",
    "n56": "artrite_reumatismo",
    "n57": "osteoporose",
    "n58": "problema_cronico_coluna",
    "n62": "doenca_parkinson",
    "n63": "doenca_alzheimer_ou_demencia",
}
GRUPO_1 = {  # cardiorrespiratórias
    "n28": "hipertensao_arterial",
    "n46": "infarto_miocardio",
    "n48": "angina_peito",
    "n50": "insuficiencia_cardiaca",
    "n54": "asma",
    "n55": "dpoc_bronquite_enfisema",
}
GRUPO_2 = {  # outras
    "n35": "diabetes_mellitus",
    "n44": "dislipidemia",
    "n59": "depressao",
    "n60": "cancer",
    "n61": "insuficiencia_renal_cronica",
}

# Indicadores binários de contagem de morbidades.
MORBIDADE_COLS = [
    "morbidades_menor_que_2",
    "morbidades_igual_a_2",
    "morbidades_igual_a_3",
    "morbidades_igual_a_4",
    "morbidades_igual_a_5",
    "morbidades_igual_a_6",
    "morbidades_maior_ou_igual_a_7",
]

# Coleta os resumos de modelos (.summary()) para gravar num único arquivo de texto.
_RESUMOS = []

# Coleta a saída completa (todos os termos) de cada modelo OLS para exportar em CSV.
_OLS_COEFS = []


# =========================================================
# 2. UTILITÁRIOS DE SAÍDA (figuras, tabelas, resumos)
# =========================================================

def garantir_pastas():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def configurar_estilo():
    """Define o tema visual de TODAS as figuras (chamado uma vez no início).

    Combina o tema `whitegrid` do seaborn com ajustes finos de tipografia, cores
    de eixos/grade e resolução, para gráficos mais legíveis e sofisticados.
    """
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.0)
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "font.family": "DejaVu Sans",
        "text.color": "#2B2B2B",
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.titlecolor": "#2B2B2B",
        "axes.titlepad": 10,
        "axes.labelsize": 11.5,
        "axes.labelcolor": "#2B2B2B",
        "axes.edgecolor": "#9AA3AD",
        "axes.linewidth": 0.9,
        "xtick.color": "#3A3A3A",
        "ytick.color": "#3A3A3A",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9.5,
        "legend.frameon": True,
        "legend.framealpha": 0.95,
        "legend.edgecolor": "#CBD0D6",
        "grid.color": "#E8EAED",
        "grid.linewidth": 0.7,
    })


def sufixo_onda():
    """Sufixo `_w{n}` aplicado a todos os arquivos para distinguir a onda."""
    return f"_w{WAVE_NUM}"


def _rotulo_onda(n=None):
    """Subtítulo padrão das figuras, identificando a onda e (opcional) o N."""
    base = f"ELSI-Brasil · Wave {WAVE_NUM}"
    if n is not None:
        base += f" · N = {n:,}".replace(",", ".")
    return base


def _titular(fig, ax, titulo, subtitulo=None):
    """Aplica título (semibold, no topo) e subtítulo discreto (sob o título)."""
    fig.suptitle(titulo, fontsize=13.5, fontweight="semibold", color="#2B2B2B", y=0.99)
    if subtitulo is not None:
        ax.set_title(subtitulo, fontsize=10, color=COR_CINZA, pad=8)


def salvar_figura(nome, fig=None):
    """Salva a figura atual (ou `fig`) em images/<nome>_w{n}.png e fecha-a."""
    fig = fig or plt.gcf()
    caminho = IMAGES_DIR / f"{nome}{sufixo_onda()}.png"
    fig.savefig(caminho, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[figura]  {caminho.name}")


def salvar_tabela(df, nome, index=False):
    """Salva um DataFrame em tables/<nome>_w{n}.csv (utf-8-sig abre certo no Excel)."""
    caminho = TABLES_DIR / f"{nome}{sufixo_onda()}.csv"
    df.to_csv(caminho, index=index, encoding="utf-8-sig")
    print(f"[tabela]  {caminho.name}")


def registrar_resumo(titulo, conteudo):
    """Guarda o resumo textual de um modelo para gravar ao final."""
    _RESUMOS.append((titulo, str(conteudo)))
    print(f"\n{'=' * 100}\n{titulo}\n{'=' * 100}")
    print(conteudo)


def salvar_resumos():
    """Grava todos os resumos de modelos em tables/resumos_modelos.txt."""
    caminho = TABLES_DIR / f"resumos_modelos{sufixo_onda()}.txt"
    with open(caminho, "w", encoding="utf-8") as fh:
        for titulo, conteudo in _RESUMOS:
            fh.write("=" * 100 + "\n")
            fh.write(titulo + "\n")
            fh.write("=" * 100 + "\n")
            fh.write(conteudo + "\n\n")
    print(f"[texto]   {caminho.name} ({len(_RESUMOS)} resumos)")


def salvar_coeficientes_ols():
    """Salva a saída completa de TODOS os modelos OLS, geral e por análise."""
    if not _OLS_COEFS:
        return
    completo = pd.concat(_OLS_COEFS, ignore_index=True)
    salvar_tabela(completo, "ols_coeficientes_completo")
    for analise, grupo in completo.groupby("analise"):
        salvar_tabela(grupo.drop(columns="analise"), f"ols_coef_{analise}")


def executar_etapa(nome, func, *args, **kwargs):
    """Executa uma etapa exploratória, registrando erro sem abortar o pipeline."""
    try:
        return func(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - queremos seguir mesmo se uma etapa falhar
        print(f"[AVISO] etapa '{nome}' falhou: {type(exc).__name__}: {exc}")
        return None


# =========================================================
# 3. FUNÇÕES DE DERIVAÇÃO DE VARIÁVEIS
# =========================================================

def get_lll(altura) -> float:
    """Comprimento do membro inferior (Lower Limb Length) estimado pela altura."""
    return LLL_RATIO * altura


def categorizar_escolaridade(valor_e21):
    """Recategoriza a escolaridade (e21) em grupos amplos."""
    if valor_e21 in (1, 2, 3):
        return 1
    elif valor_e21 == 4:
        return 2
    elif valor_e21 == 5:
        return 3
    elif valor_e21 == 6:
        return 4
    elif valor_e21 == 9:
        return 9
    return np.nan


def categorizar_atividade_fisica(valor_l9):
    """Frequência de atividade física: 0→0, 9→NaN, 1–7 mantidos, resto→NaN."""
    if valor_l9 == 0:
        return 0
    elif valor_l9 == 9:
        return np.nan
    elif 1 <= valor_l9 <= 7:
        return valor_l9
    return np.nan


def carregar_dados():
    df = pd.read_csv(DATA_FILE)
    print(f"Dados carregados de {DATA_FILE.name}: {df.shape[0]} linhas x {df.shape[1]} colunas")
    return df


def _ssws_wave2(f_df):
    """SSWS da Wave 2: tempo já em segundos (mf35s, mf38s).

    Velocidade média dos dois percursos de 3 m, excluindo os códigos de ausência
    666/888/8888. Retorna a Série alinhada ao índice de `f_df`.
    """
    f_v1 = (f_df["mf35s"] != 666) & (f_df["mf35s"] != 888) & (f_df["mf35s"] != 8888)
    f_v2 = (f_df["mf38s"] != 666) & (f_df["mf38s"] != 888) & (f_df["mf38s"] != 8888)
    vel_df = f_df.loc[f_v1 & f_v2].copy()
    vel_df["tc_3m_v_media"] = (3 / vel_df["mf35s"] + 3 / vel_df["mf38s"]) / 2
    return vel_df["tc_3m_v_media"]


def _ssws_wave1(f_df):
    """SSWS da Wave 1: não há tempo em segundos — reconstrói-se do tempo decomposto.

    Cada medição traz minutos, segundos e centésimos de segundo:
      medição 1 → mf33 (min), mf34 (s), mf35 (centésimos);
      medição 2 → mf36 (min), mf37 (s), mf38 (centésimos).
    Tempo total (s) = min*60 + s + centésimos/100; velocidade = 3 / tempo.
    A SSWS é a média das velocidades das duas medições, excluindo linhas em que
    qualquer componente seja código de ausência. Retorna a Série alinhada a `f_df`.
    """
    comps_1 = ["mf33", "mf34", "mf35"]
    comps_2 = ["mf36", "mf37", "mf38"]
    validos = ~f_df[comps_1 + comps_2].isin(SENTINELAS_TEMPO_W1).any(axis=1)
    vel_df = f_df.loc[validos].copy()

    t1 = vel_df["mf33"] * 60 + vel_df["mf34"] + vel_df["mf35"] / 100
    t2 = vel_df["mf36"] * 60 + vel_df["mf37"] + vel_df["mf38"] / 100
    vel_df["tc_3m_v_media"] = (3 / t1 + 3 / t2) / 2
    return vel_df["tc_3m_v_media"]


def derivar_marcha_e_indices(df):
    """Deriva SSWS, comprimento do membro inferior, OWS, velocidade máxima e LRI.

    A origem da SSWS depende da onda (segundos diretos na Wave 2; tempo decomposto
    na Wave 1) e a altura é normalizada para centímetros (Wave 1 vem em metros).
    A partir daí a sequência é a mesma das duas ondas:
      1. filtra a altura (sentinelas) e converte para cm;
      2. deriva a SSWS conforme a onda (média dos dois percursos de 3 m);
      3. alinha a SSWS por índice (linhas sem velocidade válida ficam NaN);
      4. deriva OWS e MAX_WALKING_SPEED a partir do membro inferior;
      5. remove casos com SSWS > MAX_WALKING_SPEED (também descarta SSWS NaN);
      6. calcula LRI = 100 * SSWS / OWS.
    """
    if WAVE_NUM == 2:
        # Altura em centímetros; sentinelas 888/999.
        f_df = df[~df["mf13"].isin([888, 999])].copy()
        f_df["altura_cm"] = f_df["mf13"]
        f_df["SSWS"] = _ssws_wave2(f_df)
    else:
        # Altura em metros (Wave 1) → converte para cm; sentinela 99999.
        f_df = df[df["mf13"] != SENTINELA_ALTURA_W1].copy()
        f_df["altura_cm"] = f_df["mf13"] * 100
        f_df["SSWS"] = _ssws_wave1(f_df)

    f_df["lower_limb_length"] = get_lll(f_df["altura_cm"])
    f_df["OWS"] = np.sqrt(FR_WALKING * G * (f_df["lower_limb_length"] / 100))
    f_df["MAX_WALKING_SPEED"] = np.sqrt(FR_RUNNING * G * (f_df["lower_limb_length"] / 100))

    # Remove casos fisicamente implausíveis (e, por consequência, SSWS NaN).
    f_df = f_df[f_df["SSWS"] <= f_df["MAX_WALKING_SPEED"]]

    f_df["LRI_decimal"] = f_df["SSWS"] / f_df["OWS"]
    f_df["LRI"] = f_df["LRI_decimal"] * 100

    print(f"Após derivação da marcha: {f_df.shape[0]} participantes elegíveis")
    return f_df


def derivar_morbidades(f_df):
    """Conta morbidades (n_morbidades) e cria os indicadores binários por contagem."""
    multimorbidity_mask = f_df[MULTIMORBIDADES_KEYS] == 1
    f_df["n_morbidades"] = multimorbidity_mask.sum(axis=1)

    f_df["morbidades_menor_que_2"] = (f_df["n_morbidades"] < 2).astype(int)
    f_df["morbidades_igual_a_2"] = (f_df["n_morbidades"] == 2).astype(int)
    f_df["morbidades_igual_a_3"] = (f_df["n_morbidades"] == 3).astype(int)
    f_df["morbidades_igual_a_4"] = (f_df["n_morbidades"] == 4).astype(int)
    f_df["morbidades_igual_a_5"] = (f_df["n_morbidades"] == 5).astype(int)
    f_df["morbidades_igual_a_6"] = (f_df["n_morbidades"] == 6).astype(int)
    f_df["morbidades_maior_ou_igual_a_7"] = (f_df["n_morbidades"] >= 7).astype(int)
    return f_df


def derivar_variaveis_secundarias(f_df):
    """Deriva escolaridade, força de preensão, quedas, atividade física e equilíbrio."""
    f_df["escolaridade_categorizada"] = f_df["e21"].apply(categorizar_escolaridade)
    # Versão para modelagem: o código 9 (não sabe/não respondeu) vira NaN, pois
    # não representa um nível de escolaridade e não pode entrar como covariável
    # de ajuste. A descritiva (escolaridade_categorizada) preserva o 9.
    f_df["escolaridade_modelo"] = f_df["escolaridade_categorizada"].replace(9, np.nan)

    # Força de preensão manual: média das 3 medidas, descartando códigos >= 555.
    handgrip_cols = ["mf27", "mf28", "mf29"]
    temp_handgrip = f_df[handgrip_cols].copy()
    for col in handgrip_cols:
        temp_handgrip.loc[temp_handgrip[col] >= 555, col] = np.nan
    f_df["handgrip_mean"] = temp_handgrip.mean(axis=1)

    # Histórico de quedas.
    f_df["queda_dummy"] = (f_df["n18"] == 1).astype(int)

    # Atividade física (frequência e tempo total).
    f_df["atividade_fisica_dummy"] = f_df["l9"].apply(categorizar_atividade_fisica)
    if "l10_2" in f_df.columns:
        f_df["tempo_minutos_atividade_fisica"] = np.nan
        condicao = (f_df["atividade_fisica_dummy"] <= 7) & (~f_df["l10_2"].isin([88, 99]))
        f_df.loc[condicao, "tempo_minutos_atividade_fisica"] = (
            f_df.loc[condicao, "atividade_fisica_dummy"] * f_df.loc[condicao, "l10_2"]
        )
    else:
        f_df["tempo_minutos_atividade_fisica"] = np.nan
        print("[AVISO] coluna 'l10_2' ausente — tempo_minutos_atividade_fisica = NaN")

    # Testes de desempenho físico.
    f_df["mf30_dummy"] = f_df["mf30"].apply(lambda x: x if x < 66 else np.nan)
    f_df["mf31_dummy"] = f_df.apply(
        lambda row: row["mf31"] if row["idade"] <= 69 else np.nan, axis=1
    )
    return f_df


# =========================================================
# 4. MODELAGEM — FÓRMULAS, AJUSTE E EXTRAÇÃO DE MÉTRICAS
# =========================================================

# Covariáveis de ajuste dos modelos multivariados. A escolaridade entra como
# fator categórico — C(...) gera variáveis indicadoras (dummies) com a menor
# escolaridade como categoria de referência, sem impor efeito linear entre os
# níveis. COLS_AJUSTE lista as colunas brutas (para o dropna conjunto);
# TERMOS_AJUSTE lista os termos como entram na fórmula patsy.
COLS_AJUSTE = ["idade", "sexo", "escolaridade_modelo"]
TERMOS_AJUSTE = ["idade", "sexo", "C(escolaridade_modelo)"]


def montar_formula(desfecho, preditor, ajustar=False):
    """Monta a fórmula patsy do modelo (ex.: 'SSWS ~ n_morbidades').

    Quando `ajustar=True`, anexa as covariáveis de ajuste (idade, sexo e
    escolaridade categórica), produzindo o modelo multivariado.
    """
    formula = f"{desfecho} ~ {preditor}"
    if ajustar:
        # Acrescenta '+ idade + sexo + C(escolaridade_modelo)' à fórmula.
        formula += " + " + " + ".join(TERMOS_AJUSTE)
    return formula


def _rodar_modelo(df, desfecho, preditor, ajustar, tipo):
    """Núcleo comum a OLS e logística: monta fórmula, limpa NaN e ajusta."""
    # 1) Fórmula do modelo (com ou sem as covariáveis de ajuste).
    formula = montar_formula(desfecho, preditor, ajustar=ajustar)
    # 2) Seleciona só as colunas usadas. No modelo ajustado inclui as covariáveis
    #    brutas (COLS_AJUSTE); usa o nome 'escolaridade_modelo' — e não 'C(...)' —
    #    porque aqui é seleção de coluna, não termo de fórmula.
    colunas = [desfecho, preditor] + (COLS_AJUSTE if ajustar else [])
    # 3) Remove linhas com qualquer NaN (listwise deletion): garante que todos os
    #    termos do modelo sejam estimados sobre exatamente o mesmo subconjunto.
    #    Como 'escolaridade_modelo' tem NaN (código 9 = NS/NR), o N do modelo
    #    ajustado é menor que o do cru.
    df_modelo = df[colunas].dropna().copy()

    if tipo == "OLS":
        modelo = smf.ols(formula=formula, data=df_modelo).fit()
        nome_tipo = "OLS"
    else:
        modelo = smf.logit(formula=formula, data=df_modelo).fit(disp=False)
        nome_tipo = "Logística"

    return {
        "tipo_modelo": nome_tipo,
        "desfecho": desfecho,
        "preditor": preditor,
        "ajustado": ajustar,
        "formula": formula,
        "n": len(df_modelo),
        "modelo": modelo,
    }


def rodar_ols(df, desfecho, preditor, ajustar=False):
    return _rodar_modelo(df, desfecho, preditor, ajustar, tipo="OLS")


def rodar_logistica(df, desfecho, preditor, ajustar=False):
    return _rodar_modelo(df, desfecho, preditor, ajustar, tipo="Logit")


def extrair_metricas_modelo(resultado):
    """Extrai coeficientes, IC95%, p-valores e métricas de ajuste em uma linha."""
    modelo = resultado["modelo"]
    preditor = resultado["preditor"]

    linha = {
        "tipo_modelo": resultado["tipo_modelo"],
        "desfecho": resultado["desfecho"],
        "preditor": resultado["preditor"],
        "ajustado": resultado["ajustado"],
        "formula": resultado["formula"],
        "n": resultado["n"],
        "intercepto": np.nan,
        "coef": np.nan, "std_err": np.nan, "stat": np.nan, "p_value": np.nan,
        "ic95_inf": np.nan, "ic95_sup": np.nan,
        "r_squared": np.nan, "r_squared_ajustado": np.nan, "pseudo_r_squared": np.nan,
        "aic": np.nan, "bic": np.nan,
        "odds_ratio": np.nan, "or_ic95_inf": np.nan, "or_ic95_sup": np.nan,
    }

    # Intercepto: smf.ols usa o rótulo "Intercept"; sm.OLS+add_constant usa "const".
    for nome_const in ("Intercept", "const"):
        if nome_const in modelo.params.index:
            linha["intercepto"] = modelo.params[nome_const]
            break

    if preditor in modelo.params.index:
        linha["coef"] = modelo.params[preditor]
        linha["std_err"] = modelo.bse[preditor]
        linha["p_value"] = modelo.pvalues[preditor]
        conf = modelo.conf_int().loc[preditor]
        linha["ic95_inf"], linha["ic95_sup"] = conf[0], conf[1]
        linha["stat"] = modelo.tvalues[preditor]  # t (OLS) ou z (Logit)

    if resultado["tipo_modelo"] == "OLS":
        linha["r_squared"] = modelo.rsquared
        linha["r_squared_ajustado"] = modelo.rsquared_adj
        linha["aic"], linha["bic"] = modelo.aic, modelo.bic
    elif resultado["tipo_modelo"] == "Logística":
        linha["pseudo_r_squared"] = modelo.prsquared
        linha["aic"], linha["bic"] = modelo.aic, modelo.bic
        if preditor in modelo.params.index:
            linha["odds_ratio"] = np.exp(modelo.params[preditor])
            linha["or_ic95_inf"] = np.exp(linha["ic95_inf"])
            linha["or_ic95_sup"] = np.exp(linha["ic95_sup"])

    return linha


def tabela_coeficientes(modelo, analise, desfecho, preditor, ajustado, cov_type="nonrobust"):
    """Saída completa de um modelo: uma linha por termo (intercepto, preditor, ajustes).

    Usa np.asarray para funcionar tanto com modelos comuns quanto com resultados
    de erros-padrão robustos (que não preservam o índice dos parâmetros).
    """
    conf = np.asarray(modelo.conf_int())
    df = pd.DataFrame({
        "analise": analise,
        "desfecho": desfecho,
        "preditor": preditor,
        "ajustado": ajustado,
        "cov_type": cov_type,
        "n": int(modelo.nobs),
        "termo": list(modelo.model.exog_names),
        "coef": np.asarray(modelo.params),
        "std_err": np.asarray(modelo.bse),
        "stat": np.asarray(modelo.tvalues),
        "p_value": np.asarray(modelo.pvalues),
        "ic95_inf": conf[:, 0],
        "ic95_sup": conf[:, 1],
        "r_squared": getattr(modelo, "rsquared", np.nan),
        "r_squared_ajustado": getattr(modelo, "rsquared_adj", np.nan),
        "aic": getattr(modelo, "aic", np.nan),
        "bic": getattr(modelo, "bic", np.nan),
    })
    num = ["coef", "std_err", "stat", "p_value", "ic95_inf", "ic95_sup",
           "r_squared", "r_squared_ajustado", "aic", "bic"]
    df[num] = df[num].round(4)
    return df


def coletar_ols(modelo, analise, desfecho, preditor, ajustado=False, cov_type="nonrobust"):
    """Acumula a saída completa de um modelo OLS para exportação posterior."""
    _OLS_COEFS.append(
        tabela_coeficientes(modelo, analise, desfecho, preditor, ajustado, cov_type)
    )


def preparar_grupos_morbidade(df):
    """Padroniza os códigos de doença e cria colunas binárias e de soma por grupo."""
    df = df.copy()
    cols_g0 = [c for c in GRUPO_0 if c in df.columns]
    cols_g1 = [c for c in GRUPO_1 if c in df.columns]
    cols_g2 = [c for c in GRUPO_2 if c in df.columns]

    # Padroniza: 1 = possui, 0 = não possui, 9 = missing -> NaN.
    for col in cols_g0 + cols_g1 + cols_g2:
        df[col] = pd.to_numeric(df[col], errors="coerce").replace(9, np.nan).map({0: 0, 1: 1})

    df["grupo_0_neuro_oftalmo_musculoesqueleticas"] = df[cols_g0].fillna(0).max(axis=1).astype(int)
    df["grupo_1_cardiorrespiratorias"] = df[cols_g1].fillna(0).max(axis=1).astype(int)
    df["grupo_2_outras"] = df[cols_g2].fillna(0).max(axis=1).astype(int)

    df["soma_grupo_0_neuro_oftalmo_musculoesqueleticas"] = df[cols_g0].fillna(0).sum(axis=1).astype(int)
    df["soma_grupo_1_cardiorrespiratorias"] = df[cols_g1].fillna(0).sum(axis=1).astype(int)
    df["soma_grupo_2_outras"] = df[cols_g2].fillna(0).sum(axis=1).astype(int)
    return df


def rodar_todas_regressoes(df):
    """Roda OLS e logísticas (cruas e ajustadas) para todos os desfechos x preditores."""
    predictors = ["SSWS", "LRI"]

    ols_desfechos = [
        "n_morbidades",
        "soma_grupo_0_neuro_oftalmo_musculoesqueleticas",
        "soma_grupo_1_cardiorrespiratorias",
        "soma_grupo_2_outras",
    ]
    logistic_desfechos = [
        "grupo_0_neuro_oftalmo_musculoesqueleticas",
        "grupo_1_cardiorrespiratorias",
        "grupo_2_outras",
    ] + MORBIDADE_COLS

    ols_raw, log_raw = [], []
    for desfecho in ols_desfechos:
        for preditor in predictors:
            ols_raw.append(rodar_ols(df, desfecho, preditor, ajustar=False))
            ols_raw.append(rodar_ols(df, desfecho, preditor, ajustar=True))
    for desfecho in logistic_desfechos:
        for preditor in predictors:
            log_raw.append(rodar_logistica(df, desfecho, preditor, ajustar=False))
            log_raw.append(rodar_logistica(df, desfecho, preditor, ajustar=True))

    # Guarda a saída completa (todos os termos) de cada OLS por grupo de doenças.
    for r in ols_raw:
        coletar_ols(r["modelo"], "grupos_morbidade", r["desfecho"], r["preditor"],
                    ajustado=r["ajustado"])

    resultados_ols = pd.DataFrame([extrair_metricas_modelo(r) for r in ols_raw])
    resultados_logistica = pd.DataFrame([extrair_metricas_modelo(r) for r in log_raw])

    ols_ordem = [
        "tipo_modelo", "desfecho", "preditor", "ajustado", "formula", "n",
        "intercepto", "coef", "std_err", "stat", "p_value", "ic95_inf", "ic95_sup",
        "r_squared", "r_squared_ajustado", "aic", "bic",
    ]
    log_ordem = [
        "tipo_modelo", "desfecho", "preditor", "ajustado", "formula", "n",
        "intercepto", "coef", "std_err", "stat", "p_value", "ic95_inf", "ic95_sup",
        "pseudo_r_squared", "aic", "bic", "odds_ratio", "or_ic95_inf", "or_ic95_sup",
    ]
    resultados_ols = resultados_ols[ols_ordem].copy()
    resultados_logistica = resultados_logistica[log_ordem].copy()

    colunas_arredondar = [
        "intercepto", "coef", "std_err", "stat", "p_value", "ic95_inf", "ic95_sup",
        "r_squared", "r_squared_ajustado", "pseudo_r_squared",
        "aic", "bic", "odds_ratio", "or_ic95_inf", "or_ic95_sup",
    ]
    for col in colunas_arredondar:
        if col in resultados_ols.columns:
            resultados_ols[col] = resultados_ols[col].round(4)
        if col in resultados_logistica.columns:
            resultados_logistica[col] = resultados_logistica[col].round(4)

    return resultados_ols, resultados_logistica


# ---- Interpretação automática dos resultados --------------------------------

def interpretar_efeito(linha):
    preditor, desfecho = linha["preditor"], linha["desfecho"]
    tipo, coef, p = linha["tipo_modelo"], linha["coef"], linha["p_value"]
    if pd.isna(coef) or pd.isna(p):
        return "interpretação indisponível"
    if p >= 0.05:
        return f"sem associação estatisticamente significativa entre {preditor} e {desfecho}"
    if tipo == "OLS":
        return (f"maior {preditor} associado a maior {desfecho}" if coef > 0
                else f"maior {preditor} associado a menor {desfecho}")
    if tipo == "Logística":
        return (f"maior {preditor} associado a maior chance de {desfecho}" if coef > 0
                else f"maior {preditor} associado a menor chance de {desfecho}")
    return "interpretação não classificada"


def classificar_direcao(linha):
    coef, p = linha["coef"], linha["p_value"]
    if pd.isna(coef) or pd.isna(p):
        return "indeterminado"
    if p >= 0.05:
        return "não significativo"
    return "positivo" if coef > 0 else "negativo" if coef < 0 else "nulo"


def classificar_significancia(p):
    if pd.isna(p):
        return "indisponível"
    if p < 0.001:
        return "p<0.001"
    if p < 0.01:
        return "p<0.01"
    if p < 0.05:
        return "p<0.05"
    return "ns"


# =========================================================
# 5. ANÁLISES DESCRITIVAS E GRÁFICOS
# =========================================================

def analise_descritiva_marcha(f_df):
    """Descritivas e gráficos de distribuição da velocidade de marcha."""
    desc = f_df[["lower_limb_length", "SSWS", "OWS", "MAX_WALKING_SPEED", "LRI"]].describe()
    salvar_tabela(desc.reset_index(), "descritivas_marcha", index=False)

    v = f_df["SSWS"]
    n = len(v)

    # Histograma da velocidade com média, mediana e cutoff clínico (0.8 m/s).
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(v, bins=40, kde=True, color=COR_PRIMARIA, edgecolor="white",
                 linewidth=0.5, alpha=0.85, ax=ax, line_kws={"linewidth": 2.2})
    if ax.lines:
        ax.lines[-1].set_color(COR_CINZA)  # recolore a curva KDE (última linha)
    ax.axvline(v.median(), color=COR_REALCE, ls="--", lw=2,
               label=f"Mediana = {v.median():.2f} m/s".replace(".", ","))
    ax.axvline(v.mean(), color=COR_DESTAQUE, ls="--", lw=2,
               label=f"Média = {v.mean():.2f} m/s".replace(".", ","))
    ax.axvline(0.8, color=COR_CINZA, ls=":", lw=2, label="Cutoff clínico = 0,80 m/s")
    ax.set_xlabel("Velocidade de marcha — SSWS (m/s)")
    ax.set_ylabel("Frequência")
    ax.legend(loc="upper right")
    _titular(fig, ax, "Distribuição da velocidade de marcha (SSWS)", _rotulo_onda(n))
    sns.despine(fig)
    salvar_figura("hist_velocidade", fig)

    # Violino + boxplot sobreposto (dispersão da velocidade).
    fig, ax = plt.subplots(figsize=(10, 3.8))
    sns.violinplot(x=v, color=COR_SECUNDARIA, inner=None, linewidth=0,
                   alpha=0.40, cut=0, ax=ax)
    sns.boxplot(x=v, width=0.18, ax=ax, showcaps=True, showmeans=True,
                boxprops={"facecolor": "white", "edgecolor": COR_PRIMARIA, "linewidth": 1.6},
                whiskerprops={"color": COR_PRIMARIA, "linewidth": 1.4},
                capprops={"color": COR_PRIMARIA, "linewidth": 1.4},
                medianprops={"color": COR_DESTAQUE, "linewidth": 2},
                meanprops={"marker": "D", "markerfacecolor": COR_REALCE,
                           "markeredgecolor": "white", "markersize": 7},
                flierprops={"marker": "o", "markerfacecolor": COR_CINZA,
                            "markeredgecolor": "none", "markersize": 3, "alpha": 0.3})
    ax.set_xlabel("Velocidade de marcha — SSWS (m/s)")
    ax.set_yticks([])
    _titular(fig, ax, "Dispersão da velocidade de marcha (SSWS)", _rotulo_onda(n))
    sns.despine(fig, left=True)
    salvar_figura("boxplot_velocidade", fig)

    # Grade de histogramas das variáveis de marcha.
    variaveis = [
        ("altura_cm", "Altura (cm)"),
        ("lower_limb_length", "Comprimento do membro inferior — LLL (cm)"),
        ("OWS", "Velocidade ótima — OWS (m/s)"),
        ("SSWS", "Velocidade auto-selecionada — SSWS (m/s)"),
        ("LRI", "Índice de reabilitação locomotor — LRI (%)"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.ravel()
    for ax_i, (col, rotulo) in zip(axes, variaveis):
        sns.histplot(f_df[col], bins=40, kde=True, color=COR_PRIMARIA,
                     edgecolor="white", linewidth=0.4, alpha=0.85, ax=ax_i,
                     line_kws={"linewidth": 2})
        if ax_i.lines:
            ax_i.lines[-1].set_color(COR_CINZA)
        ax_i.set_title(rotulo, fontsize=11.5, fontweight="bold")
        ax_i.set_xlabel("")
        ax_i.set_ylabel("Frequência")
    for ax_i in axes[len(variaveis):]:
        ax_i.set_visible(False)
    fig.suptitle("Distribuições das variáveis de marcha", fontsize=14,
                 fontweight="semibold", color="#2B2B2B", y=1.00)
    fig.text(0.5, 0.965, _rotulo_onda(len(f_df)), ha="center", color=COR_CINZA,
             fontsize=10.5)
    sns.despine(fig)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    salvar_figura("hist_variaveis_marcha", fig)


def testes_normalidade(f_df):
    """Q-Q plot, Anderson-Darling, assimetria e curtose da SSWS."""
    v = f_df["SSWS"]
    n = len(v)

    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    sm.qqplot(v, line="45", fit=True, ax=ax, marker="o",
              markerfacecolor=COR_PRIMARIA, markeredgecolor="white",
              markersize=4, alpha=0.45)
    if len(ax.lines) >= 2:  # estiliza a reta de referência (45°)
        ax.lines[1].set_color(COR_DESTAQUE)
        ax.lines[1].set_linewidth(2.2)
        ax.lines[1].set_linestyle("--")
    ax.set_xlabel("Quantis teóricos (distribuição normal)")
    ax.set_ylabel("Quantis amostrais (SSWS padronizada)")
    ax.set_aspect("equal")
    _titular(fig, ax, "Q-Q plot da SSWS", _rotulo_onda(n))
    sns.despine(fig)
    salvar_figura("qqplot_velocidade", fig)

    ad = stats.anderson(v, dist="norm")
    texto = (
        f"Teste de Anderson-Darling (SSWS)\n"
        f"  Estatística: {ad.statistic:.4f}\n"
        f"  Assimetria (skew): {stats.skew(v):.4f}\n"
        f"  Curtose (kurtosis): {stats.kurtosis(v):.4f}\n"
    )
    registrar_resumo("Normalidade / Simetria da SSWS", texto)


def analise_morbidades(f_df):
    """Distribuição do número de morbidades e contagem das categorias binárias."""
    distribuicao = f_df["n_morbidades"].value_counts().sort_index()
    dist_df = distribuicao.reset_index()
    dist_df.columns = ["n_morbidades", "n"]
    salvar_tabela(dist_df, "distribuicao_morbidades", index=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    barras = ax.bar(distribuicao.index, distribuicao.values, color=COR_PRIMARIA,
                    edgecolor="white", linewidth=0.6, alpha=0.92)
    topo = distribuicao.values.max()
    for b in barras:
        h = b.get_height()
        if h > 0:
            ax.text(b.get_x() + b.get_width() / 2, h + topo * 0.01, f"{int(h)}",
                    ha="center", va="bottom", fontsize=9, color=COR_CINZA)
    ax.set_xlabel("Número de morbidades")
    ax.set_ylabel("Frequência (nº de participantes)")
    ax.set_xticks(distribuicao.index)
    ax.margins(y=0.08)
    _titular(fig, ax, "Distribuição do número de morbidades", _rotulo_onda(len(f_df)))
    sns.despine(fig)
    salvar_figura("hist_morbidades", fig)

    contagens = pd.DataFrame(
        {"categoria": MORBIDADE_COLS, "n": [int(f_df[c].sum()) for c in MORBIDADE_COLS]}
    )
    salvar_tabela(contagens, "contagem_categorias_morbidade", index=False)


def regressao_simples_com_scatter(f_df, desfecho, nome_arquivo, titulo):
    """OLS desfecho ~ n_morbidades com gráfico de dispersão e reta de regressão."""
    Y = f_df[desfecho]
    X = sm.add_constant(f_df["n_morbidades"])
    modelo = sm.OLS(Y, X).fit()
    registrar_resumo(f"OLS: {desfecho} ~ n_morbidades", modelo.summary())
    coletar_ols(modelo, "principais", desfecho, "n_morbidades")

    rotulos_y = {"SSWS": "SSWS (m/s)", "LRI": "LRI (%)"}
    x = f_df["n_morbidades"].astype(float)
    y = f_df[desfecho]

    fig, ax = plt.subplots(figsize=(10, 6.5))

    # Nuvem de pontos com jitter horizontal (a contagem é discreta → evita
    # sobreposição). O jitter é apenas visual; o modelo usa os valores reais.
    rng = np.random.default_rng(42)
    x_jit = x + rng.uniform(-0.18, 0.18, size=len(x))
    ax.scatter(x_jit, y, s=12, color=COR_SECUNDARIA, alpha=0.16, edgecolors="none",
               zorder=1, label="Participantes (com jitter)")

    # Média ± IC95% por número de morbidades.
    resumo = f_df.groupby("n_morbidades")[desfecho].agg(["mean", "count", "std"])
    resumo["se"] = resumo["std"] / np.sqrt(resumo["count"])
    ax.errorbar(resumo.index, resumo["mean"], yerr=1.96 * resumo["se"], fmt="o",
                color=COR_PRIMARIA, ecolor=COR_PRIMARIA, elinewidth=1.5, capsize=3,
                markersize=6, markeredgecolor="white", zorder=3,
                label="Média ± IC95% por faixa")

    # Reta de regressão OLS.
    xs = np.linspace(x.min(), x.max(), 100)
    pred = modelo.predict(sm.add_constant(xs))
    ax.plot(xs, pred, color=COR_DESTAQUE, lw=2.5, zorder=4, label="Reta de regressão (OLS)")

    # Caixa com β, R² e p-valor.
    b = modelo.params["n_morbidades"]
    r2 = modelo.rsquared
    p = modelo.pvalues["n_morbidades"]
    p_txt = "p < 0,001" if p < 0.001 else f"p = {p:.3f}".replace(".", ",")
    texto = f"β = {b:.3f}\nR² = {r2:.3f}\n{p_txt}".replace(".", ",")
    ax.text(0.03, 0.06, texto, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=10.5, bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                                     edgecolor="#D5DBDB", alpha=0.95))

    ax.set_xlabel("Número de morbidades")
    ax.set_ylabel(rotulos_y.get(desfecho, desfecho))
    ax.set_xticks(range(int(x.min()), int(x.max()) + 1))
    ax.legend(loc="upper right")
    _titular(fig, ax, titulo, _rotulo_onda(len(f_df)))
    sns.despine(fig)
    salvar_figura(nome_arquivo, fig)
    return modelo


def regressoes_ols_por_categoria(f_df):
    """OLS de cada categoria binária de morbidade ~ SSWS / LRI (modelo crus)."""
    for desfecho in MORBIDADE_COLS:
        for preditor in ["SSWS", "LRI"]:
            resultado = rodar_ols(f_df, desfecho=desfecho, preditor=preditor, ajustar=False)
            registrar_resumo(f"OLS: {desfecho} ~ {preditor}", resultado["modelo"].summary())
            coletar_ols(resultado["modelo"], "por_categoria", desfecho, preditor)


def categorizacoes_descritivas(f_df):
    """Tercis de LRI/SSWS e categorização de escolaridade (apenas descritivo)."""
    f_df["LRI_tercil"] = pd.qcut(f_df["LRI"], q=3, labels=["BAIXO_LRI", "MEDIO_LRI", "ALTO_LRI"])
    f_df["SSWS_tercil"] = pd.qcut(f_df["SSWS"], q=3, labels=["BAIXO_SSWS", "MEDIO_SSWS", "ALTO_SSWS"])
    print("\nTercis de LRI:\n", f_df["LRI_tercil"].value_counts())
    print("\nTercis de SSWS:\n", f_df["SSWS_tercil"].value_counts())
    print("\nEscolaridade categorizada:\n", f_df["escolaridade_categorizada"].value_counts())
    return f_df


# =========================================================
# 6. CURVAS ROC / AUC
# =========================================================

def curvas_roc(f_df, score_col, nome_arquivo, titulo, nome_tabela):
    """Plota curvas ROC do score (LRI ou SSWS) contra cada categoria de morbidade."""
    rotulos = {
        "morbidades_menor_que_2": "< 2 morbidades",
        "morbidades_igual_a_2": "= 2 morbidades",
        "morbidades_igual_a_3": "= 3 morbidades",
        "morbidades_igual_a_4": "= 4 morbidades",
        "morbidades_igual_a_5": "= 5 morbidades",
        "morbidades_igual_a_6": "= 6 morbidades",
        "morbidades_maior_ou_igual_a_7": "≥ 7 morbidades",
    }
    cores = sns.color_palette(PALETA_SEQUENCIAL, len(MORBIDADE_COLS))

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.plot([0, 1], [0, 1], color=COR_CINZA, lw=1.8, ls="--",
            label="Acaso (AUC = 0,50)", zorder=1)

    resultados = []
    for cor, categoria in zip(cores, MORBIDADE_COLS):
        fpr, tpr, _ = roc_curve(f_df[categoria], f_df[score_col])
        roc_auc = auc(fpr, tpr)
        resultados.append({"Analise": f"{score_col} vs {categoria}", "AUC": round(roc_auc, 4)})
        rotulo = f"{rotulos.get(categoria, categoria)} (AUC = {roc_auc:.2f})".replace(".", ",")
        ax.plot(fpr, tpr, lw=2.2, color=cor, label=rotulo, zorder=2)

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.02)
    ax.set_aspect("equal")
    ax.set_xlabel("Taxa de falsos positivos (1 − especificidade)")
    ax.set_ylabel("Taxa de verdadeiros positivos (sensibilidade)")
    ax.legend(loc="lower right", title="Faixa de morbidade")
    _titular(fig, ax, titulo, _rotulo_onda(len(f_df)))
    sns.despine(fig)
    salvar_figura(nome_arquivo, fig)

    salvar_tabela(pd.DataFrame(resultados), nome_tabela, index=False)


def comparar_auc_por_corte(f_df):
    """Compara AUC de modelos logísticos SSWS vs LRI (ajustados) para cortes >=2,3,4.

    O ajuste inclui idade, sexo e escolaridade. A escolaridade entra como
    variáveis indicadoras (get_dummies com drop_first → a menor escolaridade é a
    referência); como o código 9 vira NaN, as linhas incompletas são descartadas
    em conjunto, o que reduz levemente o N deste quadro.
    """
    esc_dummies = pd.get_dummies(
        f_df["escolaridade_modelo"], prefix="esc", drop_first=True, dtype=float
    )
    cols_esc = list(esc_dummies.columns)
    base = pd.concat(
        [f_df[["n_morbidades", "SSWS", "LRI", "idade", "sexo"]], esc_dummies], axis=1
    ).dropna()

    resultados = []
    for c in (2, 3, 4):
        target = (base["n_morbidades"] >= c).astype(int)

        X_ssws = sm.add_constant(base[["SSWS", "idade", "sexo"] + cols_esc])
        mod_ssws = sm.Logit(target, X_ssws).fit(disp=0)
        auc_ssws = roc_auc_score(target, mod_ssws.predict(X_ssws))

        X_lri = sm.add_constant(base[["LRI", "idade", "sexo"] + cols_esc])
        mod_lri = sm.Logit(target, X_lri).fit(disp=0)
        auc_lri = roc_auc_score(target, mod_lri.predict(X_lri))

        resultados.append({"Corte": f">={c}", "AUC_SSWS": round(auc_ssws, 4),
                           "AUC_LRI": round(auc_lri, 4), "n": int(len(base))})

    df_res = pd.DataFrame(resultados)
    salvar_tabela(df_res, "auc_comparacao_cortes", index=False)
    print("\nComparação de AUC (SSWS vs LRI) por ponto de corte:\n", df_res)
    return df_res


# =========================================================
# 7. REGRESSÕES EXPLORATÓRIAS DE VARIÁVEIS SECUNDÁRIAS
# =========================================================

def ols_simples(df, y_col, x_col, titulo):
    """OLS de uma variável (com constante), tratando NaN em conjunto.

    Usa erros-padrão convencionais (não-robustos), por decisão do projeto: há
    heterocedasticidade nos modelos (Breusch-Pagan p < 0,001), mas o impacto
    inferencial dos erros-padrão robustos é desprezível neste N (ver
    OBSERVACOES.md §2.11); a correção relevante seria o desenho amostral (§5.1).
    """
    dados = df[[y_col, x_col]].dropna()
    if dados.empty or dados[x_col].nunique() < 2:
        # Sem dados válidos (p.ex. tempo de atividade física na Wave 1, que
        # depende de l10_2 ausente) ou preditor constante: pula sem abortar.
        print(f"[AVISO] '{titulo}' ignorado: sem dados válidos para {x_col}.")
        return None
    Y = dados[y_col]
    X = sm.add_constant(dados[x_col])
    modelo = sm.OLS(Y, X).fit()
    registrar_resumo(titulo, modelo.summary())
    coletar_ols(modelo, "exploratorias", y_col, x_col)
    return modelo


def regressoes_exploratorias(f_df):
    """Hipóteses exploratórias: força de preensão, quedas, atividade física, equilíbrio."""
    ols_simples(f_df, "n_morbidades", "handgrip_mean", "OLS: n_morbidades ~ handgrip_mean")
    ols_simples(f_df, "n_morbidades", "queda_dummy", "OLS: n_morbidades ~ queda_dummy")
    ols_simples(f_df, "n_morbidades", "atividade_fisica_dummy",
                "OLS: n_morbidades ~ atividade_fisica_dummy")
    ols_simples(f_df, "SSWS", "tempo_minutos_atividade_fisica",
                "OLS: SSWS ~ tempo_minutos_atividade_fisica")
    ols_simples(f_df, "n_morbidades", "tempo_minutos_atividade_fisica",
                "OLS: n_morbidades ~ tempo_minutos_atividade_fisica")
    ols_simples(f_df, "SSWS", "mf30_dummy", "OLS: SSWS ~ mf30_dummy")
    ols_simples(f_df, "SSWS", "mf31_dummy", "OLS: SSWS ~ mf31_dummy")
    ols_simples(f_df, "n_morbidades", "mf31_dummy",
                "OLS: n_morbidades ~ mf31_dummy")


def descritivas_finais(f_df):
    """Descritivas resumo, prevalência abaixo de cutoffs e regressões SSWS/LRI."""
    desc = f_df[["SSWS", "OWS", "LRI"]].describe()
    salvar_tabela(desc.reset_index(), "descritivas_resumo", index=False)

    prevalencias = []
    for cutoff in (0.8, 0.7, 0.6):
        pct = (f_df["SSWS"] < cutoff).mean() * 100
        prevalencias.append({"cutoff_m_s": cutoff, "percentual_abaixo": round(pct, 2)})
        print(f"% de pessoas com SSWS < {cutoff} m/s: {pct:.2f}%")
    salvar_tabela(pd.DataFrame(prevalencias), "prevalencia_cutoffs_ssws", index=False)

    print("\nDistribuição por sexo:\n", f_df["sexo"].value_counts())

    medias = pd.DataFrame({
        "variavel": ["n_morbidades", "SSWS", "LRI"],
        "media": [round(f_df[c].mean(), 2) for c in ["n_morbidades", "SSWS", "LRI"]],
        "desvio_padrao": [round(f_df[c].std(), 2) for c in ["n_morbidades", "SSWS", "LRI"]],
    })
    salvar_tabela(medias, "medias_desvios", index=False)

    # OLS LRI ~ SSWS.
    resultado_lri_ssws = rodar_ols(f_df, "LRI", "SSWS")
    registrar_resumo("OLS: LRI ~ SSWS", resultado_lri_ssws["modelo"].summary())
    coletar_ols(resultado_lri_ssws["modelo"], "principais", "LRI", "SSWS")

    # Regressão de Poisson n_morbidades ~ SSWS.
    Y = f_df["n_morbidades"]
    X = sm.add_constant(f_df["SSWS"])
    poisson = sm.Poisson(Y, X).fit(disp=False)
    registrar_resumo("Poisson: n_morbidades ~ SSWS", poisson.summary())


def teste_vif(f_df):
    """Fator de inflação da variância (multicolinearidade) para SSWS e LRI.

    Inclui idade, sexo e escolaridade (como dummies) — as mesmas covariáveis de
    ajuste — para verificar se acrescentar escolaridade não introduz colinearidade
    preocupante (regra prática: VIF > 5–10).
    """
    esc_dummies = pd.get_dummies(
        f_df["escolaridade_modelo"], prefix="esc", drop_first=True, dtype=float
    )
    cols_esc = list(esc_dummies.columns)
    base_full = pd.concat([f_df[["idade", "sexo", "n_morbidades"]], esc_dummies], axis=1)

    def calcular_vif(df, col_marcha):
        X = sm.add_constant(df[[col_marcha, "idade", "sexo"] + cols_esc])
        vif_data = pd.DataFrame({"Variavel": X.columns})
        vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
        return vif_data

    vif_ssws = calcular_vif(pd.concat([base_full, f_df[["SSWS"]]], axis=1).dropna(), "SSWS")
    vif_lri = calcular_vif(pd.concat([base_full, f_df[["LRI"]]], axis=1).dropna(), "LRI")
    salvar_tabela(vif_ssws, "vif_ssws", index=False)
    salvar_tabela(vif_lri, "vif_lri", index=False)
    print("\nVIF — modelo SSWS:\n", vif_ssws)
    print("\nVIF — modelo LRI:\n", vif_lri)


# =========================================================
# 8. TABELA-RESUMO DAS REGRESSÕES (com interpretação)
# =========================================================

def tabelas_resumo_regressoes(f_df):
    """Roda todas as regressões por grupo de doenças e gera as tabelas-resumo."""
    f_df_modelo = preparar_grupos_morbidade(f_df)

    print("\nFrequência por grupo de doenças:")
    grupos_bin = [
        "grupo_0_neuro_oftalmo_musculoesqueleticas",
        "grupo_1_cardiorrespiratorias",
        "grupo_2_outras",
    ]
    print(f_df_modelo[grupos_bin].sum())

    resultados_ols, resultados_logistica = rodar_todas_regressoes(f_df_modelo)
    salvar_tabela(resultados_ols, "regressoes_ols")
    salvar_tabela(resultados_logistica, "regressoes_logisticas")

    # Tabela única com colunas de interpretação automática.
    tabela_resumo = pd.concat([resultados_ols, resultados_logistica], ignore_index=True)
    tabela_resumo["direcao_efeito"] = tabela_resumo.apply(classificar_direcao, axis=1)
    tabela_resumo["significancia"] = tabela_resumo["p_value"].apply(classificar_significancia)
    tabela_resumo["interpretacao_automatica"] = tabela_resumo.apply(interpretar_efeito, axis=1)

    cols_ols = ["tipo_modelo", "desfecho", "preditor", "ajustado", "n", "intercepto",
                "coef", "std_err", "stat", "p_value", "r_squared", "r_squared_ajustado",
                "aic", "bic", "direcao_efeito", "significancia", "interpretacao_automatica"]
    cols_log = ["tipo_modelo", "desfecho", "preditor", "ajustado", "n", "intercepto",
                "coef", "std_err", "stat", "p_value", "pseudo_r_squared", "odds_ratio",
                "or_ic95_inf", "or_ic95_sup", "aic", "bic", "direcao_efeito",
                "significancia", "interpretacao_automatica"]

    tabela_ols = tabela_resumo[tabela_resumo["tipo_modelo"] == "OLS"][cols_ols].copy()
    tabela_logistica = tabela_resumo[tabela_resumo["tipo_modelo"] == "Logística"][cols_log].copy()
    salvar_tabela(tabela_ols, "interpretacao_ols")
    salvar_tabela(tabela_logistica, "interpretacao_logistica")


# =========================================================
# 9. ORQUESTRAÇÃO
# =========================================================

def rodar_wave(wave):
    """Roda o pipeline completo para uma onda, com saídas sufixadas por `_w{wave}`."""
    global WAVE_NUM, DATA_FILE
    WAVE_NUM = wave
    DATA_FILE = DATA_DIR / f"ELSI_wave_{wave}.csv"

    # Zera os acumuladores de resumos/coeficientes (são por onda).
    _RESUMOS.clear()
    _OLS_COEFS.clear()

    print(f"\n{'#' * 100}\n# WAVE {wave}\n{'#' * 100}")

    # --- Preparação dos dados ---
    df = carregar_dados()
    f_df = derivar_marcha_e_indices(df)
    f_df = derivar_morbidades(f_df)
    f_df = derivar_variaveis_secundarias(f_df)

    # --- Descritivas e distribuições ---
    analise_descritiva_marcha(f_df)
    testes_normalidade(f_df)
    analise_morbidades(f_df)
    executar_etapa("categorizações descritivas", categorizacoes_descritivas, f_df)

    # --- Regressões principais SSWS/LRI vs morbidade ---
    regressao_simples_com_scatter(
        f_df, "SSWS", "scatter_ssws_morbidades",
        "Relação entre Número de Multimorbidades e SSWS")
    regressao_simples_com_scatter(
        f_df, "LRI", "scatter_lri_morbidades",
        "Relação entre Número de Multimorbidades e LRI")
    regressoes_ols_por_categoria(f_df)

    # --- Curvas ROC ---
    curvas_roc(f_df, "LRI", "roc_lri_categorias",
               "Curva ROC — LRI vs Categorias de Morbidade", "roc_lri_categorias")
    curvas_roc(f_df, "SSWS", "roc_ssws_categorias",
               "Curva ROC — SSWS vs Categorias de Morbidade", "roc_ssws_categorias")
    executar_etapa("comparação de AUC por corte", comparar_auc_por_corte, f_df)

    # --- Regressões exploratórias de variáveis secundárias ---
    executar_etapa("regressões exploratórias", regressoes_exploratorias, f_df)

    # --- Descritivas finais, VIF e tabelas-resumo ---
    descritivas_finais(f_df)
    executar_etapa("teste VIF", teste_vif, f_df)
    tabelas_resumo_regressoes(f_df)

    # --- Persistência dos resultados completos e resumos textuais ---
    salvar_coeficientes_ols()
    salvar_resumos()
    print(f"\nWave {wave} concluída.")


def main():
    garantir_pastas()
    configurar_estilo()
    for wave in WAVES:
        rodar_wave(wave)
    print(f"\nConcluído (waves {WAVES}). Figuras em: {IMAGES_DIR}\nTabelas em: {TABLES_DIR}")


if __name__ == "__main__":
    main()
