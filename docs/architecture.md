# Arquitetura e contrato público

## Visão compacta

```text
DataFrame + target/config
        |
        v
validação -> perfil/tipos -> target/tarefa -> associação/triagem
                                                |
                                                v
                blueprint <- prescrições <- estresse/alertas
                    |
                    v
        revisão humana + Pipeline treinado apenas no treino
```

## Contrato público

```python
from reversede import Reversede, ReversedeConfig

analysis = Reversede(
    dataframe,
    target="critical_temp",        # opcional
    task="regression",             # auto | regression | classification
    config=ReversedeConfig(max_features=30),
)

analysis.target_                   # alvo resolvido ou None
analysis.target_confidence_        # 1.0 se informado; heurístico se inferido
analysis.target_candidates_        # candidatos e justificativas
analysis.profile_                  # perfil de todas as colunas
analysis.candidates_               # elegibilidade, métricas originais e score
analysis.stress_                   # estresse por candidata
analysis.prescriptions_            # evidência, ação, modelos e confiança
analysis.alerts_                   # alertas, não veredictos
analysis.generate_blueprint()      # texto sklearn; não escolhe estimador
analysis.summary()                 # estrutura serializável
analysis.save_report(path)         # CSV/JSON/blueprint
```

O construtor copia profundamente o DataFrame; nenhum método modifica o objeto do chamador. Configurações permitem exclusões e inclusões explícitas. Uma inclusão forçada permanece sinalizada no relatório. Limites de cardinalidade, categorias raras e outliers são propagados para o blueprint gerado, em vez de serem substituídos por constantes ocultas.

## Responsabilidades

| Módulo | Responsabilidade |
|---|---|
| `validation.py` | argumentos, DataFrame vazio, nomes duplicados e target |
| `types.py` | tipo prático e sinais de ID/texto/data/número em texto |
| `target.py` | candidatos, confiança, margem e abstenção |
| `association.py` | Pearson/Spearman, eta quadrado e Cramér V normalizados |
| `profile.py` | perfil e filtros de elegibilidade explicáveis |
| `stress.py` | nulos, infinitos, extremos, escala, categorias, sentinelas e colinearidade |
| `prescriptions.py` | recomendações condicionais, severidade e modelos afetados |
| `blueprint.py` | código sklearn sintaticamente válido, sem valores aprendidos globais |
| `api.py` | orquestração, persistência e API pública |

## Pseudocódigo

```text
validar(data, target, task)
working_copy <- deep_copy(data)
profile <- perfilar_todas_as_colunas(working_copy)
target <- explícito OU inferir_com_margem OU abster
task <- explícita OU heurística sinalizada
para cada feature != target:
    explicar elegibilidade
    se target confiável: calcular métricas compatíveis e score [0,1]
    senão: calcular prioridade estrutural, nunca importância preditiva
ordenar candidatas e limitar max_features
medir estresse de todas as elegíveis
gerar prescrições condicionadas ao modelo
gerar blueprint apenas com nomes e transformadores não ajustados
```

## Migração 0.1.0 -> 0.2.0

| Legado | Novo | Observação |
|---|---|---|
| `reverseda_ai` | `reversede` | novo namespace público |
| `ReversedaAutonoma` | `Reversede` | nova marca; classe antiga não é apagada do arquivo de referência |
| `requisitos_` | `candidates_` | relatório mais explícito e serializável |
| `estresse_` | `stress_` | inclui contagens, infinitos, sentinelas e colinearidade |
| `gerar_blueprint_extrator()` | `generate_blueprint()` | código retornado; salvar/imprimir é opção separada |
| `resumo()` | `summary()` | contrato em inglês consistente com pacote/import |

Compatibilidade aqui significa rastreabilidade e mapa de migração, não um alias silencioso: o pacote legado continua apenas como fonte auditada.
