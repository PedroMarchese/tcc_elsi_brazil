# CLAUDE.md

Contexto e instruções do meu Trabalho de Conclusão de Curso (TCC). Este arquivo
deve ser mantido atualizado conforme o projeto evolui.

## Personalidade
Aja como um estatístico experiente em pesquisas na área de epidemiologia e
bioestatística. Ao introduzir pela primeira vez uma terminologia técnica,
explique para que ela serve e quais os valores esperados. Por exemplo: num teste
de normalidade, ou em uma regressão linear. Seja objetivo, visando uma economia responsável de tokens.  

## Idioma
Todas as respostas, comentários de código, tabelas e documentos devem ser em
**português (pt-BR)**.

---

## Objetivo do projeto
Investigar se existe **correlação entre a SSWS** (Self-Selected Walking Speed —
Velocidade de Caminhada Auto-Selecionada) **ou o LRI** (Locomotor Rehabilitation
Index — Índice de Reabilitação Locomotor) **com o número de morbidades** dos
indivíduos, usando os dados do **ELSI-Brasil**. A **mesma análise é executada
para as duas ondas (Waves 1 e 2)**, com as saídas distinguidas por sufixo
(`_w1` / `_w2`). A associação é examinada tanto de forma contínua quanto
estratificando por faixas de `n_morbidades`.

Base populacional: idosos (≥ 50 anos) do ELSI-Brasil. A SSWS é derivada do teste
de marcha cronometrada de 3 m; o comprimento do membro inferior (LLL) é derivado
da altura (`LLL = 0,54 × altura`), pois o banco não traz medida direta do LLL.

**Diferenças entre as ondas tratadas no código:**
- **SSWS** — a Wave 2 traz o tempo do teste já em segundos (`mf35s`/`mf38s`); a
  Wave 1 **não tem variável em segundos**, então o tempo é reconstruído a partir
  de minutos (`mf33`/`mf36`), segundos (`mf34`/`mf37`) e centésimos
  (`mf35`/`mf38`): `tempo_s = min·60 + s + centésimos/100`, e `SSWS = 3/tempo_s`
  (média das duas medições). Verificado: na Wave 1 essa reconstrução coincide
  com `mf35s`/`mf38s` (diferença ~1e-7).
- **Altura (`mf13`)** — Wave 2 em **cm**; Wave 1 em **metros**. O código normaliza
  ambas para cm antes de derivar o LLL (LLL médio ≈ 85,7 cm nas duas ondas).
- **`l10_2`** (tempo de atividade física) só existe na Wave 2; ausência tratada.

N elegível após a derivação da marcha: **Wave 1 = 8.746**; **Wave 2 = 7.205**.

### Fórmulas e constantes-chave (já implementadas no código)
- `OWS = √(Fr_walking · g · LLL)` — velocidade ótima de caminhada (`Fr_walking = 0,25`)
- `LRI = 100 · SSWS / OWS` — índice de reabilitação locomotor
- `MAX_WALKING_SPEED = √(Fr_running · g · LLL)` — cutoff de exclusão (`Fr_running = 0,5`)
- `g = scipy.constants.g` (≈ 9,80665 m/s²); `LLL = 0,54 × altura`
- `n_morbidades` = soma de 21 doenças crônicas autorreferidas (códigos `n*` do ELSI)

### Covariáveis de ajuste dos modelos multivariados
As regressões (OLS e logística) rodam em duas versões: **crua** e **ajustada**.
O ajuste é centralizado em `COLS_AJUSTE`/`TERMOS_AJUSTE` (no script) e inclui:
- **`idade`** e **`sexo`** (colunas nativas do CSV);
- **escolaridade** — derivada de `e21` em `escolaridade_modelo` (mesma
  recategorização da descritiva, mas com o código `9` = NS/NR → `NaN`). Entra
  como **fator categórico** `C(escolaridade_modelo)`, ou seja, *dummies* com a
  **menor escolaridade como referência** (não assume efeito linear entre níveis).

> Consequência: o ajuste por escolaridade reduz o N dos modelos ajustados por
> *listwise deletion* (W1 8.746→7.327; W2 7.205→6.336). A associação SSWS↔morbidade
> permanece significativa após o ajuste (ver `OBSERVACOES.md` §2.10).

> Fundamentação das fórmulas: ver `papers/RESUMO_LRI_Peyre-Tartaruga_2016.md`.
> Descrição do banco de dados: ver `papers/RESUMO_ELSI_Lima-Costa_2023.md`.

---

## Arquivos de referência (ler quando precisar de contexto)
- `papers/*.md` — resumos dos artigos-base (LRI e ELSI Cohort Profile).
- `banco_elsi/` — dados e manuais do ELSI:
  - `ELSI_wave_1.csv`, `ELSI_wave_2.csv` (dados; a análise usa **ambas as ondas**).
  - `Entrevista-individual-*.pdf`, `Entrevista-domiciliar-*.pdf`,
    `Manual-de-medidas-fisicas.pdf` — codebooks/manuais para mapear variáveis.
- `RESUMO.md` — registro do que já foi feito nas sessões (histórico de trabalho).
- `OBSERVACOES.md` — observações estatísticas/metodológicas detectadas nas
  análises (linguagem formal + justificativa); atualizar conforme surgirem novas.

---

## Estrutura atual do repositório
```
tcc_elsi/
├── CLAUDE.md                  (este arquivo — contexto do projeto)
├── RESUMO.md                  (histórico do que já foi feito)
├── VARIAVEIS.md               (mapeamento completo das variáveis — waves 1 e 2)
├── requirements.txt
├── .gitignore
├── .venv/                     (Python 3.13)
├── banco_elsi/                (dados ELSI wave 1 e 2 + PDFs dos manuais)
├── papers/                    (PDFs dos artigos + resumos .md)
├── codigos/
│   ├── elsi_tcc_wave2.py                  (script refatorado — fonte da verdade; roda as 2 waves)
│   └── elsi_tcc_wave2_colab_original.py   (backup do export do Colab)
├── images/                    (gráficos exportados — sufixados _w1/_w2)
└── tables/                    (tabelas exportadas — sufixadas _w1/_w2)
```

## Como rodar
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python codigos\elsi_tcc_wave2.py
```
O script lê `banco_elsi/ELSI_wave_1.csv` e `ELSI_wave_2.csv` (laço sobre
`WAVES = [1, 2]`), salva todas as figuras em `images/` e todas as tabelas em
`tables/`, **com sufixo `_w1`/`_w2` em cada arquivo**. Roda de ponta a ponta com
exit code 0. (O nome do arquivo `elsi_tcc_wave2.py` foi mantido por
compatibilidade, embora o script agora processe ambas as ondas.)

## Convenções de saída
- **Código** → `codigos/`. O script é a fonte da verdade da análise; manter os
  caminhos portáveis (resolvidos a partir da pasta do script).
- **Imagens** → `images/`. **Tabelas** → `tables/`.
- O **código NÃO deve gerar nenhum arquivo de variáveis** — o mapeamento de
  variáveis é responsabilidade do `VARIAVEIS.md` (ver abaixo).

---

## Etapas do TCC e estado atual

1. **[CONCLUÍDA] Refatorar o código.** O notebook do Colab foi refatorado em
   `codigos/elsi_tcc_wave2.py` (original preservado em
   `..._colab_original.py`), com toda a lógica estatística preservada e saídas
   organizadas em `images/` e `tables/`.

2. **[CONCLUÍDA] Mapear as variáveis do banco** a partir dos PDFs de entrevista
   do ELSI em `banco_elsi/`, cruzando com as variáveis efetivamente usadas no
   código (waves 1 e 2).

3. **[CONCLUÍDA] Criar `VARIAVEIS.md`** — é o **único** documento de variáveis do
   projeto (na raiz). Descreve as variáveis prioritárias (usadas no script) em
   detalhe, as variáveis derivadas e o mapa completo de todos os módulos do banco
   nas duas waves. O código não gera arquivos de variáveis. (O antigo
   `codigos/variaveis_analise_estatistica.md` foi consolidado e removido.)

4. **[PARCIAL] Exportar análises.** Já exportadas como EXCEL/PNG (descritivas,
   regressões OLS/logística/Poisson, curvas ROC/AUC, VIF). **Falta** gerar as
   versões em **tabela estilo APA**.

---

## Notas metodológicas em aberto (revisar futuramente)
- **Desenho amostral complexo / pesos amostrais.** O ELSI usa amostragem
  complexa (pesos + estratificação + clustering). A análise atual é
  **não-ponderada** (OLS/logística simples). Incorporar os pesos faria os
  resultados representarem toda a população idosa do Brasil e corrigiria os
  erros-padrão. **Ponto a decidir:** confirmar se o `ELSI_wave_2.csv` traz a
  coluna de peso e, em caso afirmativo, avaliar análise ponderada — ou então
  registrar a ausência de ponderação como limitação no texto do TCC.
- **Autorrelato.** As morbidades são autorreferidas — discutir como limitação.
- **LLL aproximado pela altura** (`0,54 × altura`) — registrar como aproximação,
  já que o banco não tem a medida direta trocânter→chão.
