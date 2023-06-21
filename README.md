# Trabalho Prático de Engenharia Gramatical 2022

Este repositório contém o trabalho pratico da unidade curricular de Engenharia Gramatical.  
O projeto consiste na implementação da gramática e para uma nova linguagem de programação e o seu respetivo analisador estático.

Os excertos de código enviados ao programa não devem ser executados, mas sim analisados de forma a encontrar possíveis erros, avisos e informações úteis. Para além disso, o programa também cria um grafo de controlo de fluxo e um grafo de dependências de sistema de forma a permitir uma analisa mais avançada dos excertos de código escritos para a linguagem. Todos os resultados da análise dos excertos são gravados numa página html.

A implementação foi feita em **python**, utilizando **Lark** para a geração da gramática independente de contexto (CFG) e **Graphviz** para a geração dos grafos.

A cotação deste projeto foi 20.

# Funcionalidades implementadas:

Validação de variáveis:
- Não é permitido definir a mesma variável mais do que uma vez.
- Não é permitido utilizar variáveis ainda não definidas.
- Não é permitido utilizar variáveis ainda não inicializadas.
- Variáveis deixam de estar definidas quando se sai do scope onde foram criadas
- Variáveis só podem receber valores do tipo certo (exceto quando existe conversão possível)
- É possível criar variáveis globais desde que sejam inicializadas na sua criação

Tipos:
- É possível declarar tipos complexos como listas, sets, maps e tuplos
- É possível declarar tipos complexos dentro de outros tipos complexos (ex: lista de sets de bools)
- É possível aceder a elementos internos de tipos complexos (ex: acessos a listas ou maps)
- É possível aceder a tuplos, mas o tipo de retorno nao é validado devido a algumas limitações

Funções:
- É possível criar funções e fazer chamadas às mesmas
- É possível definir várias funções com o mesmo nome desde que tenham argumentos diferentes
- Não é possível utilizar funções não definidas

Operações:
- As condições dos If, While e For tem de ser do tipo bool
- Atribuições binárias e unárias só funcionam para variáveis numéricas
