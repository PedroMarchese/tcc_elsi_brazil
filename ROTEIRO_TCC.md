# ROTEIRO DE REDAÇÃO — TCC ELSI (SSWS/LRI × multimorbidade)

Roteiro crítico e detalhado para escrever a monografia, **na ordem de redação** e
com o mapeamento de cada seção às saídas já geradas (`tables/`, `images/`) e às
observações de `OBSERVACOES.md` (citadas como **§n**). Documento de planejamento —
não é o texto final.

## Decisões editoriais fixadas (não reabrir sem motivo)
1. **Formato:** monografia ABNT completa — capítulos: Introdução · Referencial
   Teórico · Metodologia · Resultados · Discussão · Conclusão · Referências ·
   Apêndices.
2. **Ondas:** **duas transversais independentes** (Wave 1 e Wave 2 lado a lado;
   W2 como replicação de W1). Há **uma** subseção de comparação temporal, mas
   **descritiva e cautelosa** — não há pareamento por indivíduo (o código não usa
   `id`) e a queda da SSWS entre ondas pode ser artefato de medição (**§1.3**).
   Proibido afirmar efeito longitudinal/causal entre ondas.
3. **Ponderação:** análise **não-ponderada**; a ausência de pesos
   (`peso_calibrado`/`estrato`/`upa`) entra como **limitação** (**§5.1**). Não
   refazer com survey design neste ciclo.
4. **Área/ênfase:** Fisioterapia com ênfase **populacional**. A biomecânica
   (pêndulo invertido, número de Froude, OWS) aparece **só** no Referencial para
   justificar o LRI e na Discussão para levantar hipóteses — nunca como foco.

## Ordem recomendada de ESCRITA (≠ ordem do documento)
Escreva **Metodologia → Resultados → Discussão → Introdução → Conclusão →
Referencial → Resumo/Abstract**. Métodos e Resultados são os mais factuais e
ancoram o resto; o Resumo se escreve por último.

---

# REGRAS DE OURO (valem para todo o texto)
Releia esta lista antes de cada seção de resultados/discussão.

1. **Sempre reportar tamanho de efeito junto do p.** Com N de milhares, quase tudo
   dá p < 0,001; isso **não** é relevância clínica (**§2.2**). Cada associação leva
   β (ou OR), IC 95% e R² (ou pseudo-R²) ao lado do p.
2. **Não confundir significância com magnitude.** A frase-modelo é: *"associação
   estatisticamente significativa, porém de magnitude pequena (R² = …)"*.
3. **Modere o p por causa da não-ponderação.** Sem o desenho complexo os
   erros-padrão tendem a ser subestimados (**§5.1**); a onipresença de p < 0,001
   pode ser, em parte, artefato. Evite linguagem triunfalista.
4. **AUC < 0,5 não é "pior que o acaso".** Significa direção protetora (velocidade
   alta prediz *menos* morbidade); a AUC "corrigida" é 1 − AUC (**§3.2**). Diga
   isso na legenda de toda figura ROC.
5. **LRI ≈ SSWS reescalado** (R² de `LRI~SSWS` ≈ 0,99; **§2.3**). Reporte a SSWS
   como medida primária (m/s, interpretação física direta) e o LRI como
   complementar; **nunca** os dois no mesmo modelo (colinearidade quase perfeita).
6. **Sempre informar o N de cada modelo.** O ajuste por escolaridade reduz o N por
   *listwise deletion* (W1 8.746→7.327; W2 7.205→6.336; **§2.10**, RESUMO §5).
   Mostre N do cru e do ajustado.
7. **Desenho transversal ⇒ associação, não causa.** Não escrever "a multimorbidade
   reduz a velocidade"; escrever "está associada a menor velocidade".
8. **Terminologia fixa e em pt-BR:** SSWS = velocidade de marcha auto-selecionada;
   LRI = índice de reabilitação locomotor; OWS = velocidade ótima de caminhada;
   `n_morbidades` = nº de morbidades. Defina cada sigla na 1ª aparição.
9. **Numeração ABNT:** Tabela N e Figura N numeradas sequencialmente no texto (não
   por wave). Toda tabela/figura precisa ser citada no corpo antes de aparecer.

---

# 0. ELEMENTOS PRÉ-TEXTUAIS (escrever por último)
- **Resumo (pt) + Abstract (en):** contexto, objetivo, método (ELSI, 2 ondas,
  transversal, N), principais resultados (direção + magnitude + ressalva de
  efeito pequeno), conclusão. 3–5 palavras-chave (ex.: envelhecimento;
  multimorbidade; velocidade de marcha; ELSI-Brasil; fisioterapia).
- Capa, folha de rosto, sumário, listas de tabelas/figuras/siglas — padrão ABNT.

---

# 1. INTRODUÇÃO
Estrutura em funil (geral → específico → lacuna → objetivo). Ênfase populacional.

1. **Envelhecimento e multimorbidade no Brasil.** Magnitude do envelhecimento
   (¼ da população ≥ 50 anos; resumo ELSI §3). Multimorbidade como desafio de
   saúde pública.
2. **Declínio funcional e marcha.** Velocidade de marcha como marcador
   consagrado de saúde/funcionalidade no idoso (sinal vital geriátrico).
3. **Do SSWS ao LRI.** Limitação da velocidade bruta (confundida por estatura);
   o LRI normaliza pelo tamanho corporal — apresentar em **uma frase** aqui (o
   detalhe biomecânico vai ao Referencial).
4. **Lacuna.** Precedente do próprio ELSI associando multimorbidade a incapacidade
   em AVD (Macinko et al., 2021; resumo ELSI §8/§10), mas pouca evidência
   populacional ligando multimorbidade a SSWS/LRI especificamente.
5. **Objetivo geral:** investigar a associação de SSWS e LRI com o nº de
   morbidades em idosos do ELSI-Brasil, em duas ondas.
   **Específicos:** (a) descrever marcha e multimorbidade na amostra; (b) estimar
   a associação contínua (OLS, cru e ajustado); (c) avaliar por faixas de
   morbidade e por grupos de doença; (d) avaliar a capacidade discriminativa
   (ROC/AUC); (e) comparar os achados entre as ondas.
6. **Hipótese:** maior multimorbidade associa-se a menor SSWS e menor LRI
   (direção negativa); plausibilidade pelo mecanismo pendular (Referencial).

> Crítico: a Introdução não promete análise causal nem ponderada. Já anuncia que
> são duas transversais (replicação), não um seguimento.

---

# 2. REFERENCIAL TEÓRICO
Aqui mora a biomecânica — apenas para fundamentar o LRI.

- **2.1 Envelhecimento populacional e multimorbidade.** Conceito de
  multimorbidade; contexto brasileiro (ELSI).
- **2.2 Velocidade de marcha como marcador funcional.** SSWS/velocidade usual;
  por que prediz desfechos em idosos.
- **2.3 Fundamentação biomecânica do LRI** (base: `papers/RESUMO_LRI_*`):
  pêndulo invertido, número de Froude (Fr = v²/(g·LLL)), OWS = √(0,25·g·LLL),
  curva custo-velocidade em U, e **LRI = 100·SSWS/OWS**. Interpretação clínica
  (LRI alto ≈ marcha ótima; baixo ≈ maior potencial de reabilitação).
- **2.4 Evidências prévias.** Marcha × morbidade/incapacidade; aplicações do LRI
  (ex.: Parkinson + Nordic walking, Monteiro 2016, resumo LRI §5).
- **2.5 O ELSI-Brasil.** Desenho, representatividade nacional, harmonização HRS
  (base: `papers/RESUMO_ELSI_*`).

---

# 3. METODOLOGIA
Escreva no passado, voz impessoal. Permita reprodução.

- **3.1 Delineamento.** Estudo transversal, analisando **duas ondas independentes**
  do ELSI-Brasil (Wave 1, 2015–16; Wave 2, 2019–21). Deixar explícito: **sem
  pareamento longitudinal**.
- **3.2 Fonte de dados e participantes.** ELSI-Brasil (citar Lima-Costa et al.,
  2023): coorte nacional, ≥ 50 anos, 70 municípios. N bruto por onda (9.412 /
  9.949).
- **3.3 Elegibilidade e exclusões.** Derivação da marcha e cutoff
  `MAX_WALKING_SPEED = √(0,5·g·LLL)` (exclui SSWS implausível). **N elegível:
  W1 = 8.746; W2 = 7.205.** → **Fluxograma (Figura 1)** já gerado em
  `images/fluxograma_elegibilidade.png` (painel duplo W1|W2) e versões por onda
  (`_w1`/`_w2`); script `codigos/gerar_fluxograma.py`. Etapas: W1 9.412 → altura
  9.043 → marcha 8.795 → elegível 8.746; W2 9.949 → 8.394 → 7.249 → 7.205.
- **3.4 Variáveis.** (apoiar em `VARIAVEIS.md`)
  - *Preditores:* **SSWS** (teste de marcha de 3 m, 2 passadas; derivação difere
    entre ondas — W2 em segundos, W1 reconstruída de min/s/centésimos, validada,
    **§1.1**). **LRI** = 100·SSWS/OWS; **OWS** de LLL = 0,54×altura; altura
    normalizada para cm (W1 em m, W2 em cm, **§1.2**). Declarar **LLL aproximado
    pela altura** (**§5.3**).
  - *Desfecho:* **`n_morbidades`** = soma de 21 doenças crônicas autorreferidas
    (listar as 21 e os 3 grupos — tabela do `VARIAVEIS.md` §1.7). Desfechos
    binários por faixa (<2, =2…=6, ≥7) e por grupo de doença.
  - *Covariáveis (modelos ajustados):* idade, sexo, **escolaridade**
    (`C(escolaridade_modelo)`, fator categórico, referência = menor nível;
    código 9 = NS/NR → NaN, distinto da descritiva, **§2.10**, RESUMO §5).
- **3.5 Análise estatística.**
  - Descritivas (média/DP, distribuições).
  - Normalidade por **Anderson-Darling** (explicar: testa aderência à normal;
    rejeição = desvio; **§4.1**). Lembrar que OLS exige normalidade dos
    *resíduos*, não da variável; N grande ⇒ TCL protege.
  - **OLS** (cru e ajustado) para associação contínua.
  - **Regressão logística** para desfechos binários (faixas e grupos).
  - **ROC/AUC** para capacidade discriminativa.
  - **VIF** (colinearidade; **§2.9**) e **Breusch-Pagan** (heterocedasticidade;
    **§2.11** — decisão: **erros-padrão convencionais** em todos os modelos,
    justificada empiricamente por HC3 ≈ convencional).
  - α = 0,05. Software: Python 3.13 (pandas, numpy, scipy, statsmodels,
    scikit-learn). Declarar **análise não-ponderada** (justificativa na Discussão/
    Limitações, **§5.1**).
- **3.6 Aspectos éticos.** Aprovações do ELSI (FIOCRUZ-MG, protocolos no resumo
  ELSI §11); dados de acesso público mediante registro; TCC usa dados secundários
  anonimizados.

---

# 4. RESULTADOS
Ordem do mais geral (quem é a amostra) ao mais específico (discriminação),
fechando com a comparação entre ondas. **Para cada onda**, reporte W1 e W2; a
síntese comparativa fica em 4.7. Cada subseção abaixo traz: *Tabela/Figura →
o que afirmar → §obs a incorporar → cuidado.*

### 4.1 Caracterização da amostra (Tabela 1)
- **Fonte:** `descritivas_resumo_w{1,2}.csv`, `medias_desvios_w{1,2}.csv`.
- **Afirmar:** idade, sexo, escolaridade; SSWS, LRI, OWS (médias/DP);
  `n_morbidades` médio; N elegível por onda. SSWS 0,74 (W1) vs 0,59 m/s (W2);
  LRI 50,7% vs 40,5%; OWS ≈ 1,45 nos dois (**§1.3**).
- **Pronto:** Tabela 1 consolidada (colunas W1/W2) em APA gerada em
  `tables/tabelas_apa/tabela1_caracterizacao_apa.xlsx` (script
  `codigos/gerar_tabela1_caracterizacao.py`). Inclui demografia (idade, sexo,
  escolaridade), antropometria/marcha (altura, LLL, OWS, SSWS, LRI) e morbidade
  (n_morbidades, multimorbidade, grupos 0/1/2).

### 4.2 Distribuição da marcha e da multimorbidade
- **Figuras:** `hist_velocidade`, `boxplot_velocidade`, `hist_variaveis_marcha`,
  `qqplot_velocidade`, `hist_morbidades` (sufixo _w1/_w2).
- **Tabelas:** `descritivas_marcha`, `distribuicao_morbidades`,
  `contagem_categorias_morbidade`.
- **Afirmar:** forma das distribuições; **assimetria positiva da SSWS** e
  rejeição de normalidade por Anderson-Darling (W1 mais assimétrica; **§4.1**).
- **Cuidado:** apresentar a não-normalidade como **descrição**, não como falha —
  remeter ao tratamento na 3.5 (resíduos/TCL; SE convencional, **§2.11**).

### 4.3 Associação contínua SSWS/LRI × nº de morbidades (OLS) — RESULTADO CENTRAL
- **Tabelas APA:** `tabelas_apa/ols_w1_apa.xlsx` (Tabela 2),
  `ols_w2_apa.xlsx` (Tabela 4 ou conforme numeração). **Figuras:**
  `scatter_ssws_morbidades`, `scatter_lri_morbidades`.
- **Afirmar:** associação **negativa e significativa** nas duas ondas (cru:
  β_SSWS por morbidade ≈ −0,024 W1 / −0,014 W2; **§2.1**); **R² baixo** (SSWS:
  0,039 W1 / 0,009 W2 — <4% e <1% da variância; **§2.2**); **atenuação ~50–60%
  após ajuste** por idade/sexo, com R² subindo por conta das covariáveis
  (**§2.4**); persistência após **escolaridade** (**§2.10**).
- **Reportar também:** **VIF** baixos (todos < 1,1; **§2.9**) e **Breusch-Pagan**
  (heterocedasticidade presente, conclusões estáveis; **§2.11**).
- **Cuidado:** este é o ponto de maior risco de oversell — aplicar Regras de Ouro
  1–3 e 6 (efeito pequeno; N do cru vs ajustado; moderar p). Nota sobre LRI ≈ SSWS
  (**§2.3**): apresentar LRI como confirmação, não como ganho.

### 4.4 Associação por grupos de doença
- **Tabela:** `ols_coef_grupos_morbidade_w{1,2}.csv` (somas por grupo, cru/ajust.).
- **Afirmar:** grupo 0 (neuro/oftalmo/musculoesq.) significativo na W1 mas
  **perde significância na W2** (p ≈ 0,065–0,067); grupos cardiorrespiratório e
  "outras" mantêm-se nas duas ondas, com magnitude menor na W2 (**§2.5**).
- **Cuidado:** não vender o achado como uniforme entre grupos/ondas.

### 4.5 Associação por faixas de morbidade (logística)
- **Tabelas APA:** `tabelas_apa/logistica_w1_apa.xlsx`,
  `logistica_w2_apa.xlsx`.
- **Afirmar:** **padrão dose-resposta não-monotônico**: SSWS protetora para
  < 2 morbidades (OR > 1; W1 ≈ 3,50) e cada vez mais negativa nas faixas altas
  (≥4…≥7; W1 OR de 0,47 a 0,15); faixas intermediárias (=2, =3) fracas/ns
  (**§2.6**). Efeito concentrado nos **extremos** do espectro.
- **Cuidado:** explicar o OR (chance relativa) na 1ª aparição; conectar este
  padrão ao comportamento das ROC (4.6).

### 4.6 Capacidade discriminativa (ROC/AUC)
- **Figuras:** `roc_ssws_categorias`, `roc_lri_categorias` (_w1/_w2).
  **Tabelas:** `roc_ssws_categorias`, `roc_lri_categorias`,
  `auc_comparacao_cortes`, `prevalencia_cutoffs_ssws`.
- **Afirmar:** discriminação **fraca isolada** (AUC ≈ 0,5 na maioria das faixas;
  **§3.1**); AUC < 0,5 = direção protetora (**§3.2**); **SSWS ≈ LRI** em AUC
  (**§3.3**); ganho vem do **ajuste por idade/sexo** (AUC 0,64–0,68), não da
  marcha (**§3.4**); discriminação levemente maior na W1 (**§3.5**).
- **Cuidado:** legenda de toda ROC deve explicar a leitura de AUC < 0,5
  (Regra de Ouro 4).

### 4.7 Comparação entre as ondas (descritiva e cautelosa)
- **Afirmar (síntese):** SSWS e LRI menores na W2; associação e discriminação um
  pouco mais fortes na W1 (**§2.2/§3.5**); grupo neuro perde força na W2
  (**§2.5**).
- **Cuidado (essencial):** **não interpretar como tendência temporal pura.** A
  queda de SSWS (~0,15 m/s) excede o esperado por envelhecimento e pode refletir
  **diferença de protocolo/medição entre ondas** + recomposição amostral
  (*refreshment*); **sem pareamento por indivíduo** (**§1.3**). Enquadrar como
  "replicação com diferenças de magnitude", levantando a medição como hipótese —
  a confirmar na Discussão.

### 4.8 Análises exploratórias (opcional / apêndice)
- **Tabela:** `ols_coef_exploratorias_w{1,2}.csv`.
- **Afirmar:** consistência interna — força de preensão ↔ menos morbidades;
  queda ↔ mais morbidades; melhor equilíbrio (mf30) ↔ maior SSWS (**§2.7**).
- **Cuidado:** `mf31` (semi-tandem) tem codificação divergente entre ondas
  (**§2.8**) — **não** usar para comparação entre ondas; manter como checagem de
  plausibilidade, de preferência em apêndice.

---

# 5. DISCUSSÃO
Espelha os Resultados, mas interpreta. Ênfase populacional/fisioterapêutica;
biomecânica só como hipótese.

- **5.1 Síntese dos achados.** Responder à hipótese: a associação marcha ↔
  multimorbidade **existe, é negativa, significativa, mas pequena** e em parte
  conduzida por idade/sexo (**§2.1/§2.2/§2.4**).
- **5.2 Significância × relevância clínica.** Discutir R² baixo: marca associação
  populacional real, mas pouco poder explicativo individual. Aqui cabe a
  **hipótese biomecânica** (mecanismo pendular / custo metabólico: patologias
  deslocam o indivíduo para o ramo descendente da curva custo-velocidade) como
  *possível* mecanismo, sem afirmar causalidade.
- **5.3 LRI não supera a SSWS.** Interpretar **§2.3/§3.3**: como o LLL (derivado
  da altura) varia pouco entre idosos, a normalização agrega pouco; em amostra
  populacional a SSVS bruta basta. Conectar à aproximação do LLL (**§5.3**).
- **5.4 Efeito nos extremos e papel de idade/sexo.** Discutir **§2.6/§3.4**: a
  marcha discrimina bem os extremos do espectro, mal a zona intermediária; o
  poder classificatório vem majoritariamente de idade/sexo. Implicação prática
  (fisioterapia): SSWS é triagem útil nos extremos, não classificador de
  multimorbidade.
- **5.5 Diferenças entre ondas.** Interpretar **§1.3/§2.5/§3.5** com cautela:
  provável contribuição de medição/protocolo + envelhecimento + refreshment;
  reforçar ausência de pareamento. **Não** concluir tendência temporal.
- **5.6 Comparação com a literatura.** Macinko et al. (2021, multimorbidade ↔ AVD
  no próprio ELSI); literatura de velocidade de marcha como marcador; estudos de
  LRI (Parkinson). Situar magnitude dos achados.
- **5.7 Limitações.** (a) **Não-ponderação** — subestima SE, pode inflar
  significância (**§5.1**); (b) **autorrelato** das morbidades (**§5.2**);
  (c) **LLL aproximado** pela altura (**§5.3**); (d) **transversal** ⇒ sem
  causalidade; (e) **medição entre ondas** (**§1.3**); (f) *listwise deletion*
  reduz N nos ajustados (**§2.10**).
- **5.8 Implicações e perspectivas.** Uso da SSWS na prática fisioterapêutica
  populacional; recomendação metodológica de **reanálise ponderada** (survey
  design) em trabalhos futuros.

---

# 6. CONCLUSÃO
Curta, sem dados novos. Retomar o objetivo e responder: há associação negativa e
significativa de SSWS/LRI com a multimorbidade nas duas ondas, de **magnitude
pequena** e concentrada nos extremos; o **LRI não acrescenta** sobre a SSWS nesta
população; a marcha isolada **não classifica** multimorbidade. Mensagem prática
(fisioterapia) + ressalva de não-ponderação. Uma frase sobre a replicação entre
ondas (consistência qualitativa, com diferenças de magnitude a esclarecer).

---

# 7. PÓS-TEXTUAIS
- **Referências (ABNT):** mínimo obrigatório — Lima-Costa et al. (2023, ELSI);
  Peyré-Tartaruga & Monteiro (2016, LRI); Macinko et al. (2021); Alexander (2005);
  Cavagna et al. (1977); Salbach et al. (2015); Monteiro et al. (2016). (Dados
  completos nos resumos em `papers/`.)
- **Apêndices:** tabelas APA completas (`tables/tabelas_apa/`), saídas completas
  das OLS (`ols_coeficientes_completo`), VIF, ROC detalhada.

---

# PENDÊNCIAS QUE BLOQUEIAM/ATRASAM A REDAÇÃO
Ordenadas por prioridade.

| # | Pendência | Impacto | Onde |
|---|-----------|---------|------|
| ~~1~~ | ~~**Tabela 1 (caracterização) consolidada W1×W2** em APA~~ | — | ✅ FEITO: `tables/tabelas_apa/tabela1_caracterizacao_apa.xlsx` |
| ~~2~~ | ~~**Fluxograma de elegibilidade (Figura 1)**~~ | — | ✅ FEITO: `images/fluxograma_elegibilidade.png` |
| 3 | Versões **APA das demais tabelas** (descritivas extras, ROC/AUC, VIF) | Etapa 4 do CLAUDE.md (parcial) | só OLS/logística + Tabela 1 têm APA |
| 4 | **Numeração final** de tabelas/figuras no corpo (ABNT) | Todo o texto | as APA de regressão ainda numeram a partir de "Tabela 1" — renumerar (Tabela 1 = caracterização) |
| 5 | Confirmar rótulos das categorias 1–3 de `e21` (escolaridade) | Metodologia 3.4 e nota da Tabela 1 | VARIAVEIS.md "pontos a confirmar" |
| 6 | Decidir o que vai ao **corpo** vs **apêndice** (exploratórias, OLS completas) | Resultados | reduzir ruído no corpo |

---

# MAPA RÁPIDO: SEÇÃO → SAÍDAS → OBSERVAÇÕES
| Seção | Tabelas/Figuras | §OBSERVACOES |
|-------|------------------|--------------|
| 4.1 Amostra | descritivas_resumo, medias_desvios | §1.3 |
| 4.2 Distribuições | hist_*, boxplot_*, qqplot_*, distribuicao_morbidades | §4.1 |
| 4.3 OLS contínua | tabelas_apa/ols_*, scatter_* , vif_* | §2.1–2.4, §2.9–2.11, §2.3 |
| 4.4 Grupos doença | ols_coef_grupos_morbidade | §2.5 |
| 4.5 Faixas (logística) | tabelas_apa/logistica_* | §2.6 |
| 4.6 ROC/AUC | roc_*_categorias, auc_comparacao_cortes | §3.1–3.5 |
| 4.7 Entre ondas | (síntese) | §1.3, §2.2, §2.5, §3.5 |
| 4.8 Exploratórias | ols_coef_exploratorias | §2.7, §2.8 |
| 5 Discussão | — | §2.2/2.3/2.4/2.6, §3.4, §1.3, §5.1–5.3 |
