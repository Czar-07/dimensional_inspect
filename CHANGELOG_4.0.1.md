# DIMENSION-RATE 4.0.1

## Correção do contador de características

O parser agora reconhece características numeradas que não são LOCs, mas possuem a mesma estrutura dimensional do relatório Hexagon:

- LOC1 ... LOC49
- PLANO1 ... PLANO4
- DIST1

No relatório 7131_26 usado como validação:

- 45 LOCs detectados
- 4 planos
- 1 distância
- **50 características dimensionais calculadas**

X/Y/Z/D/L dentro do mesmo LOC continuam sendo uma única característica.

## Interface

- Modo claro Art Déco de engenharia como padrão.
- Removidos estilos conflitantes preto/vermelho que sobrescreviam o tema claro.
- Hierarquia visual simplificada.
- Navegação lateral reduzida às funções reais do sistema.
- Resultados em lote continuam em lista, sem gráficos automáticos.
- Histórico e Part Number continuam permitindo abrir um relatório individual ou selecionar vários para comparação.
