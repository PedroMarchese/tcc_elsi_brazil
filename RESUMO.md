# RESUMO — TCC ELSI (Wave 2)

Resumo do trabalho realizado nesta sessão sobre a análise estatística do
ELSI-Brasil (onda 2), que investiga a associação entre velocidade de marcha
auto-selecionada (SSWS) e o Índice de Reabilitação Locomotora (LRI) com a
multimorbidade em idosos.

---

## 1. Configuração do projeto

- Criado `CLAUDE.md` com a descrição e os objetivos do projeto.
- Criadas as pastas de saída `images/` (gráficos) e `tables/` (tabelas).
- Criado `requirements.txt` com as dependências (pandas, numpy, scipy,
  scikit-learn, statsmodels, matplotlib, seaborn).
- Criado `.gitignore` para ignorar `.venv/` e cache do Python.
- Criado ambiente virtual `.venv` com **Python 3.13** e dependências instaladas.

---

## 2. Refatoração do código (Etapa 1)

Ponto de partida: `codigos/elsi_tcc_wave2.py`, um export do Google Colab com
vários problemas (typo `Qfrom`, `drive.mount`/`display` específicos do Colab,
leitura de dados do Google Drive, funções duplicadas, bloco morto com nomes de
colunas inexistentes, e nenhum resultado salvo em disco).

O código foi refatorado para um **script único organizado**, preservando toda a
lógica estatística. Principais mudanças:

- Backup do original em `codigos/elsi_tcc_wave2_colab_original.py`.
- Remoção de todo código específico do Colab e do typo inicial.
- **Caminhos locais e portáveis** (resolvidos a partir da pasta do script):
  lê `banco_elsi/ELSI_wave_2.csv`, salva figuras em `images/` e tabelas em
  `tables/`.
- Eliminação de duplicações (`extrair_metricas_modelo` definida 2×, grupos de
  doenças, relatório de variáveis embutido em string).
- Correção do bloco de verificação que usava nomes de colunas inexistentes.
- Consolidação de `rodar_ols`/`rodar_logistica` num núcleo comum e das
  regressões exploratórias em `ols_simples()`.
- Cada gráfico em sua própria figura, salvo via `plt.savefig` (backend `Agg`).
- Etapas exploratórias protegidas por `executar_etapa` (uma falha não aborta
  o pipeline).

A sequência original de filtros na derivação da marcha foi mantida fiel para
não alterar o N nem os resultados (7.205 participantes elegíveis de 9.949).

---

## 3. Execução e correção de erros

- Ambiente criado e dependências instaladas.
- Erro corrigido: `Series.reset_index(names=...)` não existe no pandas 3.0 —
  substituído por construção explícita do DataFrame.
- Script roda de ponta a ponta com **exit code 0**, sem etapas falhadas.
- Observação (não é erro): `FutureWarning` do SciPy 1.18 em `stats.anderson`;
  usamos apenas `ad.statistic`, que não é afetado.

---

## 4. Coluna de intercepto nas tabelas-resumo

A pedido, foi adicionada a coluna **`intercepto`** (β₀) às tabelas-resumo das
regressões (`regressoes_ols.csv`, `interpretacao_ols.csv` e equivalentes
logísticas). Antes, a coluna `coef` trazia apenas o β do preditor e o
intercepto não era exportado.

---

## 5. Distinção entre código 9 e NaN na variável de escolaridade (`e21`)

A variável `e21` (grau de instrução concluído) usa dois tratamentos distintos
dependendo do contexto:

- **Código 9 (NS/NR — não sabe / não respondeu):** não representa um nível de
  escolaridade real. Na análise descritiva é mantido como categoria `9` em
  `escolaridade_categorizada`, para transparência da distribuição da amostra.
- **`NaN`:** nos modelos de regressão, o código 9 é convertido para `NaN` em
  `escolaridade_modelo`. Isso garante que respondentes sem informação de
  escolaridade sejam excluídos por *listwise deletion*, sem distorcer a
  estimativa dos coeficientes de ajuste.

Os demais valores ausentes (i.e., não-resposta por outros motivos) já chegam
como `NaN` diretamente do CSV e recebem o mesmo tratamento.

Consequência prática: o N dos modelos **ajustados** é menor que o dos **crus**
(W1: 8.746 → 7.327; W2: 7.205 → 6.336).

---

## 6. Exportação completa das OLS

A pedido, passou-se a exportar a **saída completa de cada modelo OLS** (uma
linha por termo: intercepto, preditor e, nos modelos ajustados, `idade`, `sexo`
e os níveis de escolaridade), com `coef`, `std_err`, `stat` (t), `p_value`, IC95%
e métricas de ajuste (`r_squared`, `aic`, `bic`). Todos os modelos usam
**erros-padrão convencionais** (não-robustos) — ver OBSERVACOES.md §2.11.

Novos arquivos em `tables/`:

| Arquivo | Conteúdo |
|---|---|
| `ols_coeficientes_completo.csv` | Todos os modelos OLS num único arquivo (coluna `analise`) |
| `ols_coef_principais.csv` | SSWS~n_morbidades, LRI~n_morbidades, LRI~SSWS |
| `ols_coef_por_categoria.csv` | cada `morbidades_*` ~ SSWS/LRI |
| `ols_coef_grupos_morbidade.csv` | n_morbidades e `soma_grupo_*` ~ SSWS/LRI (crus e ajustados) |
| `ols_coef_exploratorias.csv` | handgrip, queda, atividade física, mf30, mf31 |

---

## 7. Roteiro de redação do TCC, Tabela 1 e fluxograma

- Criado `ROTEIRO_TCC.md` (raiz) — roteiro crítico de redação da monografia ABNT,
  na ordem de escrita, mapeando cada seção às tabelas/figuras e às observações de
  `OBSERVACOES.md`. Decisões fixadas: duas transversais independentes (comparação
  temporal cautelosa), análise não-ponderada como limitação, ênfase populacional
  (Fisioterapia).
- Criado `codigos/gerar_tabela1_caracterizacao.py` → **Tabela 1** (caracterização
  da amostra, W1×W2) em APA: `tables/tabelas_apa/tabela1_caracterizacao_apa.xlsx`.
  Reutiliza a derivação do script principal (N idêntico: W1 8.746; W2 7.205).
- Criado `codigos/gerar_fluxograma.py` → **Figura 1** (fluxograma de elegibilidade)
  em `images/fluxograma_elegibilidade.png` (painel duplo) + versões `_w1`/`_w2`.
  Contagens (com tie-out por `assert` contra o N do pipeline): W1 9.412 → altura
  9.043 → marcha 8.795 → elegível 8.746; W2 9.949 → 8.394 → 7.249 → 7.205.
- **Correção de dado:** a variável `sexo` é codificada **0 = Feminino / 1 =
  Masculino** (não 1/2). Verificado pelo bloco M (saúde da mulher): só `sexo = 0`
  o responde (W2: 5.306 vs 0). `VARIAVEIS.md` corrigido. Implicação: nos modelos
  ajustados, o coeficiente de `sexo` é o efeito de ser **masculino** (ref. = feminino);
  o valor do coeficiente não muda, apenas sua leitura.

---

## Saídas geradas

### `images/` (11 figuras por onda + 1 painel duplo)
`hist_velocidade`, `boxplot_velocidade`, `hist_variaveis_marcha`,
`qqplot_velocidade`, `hist_morbidades`, `scatter_ssws_morbidades`,
`scatter_lri_morbidades`, `roc_lri_categorias`, `roc_ssws_categorias`
(sufixos `_w1`/`_w2`) + `fluxograma_elegibilidade.png` (painel duplo W1|W2)
+ `fluxograma_elegibilidade_w1.png` / `_w2.png`.

### `tables/`
Descritivas, distribuição/contagem de morbidades, regressões OLS e logísticas
(resumo + saída completa), tabelas interpretadas, curvas ROC, comparação de AUC
por corte, VIF, prevalências de cutoff, médias, e `resumos_modelos.txt` com os
`.summary()` completos.

### `tables/tabelas_apa/` (APA 7ª ed.)
`tabela1_caracterizacao_apa.xlsx` · `ols_w1_apa.xlsx` · `ols_w2_apa.xlsx` ·
`logistica_w1_apa.xlsx` · `logistica_w2_apa.xlsx`.

---

## Estrutura atual do projeto

```
tcc_elsi/
├── CLAUDE.md
├── RESUMO.md                 (este arquivo)
├── ROTEIRO_TCC.md            (roteiro de redação da monografia)
├── VARIAVEIS.md              (mapeamento completo de variáveis — único)
├── OBSERVACOES.md            (observações estatísticas/metodológicas)
├── requirements.txt
├── .gitignore
├── banco_elsi/              (dados ELSI wave 1 e 2 + PDFs dos manuais)
├── codigos/
│   ├── elsi_tcc_wave2.py                  (script refatorado — fonte da verdade)
│   ├── elsi_tcc_wave2_colab_original.py   (backup do original)
│   ├── gerar_tabela1_caracterizacao.py    (Tabela 1 APA)
│   └── gerar_fluxograma.py               (Figura 1 — fluxograma de elegibilidade)
├── images/                  (gráficos exportados, sufixo _w1/_w2)
└── tables/                  (tabelas exportadas, sufixo _w1/_w2)
    └── tabelas_apa/         (tabelas em APA 7ª ed.)
```

## Como rodar

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python codigos\elsi_tcc_wave2.py
```

---

## Análise das duas ondas (Waves 1 e 2)

O script roda a **mesma análise para as duas ondas** num laço
(`WAVES = [1, 2]`), exportando todas as figuras e tabelas com sufixo `_w1`/`_w2`.

- **SSWS da Wave 1:** o banco da Wave 1 **não tem o tempo em segundos**
  (`mf35s`/`mf38s` são os da Wave 2). O tempo foi reconstruído da decomposição
  minutos/segundos/centésimos: medição 1 = `mf33`/`mf34`/`mf35`, medição 2 =
  `mf36`/`mf37`/`mf38`; `tempo_s = min·60 + s + centésimos/100`,
  `SSWS = média(3/tempo_s)`. Validado contra `mf35s`/`mf38s` (diferença ~1e-7).
  Sentinelas dos componentes: 8888/9666/9888/9999.
- **Altura (`mf13`):** Wave 1 vem em **metros**, Wave 2 em **cm**. Normalizada
  para cm em ambas (LLL médio ≈ 85,7 cm nas duas — confirma a correção).
- **`l10_2`** (tempo de atividade física) inexiste na Wave 1; etapas dependentes
  são puladas com aviso, sem abortar o pipeline.
- **N elegível:** Wave 1 = **8.746**; Wave 2 = **7.205** (Wave 2 inalterada).
- `ols_simples` ficou robusta a dados vazios / preditor constante.

Saídas médias (idosos ELSI): SSWS 0,74 m/s (W1) vs 0,59 m/s (W2);
LRI 50,7% (W1) vs 40,5% (W2); OWS ≈ 1,45 m/s nas duas.

---

## Checklist de pendências (atualizada 2026-06-26)

### Código / saídas
- [x] Refatorar notebook → script `elsi_tcc_wave2.py` (roda exit 0, 2 ondas)
- [x] Mapear variáveis → `VARIAVEIS.md` (único documento)
- [x] Exportar análises (CSV/PNG): OLS, logística, ROC, VIF, descritivas
- [x] Tabelas APA de regressão: `ols_w{1,2}_apa.xlsx`, `logistica_w{1,2}_apa.xlsx`
- [x] **Tabela 1** — caracterização da amostra W1×W2 APA: `tabela1_caracterizacao_apa.xlsx`
- [x] **Figura 1** — fluxograma de elegibilidade (painel duplo + individuais)
- [x] Roteiro de redação (`ROTEIRO_TCC.md`) com decisões editoriais e Regras de Ouro
- [x] Correção `sexo`: 0 = Feminino / 1 = Masculino (verificado por bloco M)
- [ ] **APA das demais tabelas**: descritivas extras, ROC/AUC, VIF
- [ ] **Renumerar** tabelas APA de regressão (Tabela 1 já é caracterização; OLS/logística → Tabelas 2–5)
- [ ] **Confirmar rótulos** das categorias 1–3 de `e21` (escolaridade) no codebook PDF

### Redação do TCC
- [ ] Metodologia (§3)
- [ ] Resultados (§4.1–4.8)
- [ ] Discussão (§5)
- [ ] Introdução (§1)
- [ ] Conclusão (§6)
- [ ] Referencial Teórico (§2)
- [ ] Resumo / Abstract (por último)
- [ ] Elementos pré/pós-textuais ABNT (capa, sumário, listas, referências)

### Decisões em aberto
- [ ] Decidir o que vai ao corpo vs. apêndice (exploratórias, OLS completas)
- [ ] Declarar limitação de não-ponderação na seção de metodologia
