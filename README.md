# Funcionalidades implementadas:

Validação de variaveis:
- Não é permitido definir a mesma variavel mais do que uma vez.
- Não é permitido utilizar variaveis ainda não definidas.
- Não é permitido utilizar variaveis ainda não inicializadas.
- Variaveis deixam de estar definidas quando se sai do scope onde foram criadas
- Variaveis so podem receber valores do tipo certo (exceto quando existe conversao possivel)
- É possivel criar variaveis globais desde que sejam inicializadas na sua criação

Tipos:
- É possivel declarar tipos complexos como listas, sets, maps e tuplos
- É possivel declarar tipos complexos dentro de outros tipos complexos (ex: lista de sets de bools)
- É possivel aceder a elementos internos de tipos complexos (ex: acessos a listas ou maps)
- É possivel aceder a tuplos, mas o tipo de retorno nao é validado devido a algumas limitações

Funcoes:
- É possivel criar funcoes e fazer chamadas às mesmas
- É possivel definir varias funções com o mesmo nome desde que tenham argumentos diferentes
- Não é possivel utilizar funcoes nao definidas

Operacoes:
- As condicoes dos If, While e For tem de ser do tipo bool
- Atribuicoes binarias e unarias so funcionam para variaveis numericas

# Duvidas:
- Podemos utilizar simbolos diferentes dos de python? (ex: « » para os sets)
- A maneira como representamos os tipos é valida para este trabalho?