# OBSERVAÇÕES — Análise ELSI (Waves 1 e 2)

Registro das observações estatísticas e metodológicas detectadas ao longo das
análises da associação entre **SSWS** (velocidade de marcha auto-selecionada) /
**LRI** (índice de reabilitação locomotor) e o **número de morbidades**
(`n_morbidades`) em idosos do ELSI-Brasil. As duas ondas são analisadas com o
mesmo pipeline (`codigos/elsi_tcc_wave2.py`), com saídas sufixadas `_w1`/`_w2`.

> **Formato de cada item:** primeiro a observação em **linguagem estatística
> formal**; em seguida, em *Por quê*, a justificativa de por que ela é registrada
> (o que implica para a interpretação ou para o texto do TCC).

Convenções: N elegível após a derivação da marcha = **8.746 (Wave 1)** e
**7.205 (Wave 2)**. Salvo indicação, "significativo" = p < 0,05.

---

## 1. Observações metodológicas (preparação dos dados)

### 1.1. Reconstrução da SSWS na Wave 1
**Observação.** Na Wave 2 o tempo do teste de marcha de 3 m está disponível
diretamente em segundos (`mf35s`, `mf38s`); na Wave 1 essa variável não existe e
o tempo foi reconstruído a partir da decomposição minutos/segundos/centésimos
(`mf33`/`mf34`/`mf35` e `mf36`/`mf37`/`mf38`), via
`tempo_s = min·60 + s + centésimos/100` e `SSWS = média(3 / tempo_s)`. A
reconstrução foi validada contra `mf35s`/`mf38s` (presentes na Wave 1), com
discrepância máxima da ordem de 1×10⁻⁷ s.

*Por quê:* a SSWS é o preditor central do estudo; é necessário documentar que a
variável foi **derivada de forma distinta entre as ondas** e que essa derivação
é numericamente equivalente à medida direta, afastando a hipótese de que
diferenças entre ondas decorram do método de cálculo.

### 1.2. Unidade da altura difere entre as ondas
**Observação.** A variável de altura (`mf13`) está em **metros** na Wave 1 e em
**centímetros** na Wave 2. Ambas foram normalizadas para centímetros antes de
derivar o comprimento do membro inferior (LLL = 0,54 × altura). Como verificação,
o LLL médio resultou praticamente idêntico nas duas ondas (≈ 85,7 cm).

*Por quê:* sem a normalização, o LLL da Wave 1 sairia 100× menor, inflando
artificialmente o LRI. A convergência do LLL médio entre ondas é a evidência de
que a harmonização de unidades foi bem-sucedida.

### 1.3. Diferença de nível da SSWS entre as ondas
**Observação.** A SSWS média foi de **0,74 m/s (DP 0,25)** na Wave 1 e
**0,59 m/s (DP 0,29)** na Wave 2; o LRI médio caiu de **50,7%** para **40,5%**.
A OWS média manteve-se estável (≈ 1,45 m/s nas duas ondas).

*Por quê:* uma queda de ~0,15 m/s na velocidade habitual é **grande** para um
intervalo de 3–4 anos entre ondas e excede o declínio esperado apenas pelo
envelhecimento da coorte. Como a OWS (que depende só do LLL) não mudou, a
diferença concentra-se na SSWS — sugerindo possível contribuição de
**protocolo/instrumentação de medição entre as ondas**, além de envelhecimento e
recomposição amostral (*refreshment*). Deve ser registrada como ponto a discutir,
evitando interpretar a diferença como puro efeito longitudinal.

### 1.4. Ausência de `l10_2` na Wave 1
**Observação.** A variável de tempo de atividade física (`l10_2`) existe apenas na
Wave 2. As análises que dela dependem
(`tempo_minutos_atividade_fisica ~ SSWS/n_morbidades`) não são estimáveis na
Wave 1 e foram omitidas dessa onda, sem interromper o restante do pipeline.

*Por quê:* a comparação entre ondas dessas associações específicas **não é
possível**; o leitor deve saber que a ausência é estrutural (banco), não uma
perda por dados faltantes.

---

## 2. Observações sobre as regressões

### 2.1. Associação central na direção esperada e significativa nas duas ondas
**Observação.** Nas regressões lineares (OLS) brutas, `n_morbidades` associa-se
**negativamente** tanto à SSWS quanto ao LRI, com p < 0,001 nas duas ondas
(Wave 1: β_SSWS = −0,0239 por morbidade; Wave 2: β_SSWS = −0,0141). De forma
equivalente, modelando SSWS/LRI como desfecho, cada morbidade adicional reduz a
SSWS em ≈ 0,024 m/s (W1) e ≈ 0,014 m/s (W2).

*Por quê:* confirma a **hipótese central** do TCC (maior multimorbidade ↔ pior
desempenho de marcha) e mostra que o sinal do efeito é consistente entre as
ondas, dando robustez ao achado qualitativo.

### 2.2. Significância estatística com tamanho de efeito pequeno (R² baixo)
**Observação.** Apesar dos p-valores < 0,001, o coeficiente de determinação é
baixo: para `SSWS ~ n_morbidades`, R² = 0,039 (Wave 1) e R² = 0,009 (Wave 2);
para `LRI ~ n_morbidades`, R² = 0,035 e 0,007, respectivamente. Ou seja, o número
de morbidades explica **menos de 4% (W1) e menos de 1% (W2)** da variância da
velocidade de marcha.

*Por quê:* com N de milhares, efeitos diminutos atingem significância; a
**significância estatística não deve ser confundida com relevância clínica**. É
essencial reportar tamanho de efeito (β, R²) ao lado do p-valor e moderar as
conclusões: a multimorbidade está associada à marcha, mas explica pouco da sua
variabilidade individual.

### 2.3. O LRI é praticamente uma reescala linear da SSWS
**Observação.** A regressão `LRI ~ SSWS` apresenta R² = 0,992 (Wave 1) e
R² = 0,996 (Wave 2), com inclinação ≈ 67–68. Isso ocorre porque o LRI =
100·SSWS/OWS e a OWS tem variabilidade pequena (coeficiente de variação ≈ 3%:
DP ≈ 0,04 sobre média ≈ 1,45 m/s).

*Por quê:* implica que **SSWS e LRI carregam quase a mesma informação** nesta
amostra — a normalização pelo tamanho corporal (via OWS/LLL) acrescenta pouco,
porque o LLL (derivado da altura) varia pouco entre idosos. Consequência prática:
não se deve esperar que o LRI supere a SSWS como preditor (ver §3.2), e usar
ambos no mesmo modelo introduziria colinearidade quase perfeita.

### 2.4. Atenuação dos coeficientes após ajuste por idade e sexo
**Observação.** Ao ajustar por idade e sexo, o coeficiente de `n_morbidades ~
SSWS` cai de −1,64 para −0,82 na Wave 1 e de −0,62 para −0,25 na Wave 2
(reduções de ~50% e ~60%); ainda assim o R² do modelo **sobe** (Wave 1: 0,039 →
0,110; Wave 2: 0,009 → 0,082).

*Por quê:* indica **confundimento por idade/sexo** — parte da associação bruta
SSWS–morbidade é explicada pela idade (idosos mais velhos andam mais devagar e
acumulam mais doenças). O aumento do R² vem majoritariamente de idade/sexo, não
da marcha, reforçando §2.2. Sustenta reportar preferencialmente os modelos
ajustados.

### 2.5. Menor robustez da associação na Wave 2 (grupo neuro/musculoesquelético)
**Observação.** Nas somas por grupo de doenças ajustadas por idade/sexo, o
`grupo_0` (neuro/oftálmico/musculoesquelético) permanece significativo na Wave 1
(p < 0,001) mas **perde significância na Wave 2** (SSWS: p = 0,067; LRI:
p = 0,065). Os grupos cardiorrespiratório e "outras" mantêm significância nas
duas ondas, embora com magnitude menor na Wave 2.

*Por quê:* a associação não é uniformemente reprodutível entre as ondas para
todos os grupos de doença; esse contraste deve ser explicitado para não
superestimar a estabilidade do achado e para orientar a discussão sobre quais
grupos de morbidade efetivamente se relacionam à marcha.

### 2.6. Padrão dose-resposta não-monotônico nas faixas de morbidade
**Observação.** Nas regressões logísticas por faixa de contagem, a SSWS associa-se
**positivamente** a ter < 2 morbidades (OR > 1; Wave 1 bruto OR = 3,50) e
**negativamente**, com magnitude crescente, às faixas altas (≥ 4, ≥ 5, ≥ 6 e
≥ 7 morbidades; Wave 1 bruto: OR de 0,47 em "= 4" a 0,15 em "≥ 7"). As faixas
intermediárias (`= 2`, `= 3`) são não-significativas ou fracas em ambas as ondas.

*Por quê:* o efeito da marcha **concentra-se nos extremos** da distribuição de
morbidades (discrimina bem "muito saudável" e "muito doente", mal a zona
intermediária). Esse padrão antecipa e explica o comportamento das curvas ROC
(§3.1) e sugere que a SSWS é mais útil como marcador nos extremos do espectro.

### 2.7. Achados exploratórios coerentes (força de preensão, quedas, equilíbrio)
**Observação.** Nas duas ondas: maior força de preensão associa-se a menos
morbidades (β ≈ −0,05 a −0,06; p < 0,001); histórico de queda associa-se a mais
morbidades (β ≈ +0,87 a +0,89; p < 0,001); melhor equilíbrio (`mf30`) associa-se a
maior SSWS (p < 0,001).

*Por quê:* são associações na direção biologicamente plausível e servem de
**checagem de consistência interna** dos dados derivados — aumentam a confiança
de que as variáveis foram corretamente construídas em ambas as ondas.

### 2.8. Codificação de `mf31` (semi-tandem) difere entre as ondas
**Observação.** Em `SSWS ~ mf31_dummy`, o coeficiente é ≈ 0 na Wave 1
(β ≈ −1×10⁻⁵, ainda que com p < 0,001 e R² = 0,02) e da ordem de −0,002 na
Wave 2; em `n_morbidades ~ mf31_dummy` o sinal/escala também diverge entre ondas.

*Por quê:* coeficiente praticamente nulo com p significativo é sinal de
**diferença de escala/codificação da variável entre as ondas** (provável unidade
ou faixa distinta de `mf31`). Ponto a confirmar no codebook antes de qualquer uso
comparativo de `mf31` entre Wave 1 e Wave 2.

### 2.9. Ausência de multicolinearidade preocupante nos modelos ajustados
**Observação.** Os fatores de inflação da variância (VIF) das covariáveis dos
modelos SSWS/LRI + idade + sexo + escolaridade são baixos (todos < 1,1 nas duas
ondas — inclusive as *dummies* de escolaridade, VIF ≈ 1,0), desconsiderando o
intercepto.

*Por quê:* o VIF mede quanto a variância de um coeficiente é inflada por
correlação entre preditores (valores > 5–10 indicam problema). Os valores
observados garantem que **idade, sexo, escolaridade e a variável de marcha não
competem entre si**, validando a leitura dos coeficientes ajustados. (O VIF alto
do intercepto é esperado e não tem interpretação de colinearidade.)

### 2.10. Robustez da associação central ao ajuste adicional por escolaridade
**Observação.** Acrescentando a escolaridade às covariáveis de ajuste (idade,
sexo, como fator categórico `C(escolaridade_modelo)` com a menor escolaridade
como referência), a associação `n_morbidades ~ SSWS` **mantém-se significativa e
na mesma direção** nas duas ondas (Wave 1: β = −0,77, p < 0,001; Wave 2:
β = −0,25, p = 0,002). A própria escolaridade contribui de forma modesta: na
Wave 1 nenhum nível atinge significância (o nível superior tem p = 0,069); na
Wave 2 apenas o nível "ginásio completo" é significativo (β = −0,30, p = 0,011).
O ajuste reduz o N por exclusão de casos completos (*listwise deletion*): Wave 1
de 8.746 → 7.327; Wave 2 de 7.205 → 6.336 (perda dos códigos 9 = "não sabe/não
respondeu" e faltantes de `e21`).

*Por quê:* escolaridade é um **confundidor plausível** — associa-se tanto à
multimorbidade (gradiente socioeconômico em saúde) quanto ao desempenho de marcha.
Demonstrar que o efeito da SSWS **persiste após esse controle** fortalece o
argumento de que a associação não é mero reflexo de posição socioeconômica. A
redução de N e o efeito modesto da escolaridade devem ser reportados: o primeiro
como custo do ajuste (eventualmente avaliar imputação); o segundo indica que, na
presença de idade e sexo, a escolaridade agrega pouco confundimento residual.

### 2.11. Heterocedasticidade presente, mas inferência estável com erros-padrão convencionais
**Observação.** O teste de Breusch-Pagan rejeita a homocedasticidade em todos os
modelos principais (LM p entre 1×10⁻⁶ e 5×10⁻¹⁸ nas duas ondas). Apesar disso, ao
comparar erros-padrão convencionais com robustos à heterocedasticidade (HC3), a
variação é mínima (≤ ~6%) e **nenhuma conclusão muda**: por exemplo, em
`n_morbidades ~ SSWS` ajustado, a SSWS mantém p = 6×10⁻¹⁵ (convencional) vs.
2×10⁻¹³ (HC3) na Wave 1, e p = 2,2×10⁻³ em ambos na Wave 2. Por decisão do
projeto, adotaram-se **erros-padrão convencionais em todos os modelos**.

*Por quê:* a heterocedasticidade é esperada quando o desfecho é uma **contagem**
(`n_morbidades`), cuja variância cresce com a média. Ela enviesa os erros-padrão,
não os coeficientes. A robustez (HC3) seria a correção usual, mas aqui o impacto é
desprezível porque o N é grande e os efeitos estão muito longe do limiar de
significância — logo, manter os erros-padrão convencionais não altera as
conclusões e simplifica a interpretação. Vale registrar que o **HC3 corrige
heterocedasticidade, mas não o desenho amostral complexo** (conglomerados/UPA): a
correção metodologicamente mais relevante continua sendo a análise de *survey*
(§5.1), não os erros-padrão robustos.

---

## 3. Observações sobre as curvas ROC / AUC

> A AUC (*Area Under the ROC Curve*) mede a capacidade de um escore separar casos
> de não-casos: 0,5 = ausência de discriminação (acaso); 1,0 = discriminação
> perfeita; 0,7–0,8 costuma ser tido como discriminação aceitável.

### 3.1. Discriminação fraca da SSWS/LRI isoladas para a maioria das faixas
**Observação.** Nas ROC simples (escore único, sem ajuste), as AUC ficam próximas
de 0,5 na maior parte das faixas: na Wave 1 variam de 0,60 (`< 2 morbidades`) a
0,36 (`≥ 7`); na Wave 2, de 0,54 a 0,38. As faixas intermediárias (`= 3`) têm
AUC ≈ 0,49–0,50.

*Por quê:* isoladamente, **SSWS e LRI discriminam mal** o número de morbidades —
coerente com o R² baixo (§2.2) e com o padrão nos extremos (§2.6). Sustenta que a
marcha, sozinha, não é um bom classificador de multimorbidade.

### 3.2. AUC < 0,5 indica direção protetora, não desempenho "pior que o acaso"
**Observação.** Várias AUC são < 0,5 (ex.: SSWS vs `≥ 7 morbidades` = 0,36 na
Wave 1). Como a curva foi traçada usando o escore "como está" (escore alto =
predição de caso), AUC < 0,5 reflete que **escore alto prediz o desfecho
negativo**: maior velocidade está associada a *menor* probabilidade de muitas
morbidades. Invertendo o sinal do escore, a AUC correspondente seria 1 − 0,36 =
0,64.

*Por quê:* evita o erro de interpretar AUC < 0,5 como "modelo ruim". A informação
discriminante existe, mas é **protetora** (direção esperada). É importante deixar
isso explícito na legenda das figuras ROC do TCC.

### 3.3. SSWS e LRI produzem AUC praticamente idênticas
**Observação.** Em todas as faixas e nos modelos ajustados por corte, as AUC de
SSWS e LRI diferem apenas na 2ª–3ª casa decimal (ex.: Wave 2, corte ≥ 2:
AUC_SSWS = AUC_LRI = 0,6448).

*Por quê:* confirma empiricamente §2.3 — como o LRI é quase uma reescala da SSWS,
**não acrescenta poder discriminante**. Para os objetivos do TCC, reportar a SSWS
(de interpretação física direta, em m/s) é suficiente; o LRI pode ser apresentado
como medida complementar, não como ganho preditivo.

### 3.4. Ganho de discriminação vem do ajuste por idade/sexo, não da marcha
**Observação.** Nos modelos logísticos ajustados (SSWS/LRI + idade + sexo), a AUC
sobe para a faixa de **0,64–0,68** (Wave 1: 0,669–0,679 para cortes ≥ 2 a ≥ 4;
Wave 2: 0,645–0,660), contra ≈ 0,5 das ROC simples.

*Por quê:* o salto de discriminação ao adicionar idade e sexo, frente ao R²
modesto atribuível à marcha (§2.4), indica que **a maior parte do poder
classificatório provém de idade/sexo**, não da SSWS/LRI. Reforça a leitura
cautelosa do papel preditivo da marcha.

### 3.5. Discriminação levemente superior na Wave 1
**Observação.** As AUC ajustadas são sistematicamente um pouco maiores na Wave 1
do que na Wave 2 (ex.: corte ≥ 2: 0,669 vs 0,645).

*Por quê:* é consistente com o R² maior na Wave 1 (§2.2) e com a §2.5; a relação
marcha–morbidade aparece **mais forte na Wave 1**. Pode refletir diferenças de
medição entre ondas (§1.3) e merece nota na comparação entre as ondas.

---

## 4. Observações sobre pressupostos (normalidade)

### 4.1. SSWS desvia da normalidade, com assimetria positiva
**Observação.** O teste de Anderson-Darling rejeita a normalidade da SSWS nas
duas ondas (estatística = 44,6 na Wave 1 e 13,7 na Wave 2; muito acima do valor
crítico ≈ 0,78 a 5%). A assimetria (*skewness*) é positiva (0,75 na Wave 1; 0,28
na Wave 2) e a Wave 2 é mais simétrica.

*Por quê:* a OLS não exige normalidade da variável em si, mas dos **resíduos**;
com N grande, o Teorema Central do Limite protege as estimativas dos
coeficientes. A assimetria recomenda **cautela com intervalos de confiança**; a
opção do projeto, contudo, foi manter **erros-padrão convencionais** em todos os
modelos (ver §2.11 para a justificativa empírica).

---

## 5. Limitações transversais (a registrar no texto do TCC)

### 5.1. Análise não-ponderada (desenho amostral complexo)
**Observação.** O ELSI emprega amostragem complexa (pesos `peso_calibrado`,
estratos `estrato` e conglomerados `upa`, presentes nas duas ondas), mas a
análise atual é **não-ponderada** (OLS/logística simples).

*Por quê:* ignorar o desenho amostral tende a **subestimar os erros-padrão** e,
portanto, a superestimar a significância. Dado que praticamente todos os testes
retornam p < 0,001, parte dessa onipresença pode ser artefato da não-ponderação.
Recomenda-se, como passo futuro, repetir as estimativas com pesos e correção de
variância para desenho complexo — ou, no mínimo, declarar explicitamente a
não-ponderação como limitação.

### 5.2. Morbidades autorreferidas
**Observação.** As 21 condições que compõem `n_morbidades` são **autorreferidas**
(diagnóstico médico prévio relatado pelo participante).

*Por quê:* sujeito a viés de memória e de acesso ao diagnóstico (quem usa mais
serviços de saúde tende a relatar mais doenças), o que pode atenuar ou distorcer
a associação observada. Limitação padrão a discutir.

### 5.3. LLL aproximado pela altura
**Observação.** O comprimento do membro inferior (LLL) não é medido diretamente
no ELSI; foi aproximado por `LLL = 0,54 × altura`, e dele derivam OWS e LRI.

*Por quê:* qualquer erro sistemático nessa razão se propaga à OWS e ao LRI. Como
o LRI mostrou-se quase uma reescala da SSWS (§2.3), o impacto sobre as conclusões
qualitativas é limitado, mas a aproximação deve ser declarada.

---

## 6. Síntese das observações com maior implicação para o TCC

1. A associação **marcha ↔ multimorbidade existe, é negativa e significativa**,
   mas de **magnitude pequena** (R² baixo) e dirigida em parte por idade/sexo
   (§2.1, §2.2, §2.4).
2. **LRI ≈ SSWS reescalado** → não há ganho preditivo do LRI sobre a SSWS nesta
   amostra (§2.3, §3.3); priorizar a SSWS na interpretação.
3. O poder de **discriminação isolado da marcha é fraco** (AUC ≈ 0,5); o que
   discrimina é idade/sexo (§3.1, §3.4).
4. O efeito é **mais nítido nos extremos** do espectro de morbidades (§2.6, §3.2)
   e **mais forte na Wave 1** que na Wave 2 (§2.5, §3.5), com possível
   contribuição de diferenças de medição entre ondas (§1.3).
5. **Cautela com p-valores** dada a não-ponderação amostral (§5.1).
