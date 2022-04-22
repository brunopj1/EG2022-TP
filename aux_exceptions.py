from enum import Enum

class LanguageErrorType(Enum):
    NONE    = 0
    ERROR   = 1
    WARNING = 2
    INFO    = 3

class LanguageError(Exception):
    # TODO meter o tipo e a posicao
    def __init__(self, message, tipo = LanguageErrorType.NONE, posicao = None):
        super().__init__(message)
        self.message = message
        self.tipo = tipo
        self.posicao = posicao

#region Variaveis

class VariavelNaoDefinida(LanguageError):
    def __init__(self, nomeVar):
        super().__init__(f"Variavel '{nomeVar}' nao definida")

class VariavelRedefinida(LanguageError):
    def __init__(self, nomeVar):
        super().__init__(f"Variavel '{nomeVar}' redefinida")

class VariavelNaoInicializada(LanguageError):
    def __init__(self, nomeVar):
        super().__init__(f"Variavel '{nomeVar}' nao inicializada")

#endregion

#region Funcoes

class FuncaoNaoDefinida(LanguageError):
    def __init__(self, nomeFunc, argsFunc):
        super().__init__(f"Funcao '{nomeFunc}' com os argumentos {argsFunc} nao definida")

class FuncaoRedefinida(LanguageError):
    def __init__(self, nomeFunc, argsFunc):
        super().__init__(f"Funcao '{nomeFunc}' com os argumentos {argsFunc} redefinida")

#endregion

#region Tipos

class TipoInvalido(LanguageError):
    def __init__(self, nome, num_subtipos):
        subtipos = "" if num_subtipos == 0 else f"<{num_subtipos}>"
        super().__init__(f"Utilização de um tipo inválido '{nome}{subtipos}'")

class TipoVariavel(LanguageError):
    def __init__(self, nomeVar, tipoVar, tipoVal):
        super().__init__(f"Variavel '{nomeVar}' do tipo {tipoVar} a receber um valor do tipo {tipoVal}")

class TipoCast(LanguageError):
    def __init__(self, tipoCast, tipoExp):
        super().__init__(f"Cast inválido de uma expressao do tipo {tipoExp} para o tipo {tipoCast}")

class AcessoTipo(LanguageError):
    def __init__(self, tipo):
        super().__init__(f"Acesso inválido a um valor do tipo '{tipo}'")

class AcessoTipoKey(LanguageError):
    def __init__(self, tipoEstrutura, tipoKey, tipoKeyEsperada):
        super().__init__(f"Acesso inválido a uma estrutura do tipo '{tipoEstrutura}' com uma chave do tipo '{tipoKey}' (esperada uma chave do tipo '{tipoKeyEsperada}')")

class TipoEstrutura(LanguageError):
    def __init__(self, tipo1, tipo2):
        super().__init__(f"Estrutura com elementos de tipos incompativeis '{tipo1}' e '{tipo2}'")

class NumeroTiposEstrutura(LanguageError):
    def __init__(self, nomeEstrutura, numAtribuido, numEsperado, numVariavel):
        numEsperado = str(numEsperado)
        if numVariavel:
            numEsperado += " ou mais"
        super().__init__(f"Estrutura do tipo '{nomeEstrutura}' a receber {numAtribuido} subtipos (esperados {numEsperado} subtipos)")

class TipoAtribuicaoBinaria(LanguageError):
    def __init__(self, nomeVar):
        super().__init__(f"Variavel '{nomeVar}' de tipo nao numerico utilizada numa atribuicao binaria")

class TipoOperadorBin(LanguageError):
    def __init__(self, operador, tipoEsq, tipoDir):
        super().__init__(f"Tipos de dados '{tipoEsq}' e '{tipoDir}' invalidos no operador binario '{operador}'")

class TipoOperadorUn(LanguageError):
    def __init__(self, operador, tipo):
        super().__init__(f"Tipo de dados '{tipo}' invalido no operador unario '{operador}'")

class CondicaoIf(LanguageError):
    def __init__(self):
        super().__init__(f"A condicao da operação If não corresponde a um valor do tipo bool")

class CondicaoWhile(LanguageError):
    def __init__(self):
        super().__init__(f"A condicao do ciclo While não corresponde a um valor do tipo bool")

class CondicaoFor(LanguageError):
    def __init__(self):
        super().__init__(f"A condicao do ciclo For não corresponde a um valor do tipo bool")

#endregion

#region Outras

class NomeProibido(LanguageError):
    def __init__(self, nome):
        super().__init__(f"A palavra '{nome}' nao pode ser utilizada como nome de variavel / funcao")

#endregion