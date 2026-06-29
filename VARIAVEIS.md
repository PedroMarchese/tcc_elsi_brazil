# VARIAVEIS.md — Mapeamento das Variáveis do ELSI-Brasil (Waves 1 e 2)

Documento de referência das variáveis do banco ELSI-Brasil usadas (e disponíveis)
no TCC. Mapeado por leitura dos questionários e do manual de medidas físicas em
`banco_elsi/`, cruzado com o uso efetivo no script `codigos/elsi_tcc_wave2.py`.

**Fontes (em `banco_elsi/`):**
- `Entrevista-individual-2019-21_wave_2.pdf` / `Entrevista-individual-2015-16_wave_1.pdf`
- `Entrevista-domiciliar-2019-21_wave_2.pdf` / `Entrevista-domiciliar-2015-16_wave_1.pdf`
- `Manual-de-medidas-fisicas.pdf` (define todas as variáveis `mf*`)
- Dados: `ELSI_wave_1.csv` (1.082 colunas) e `ELSI_wave_2.csv` (975 colunas)

**Organização deste documento:**
- **Parte 1** — variáveis **prioritárias** (as efetivamente usadas no script), com
  descrição completa: significado, categorias/unidade, códigos de ausência e papel.
- **Parte 2** — variáveis **derivadas** criadas no script.
- **Parte 3** — **mapa completo** de todos os módulos do banco (as demais variáveis),
  por bloco do questionário, com prefixo e contagem em cada wave.
- **Parte 4** — diferenças estruturais entre a Wave 1 e a Wave 2.

> **A análise usa a Wave 2.** A Wave 1 é mapeada em paralelo para referência e
> eventuais análises longitudinais.

---

## Convenção de códigos de ausência (missing) no ELSI

O ELSI usa códigos numéricos especiais para respostas não-válidas. Os mais comuns:

| Código | Significado |
|--------|-------------|
| `0` | Não / Nenhum (em itens de Sim/Não pode ser resposta válida) |
| `8`, `88`, `888`, `8888` | Não se aplica |
| `9`, `99`, `999` | Não sabe / Não respondeu |
| `666` / `9666` | Não tentou / não realizou (ex.: por achar arriscado, nos testes físicos) |
| `555` (preensão) | Não realizou / código de não-medida na força de preensão |

⚠️ Esses códigos **não são valores reais** — precisam ser convertidos para `NaN`
antes de qualquer cálculo. O script faz isso variável a variável (ver coluna
"Códigos tratados como ausentes" abaixo).

---

# PARTE 1 — Variáveis prioritárias (usadas no script)

## 1.1 Identificação e desenho amostral

Variáveis **derivadas do desenho da amostra** (não vêm do questionário; são
construídas pela equipe do ELSI). Existem nas **duas waves**.

| Variável | Descrição | Observação para a análise |
|----------|-----------|----------------------------|
| `id` / `id2` | Identificador único do indivíduo (W1 = `id`; W2 = `id2`) | Chave do participante |
| `iddom` / `iddom2` | Identificador único do domicílio | Liga indivíduo ↔ domicílio |
| `upa` | Unidade Primária de Amostragem (PSU / *cluster*) | **Cluster** do desenho amostral |
| `estrato` | Estrato amostral (geográfico) | **Estratificação** do desenho |
| `peso_calibrado` | **Peso amostral calibrado** de cada participante | **Peso** para análise ponderada |
| `regiao` | Macrorregião do Brasil | Covariável / estratificação |
| `zona` | Zona urbana ou rural | Covariável |
| `nmoradores` (W2) | Nº de moradores no domicílio | Contexto domiciliar |

> 📌 **Nota metodológica (ver `CLAUDE.md`).** As três variáveis `upa`, `estrato`
> e `peso_calibrado` são exatamente o que se precisa para uma **análise ponderada
> com desenho amostral complexo**. Elas **existem nas duas waves**. A análise atual
> do script é **não-ponderada** — incorporá-las é uma decisão metodológica em aberto.

## 1.2 Demográficas

| Variável | Wave | Descrição | Categorias / unidade | Uso no script |
|----------|------|-----------|----------------------|---------------|
| `idade` | W1, W2 | Idade do participante | anos (≥ 50) | Covariável de ajuste; filtro de elegibilidade (`mf31_dummy` para idade ≤ 69) |
| `sexo` | W1, W2 | Sexo do participante | **(0) Feminino / (1) Masculino** | Covariável de ajuste |

> Atenção (Wave 2): além de `idade`/`sexo` do entrevistado, existem `idade2..idade12`
> e `sexo2..sexo12`, que descrevem **os demais moradores do domicílio** (roster), não
> o participante. O script usa `idade` e `sexo` (o entrevistado).

> ⚠️ **Codificação de `sexo` verificada nos dados (não no codebook):** no CSV, `sexo`
> assume **0/1** (não 1/2). Verificação: somente quem tem `sexo = 0` respondeu o bloco
> M (saúde da mulher) — na Wave 2, 5.306 respostas para `sexo = 0` e **0** para
> `sexo = 1`. Logo **0 = Feminino, 1 = Masculino**. Consequência para os modelos
> ajustados: o coeficiente de `sexo` representa o efeito de **ser do sexo masculino**
> (1) em relação ao feminino (0, referência).

## 1.3 Marcha e antropometria (bloco MF — medidas físicas)

| Variável | Wave | Descrição | Unidade | Códigos ausentes | Uso no script |
|----------|------|-----------|---------|------------------|---------------|
| `mf13` | W1, W2 | **Altura** (média de medidas com estadiômetro) | cm | `888`, `999` | Base de `lower_limb_length` (LLL = 0,54 × altura) |
| `mf35s` | W1, W2 | Tempo do percurso de 3 m — **1ª passada** (consolidado em segundos) | s | `666`, `888`, `8888` | Velocidade 1 da marcha → `SSWS` |
| `mf38s` | W1, W2 | Tempo do percurso de 3 m — **2ª passada** (consolidado em segundos) | s | `666`, `888`, `8888` | Velocidade 2 da marcha → `SSWS` |

> **Confirmação no manual de medidas físicas:** o teste de caminhada de 3 m é feito
> **duas vezes**, pedindo ao participante que "ande na sua velocidade NORMAL de
> caminhada, da mesma forma como caminha na rua para ir a uma loja". Isso confirma
> que a velocidade derivada é a **SSWS (velocidade auto-selecionada / usual)**.
> As variáveis de origem no manual são `mf33/mf35` (1ª passada) e `mf36/mf38` (2ª),
> em centésimos de segundo; o banco traz as versões consolidadas em segundos
> (`mf35s`, `mf38s`), que são as usadas no cálculo.

## 1.4 Desempenho físico (bloco MF)

| Variável | Wave | Descrição | Unidade | Códigos ausentes | Uso no script |
|----------|------|-----------|---------|------------------|---------------|
| `mf27` | W1, W2 | Força de preensão manual — medida 1 | kg | `≥ 555` | Compõe `handgrip_mean` |
| `mf28` | W1, W2 | Força de preensão manual — medida 2 | kg | `≥ 555` | Compõe `handgrip_mean` |
| `mf29` | W1, W2 | Força de preensão manual — medida 3 | kg | `≥ 555` | Compõe `handgrip_mean` |
| `mf30` | W1, W2 | **Equilíbrio "pés lado a lado"** (parado, pés juntos), tempo até 10 s | s | `≥ 66` (cobre `9666`/`9888`/`9999`) | `mf30_dummy` |
| `mf31` | W1, W2 | **Equilíbrio semi-tandem** (um pé um pouco à frente do outro), tempo até 10 s | s | restrito a idade ≤ 69 | `mf31_dummy` |

> **Resolução da inconsistência registrada antes:** pelo manual, `mf30` é o teste de
> equilíbrio **com os pés lado a lado** (não "levantar/sentar da cadeira"). `mf31` é o
> equilíbrio **semi-tandem**. Ambos têm os códigos especiais `9666` (não tentou por
> achar arriscado), `9888` (recusou-se) e `9999` (incapacitado).

## 1.5 Estilo de vida (bloco L — comportamentos em saúde)

| Variável | Wave | Descrição | Categorias | Códigos ausentes | Uso no script |
|----------|------|-----------|-----------|------------------|---------------|
| `l9` | W1, W2 | Em quantos dias da última semana realizou **atividades físicas vigorosas** por ≥ 10 min contínuos | `0` Nenhum … `7` 7 dias; `9` NS/NR | `9` | `atividade_fisica_dummy` |
| `l10_2` | **Só W2** | Componente de **minutos** do tempo gasto por dia nas atividades vigorosas | minutos | `88`, `99` | `tempo_minutos_atividade_fisica` |

> ⚠️ **`l10_2` não existe na Wave 1** (confirmado nos cabeçalhos do CSV). O script já
> trata isso: se a coluna estiver ausente, `tempo_minutos_atividade_fisica = NaN`.
> Observação conceitual: `l9` refere-se a atividades **vigorosas** (não às moderadas,
> que estão em itens anteriores do bloco L).

## 1.6 Outras variáveis individuais

| Variável | Wave | Descrição | Categorias | Códigos ausentes | Uso no script |
|----------|------|-----------|-----------|------------------|---------------|
| `e21` | W1, W2 | **Nível de escolaridade** do entrevistado (grau concluído) | (1) sem instrução/fundamental incompleto … (4) ginásio completo, (5) colegial completo, (6) curso superior; (8) NA, (9) NS/NR | `9` (mapeado para categoria 9) | `escolaridade_categorizada` |
| `n18` | W1, W2 | Nos **últimos 12 meses**, teve alguma **queda**? | (0) Não, (1) Sim, (9) NS/NR | — | `queda_dummy` |

## 1.7 Doenças crônicas (bloco N) — base de `n_morbidades`

Todas seguem o mesmo formato: *"Algum médico já lhe disse que o(a) Sr(a) tem
[doença]?"* — **(0) Não, (1) Sim, (9) Não sabe/não respondeu** (o `9` vira `NaN`).
As **21 condições** abaixo existem nas **duas waves** e compõem a contagem de
multimorbidade. Os "grupos" são a estratificação por sistema usada no script.

| Código | Doença | Grupo no script |
|--------|--------|-----------------|
| `n9`  | Glaucoma | 0 — neuro/oftalmo/musculoesquelético |
| `n10` | Retinopatia diabética | 0 |
| `n11` | Degeneração macular | 0 |
| `n12` | Catarata | 0 |
| `n52` | AVC / derrame | 0 |
| `n56` | Artrite ou reumatismo | 0 |
| `n57` | Osteoporose | 0 |
| `n58` | Problema crônico de coluna | 0 |
| `n62` | Doença de Parkinson | 0 |
| `n63` | Doença de Alzheimer ou outra demência | 0 |
| `n28` | Hipertensão arterial (pressão alta) | 1 — cardiorrespiratório |
| `n46` | Infarto do miocárdio | 1 |
| `n48` | Angina do peito | 1 |
| `n50` | Insuficiência cardíaca | 1 |
| `n54` | Asma | 1 |
| `n55` | Enfisema / bronquite crônica / DPOC | 1 |
| `n35` | Diabetes mellitus | 2 — outras |
| `n44` | Dislipidemia (colesterol/triglicérides altos) | 2 |
| `n59` | Depressão | 2 |
| `n60` | Câncer | 2 |
| `n61` | Insuficiência renal crônica | 2 |

> **Total: 21 condições.** `n_morbidades` = soma das que têm valor `1`.

---

# PARTE 2 — Variáveis derivadas no script

Criadas em `codigos/elsi_tcc_wave2.py` a partir das variáveis acima. **Não existem
no banco bruto.**

## 2.1 Marcha e índices locomotores

| Variável | Fórmula / regra | Papel |
|----------|------------------|-------|
| `tc_3m_v_media` | `(3/mf35s + 3/mf38s) / 2` | Velocidade média dos 3 m (m/s) |
| `SSWS` | `tc_3m_v_media` alinhada ao df e filtrada | **Preditor primário** (m/s) |
| `lower_limb_length` | `0,54 × mf13` (altura) | Comprimento do membro inferior (cm) |
| `OWS` | `√(0,25 · g · LLL/100)` | Velocidade ótima de caminhada (m/s) |
| `MAX_WALKING_SPEED` | `√(0,5 · g · LLL/100)` | Cutoff: exclui `SSWS > MAX` |
| `LRI_decimal` | `SSWS / OWS` | Intermediária |
| `LRI` | `LRI_decimal × 100` | **Preditor primário** (Índice de Reabilitação Locomotor, %) |

## 2.2 Multimorbidade

| Variável | Regra | Papel |
|----------|-------|-------|
| `n_morbidades` | Soma das 21 doenças `n*` = 1 | **Desfecho** (contagem) |
| `morbidades_menor_que_2` | `n_morbidades < 2` | Desfecho binário |
| `morbidades_igual_a_2` … `_igual_a_6` | `== 2 … == 6` | Desfechos binários |
| `morbidades_maior_ou_igual_a_7` | `>= 7` | Desfecho binário |
| `grupo_0/1/2_*` | `max` das doenças do grupo | Desfecho binário por sistema |
| `soma_grupo_0/1/2_*` | `sum` das doenças do grupo | Desfecho contagem por sistema |

## 2.3 Variáveis secundárias / exploratórias

| Variável | Derivada de | Regra |
|----------|-------------|-------|
| `handgrip_mean` | `mf27`, `mf28`, `mf29` | Média (≥ 555 → NaN) |
| `queda_dummy` | `n18` | `n18 == 1` → 1 |
| `atividade_fisica_dummy` | `l9` | `0`→0, `9`→NaN, `1–7` mantidos |
| `tempo_minutos_atividade_fisica` | `l9`, `l10_2` | `dummy × l10_2` (W2; NaN se `l10_2` ausente) |
| `mf30_dummy` | `mf30` | `mf30` se `< 66`, senão NaN |
| `mf31_dummy` | `mf31`, `idade` | `mf31` se `idade ≤ 69`, senão NaN |
| `escolaridade_categorizada` | `e21` | `{1,2,3}`→1, `4`→2, `5`→3, `6`→4, `9`→9 (descritiva) |
| `escolaridade_modelo` | `escolaridade_categorizada` | igual à descritiva, mas `9`→NaN; entra nos modelos ajustados como fator `C(escolaridade_modelo)` (referência = nível 1) |

---

# PARTE 3 — Mapa completo dos módulos do banco

O ELSI organiza as variáveis por **blocos do questionário**, identificados pela
**letra inicial do código** (ex.: tudo que começa com `n` pertence ao bloco N).
As tabelas abaixo cobrem **todas as ~1.082 (W1) / ~975 (W2) colunas**, por módulo.
As variáveis prioritárias (Parte 1) estão dentro destes blocos.

## 3.1 Entrevista DOMICILIAR (um registro por domicílio)

| Bloco | Prefixo | Conteúdo | Nº vars (W1 / W2) |
|-------|---------|----------|-------------------|
| Arrolamento | `ar*` (W1); `idade*`/`sexo*`/`relacao*` + `nmoradores` (W2) | Listagem dos moradores do domicílio (idade, sexo, parentesco) | 46 / ~37 |
| A — Estrutura domiciliar | `a*` | Características e infraestrutura da casa | 20 / 21 |
| B — Ativos (bens) | `b*` | Posse de bens duráveis e patrimônio | 39 / 39 |
| C — Despesas do domicílio | `c*` | Gastos do domicílio | 18 / 18 |
| D — Renda dos moradores | `d*` (e `dr*` em W1) | Renda de cada morador | 255+18 / 20 |

> Variáveis de renda agregadas presentes no banco: `rendadom` (renda domiciliar),
> `rendadompc` (renda domiciliar per capita), `rendaind` (renda individual),
> `propriedades`. (Derivadas pela equipe ELSI a partir do bloco D.)

## 3.2 Entrevista INDIVIDUAL (um registro por participante ≥ 50 anos)

| Bloco | Prefixo | Conteúdo | Nº vars (W1 / W2) |
|-------|---------|----------|-------------------|
| E — Características sociodemográficas | `e*` | Demografia, cor/raça, **escolaridade** (`e21`), estado civil | 30 / 30 |
| F — Vizinhança / Ambiente urbano | `f*` | Ambiente e vizinhança | 21 / 22 |
| G — Discriminação | `g*` | Experiências de discriminação | 14 / 31 |
| H — História de vida e de saúde | `h*` (e `ci*` = infância?) | Infância, condições de vida ao longo do tempo | 26+8 / 26+8 |
| I — Trabalho e aposentadoria | `i*` | Ocupação, aposentadoria, transferências | 46 / 57 |
| K — Ajudas familiares | `k*` | Transferências e apoio familiar | 11 / 13 |
| L — Comportamentos em saúde | `l*` | Tabagismo, álcool, **atividade física** (`l9`, `l10_2`) | 43 / 47 |
| M — Saúde da mulher | `m*` | História reprodutiva | 16 / 16 |
| N — Saúde geral e doenças | `n*` | Autoavaliação de saúde, visão/audição, **quedas** (`n18`), **doenças crônicas** (`n9`–`n63`) | 79 / 132 |
| O — Saúde bucal | `o*` | Condição e uso de serviços odontológicos | 30 / 47 |
| P — Funcionalidade | `p*` | Atividades de vida diária (AVD/AIVD), mobilidade | 80 / 129 |
| Q — Cognição | `q*` | Memória e função executiva | 21 / 19 |
| QP — Função cognitiva (respondente próximo) | `qp*` | Cognição avaliada por proxy | 55 / 55 |
| R — Sintomas depressivos | `r*` | Escala de depressão (CES-D-8) | 9 / 9 |
| S — Psicossocial | `s*` | Suporte social, bem-estar, qualidade de vida (CASP-19) | 54 / 58 |
| T — Uso de medicamentos | `t*` | Medicamentos em uso | 7 / 7 |
| U — Uso de serviços de saúde | `u*` | Consultas, internações, plano de saúde | 81 / 97 |
| MF — Medidas físicas | `mf*` | **Antropometria, pressão, preensão, equilíbrio, marcha** (todas as variáveis prioritárias físicas) | 42 / 24 |

> Os blocos `m*` (16 vars) também podem incluir itens herdados; `ci*` foi
> interpretado como **questionário de infância** (history of life) — **confirmar no
> codebook oficial** se necessário em análises futuras.

---

# PARTE 4 — Diferenças estruturais entre Wave 1 e Wave 2

1. **Identificadores.** W1 usa `id` / `iddom`; W2 usa `id2` / `iddom2`.
2. **Roster do domicílio.** W1 lista os moradores em variáveis `ar*`; W2 usa colunas
   numeradas `idade2..idade12`, `sexo2..sexo12`, `relacao2..relacao12` (+ `nmoradores`).
3. **Renda.** W1 detalha a renda por morador em ~255 colunas `d*`; W2 condensa o bloco
   D em ~20 colunas.
4. **`l10_2` só existe na W2** (componente de minutos da atividade física vigorosa).
   Na W1, `tempo_minutos_atividade_fisica` fica `NaN`.
5. **Tamanho dos blocos N, P, U cresce na W2** (mais detalhamento de doenças,
   funcionalidade e uso de serviços).
6. **Bloco F** muda de nome: "Vizinhança" (W1) → "Ambiente urbano e vizinhança" (W2).
7. **As 21 doenças crônicas, as medidas físicas prioritárias e o desenho amostral
   (`upa`, `estrato`, `peso_calibrado`) existem nas duas waves** — viabilizando tanto
   a análise da Wave 2 quanto comparações longitudinais futuras.

---

## Pontos a confirmar no codebook oficial (se necessário)

- Significado preciso dos prefixos `ci*` (infância?) e `dr*` (renda — respondente
  próximo?) — não detalhados aqui por não serem usados no script.
- Rótulos completos das categorias `1`–`3` de `e21` (níveis mais baixos de
  escolaridade), agrupados como categoria 1 no script.
