class LanguageException(Exception):
    pass

#region Variaveis

class VariavelNaoDefinidaException(LanguageException):
    def __init__(self, nomeVar):
        super().__init__(f"Variavel '{nomeVar}' nao definida")

class VariavelRedefinidaException(LanguageException):
    def __init__(self, nomeVar):
        super().__init__(f"Variavel '{nomeVar}' redefinida")

class VariavelNaoInicializadaException(LanguageException):
    def __init__(self, nomeVar):
        super().__init__(f"Variavel '{nomeVar}' nao inicializada")

#endregion

#region Funcoes

class FuncaoNaoDefinidaException(LanguageException):
    def __init__(self, nomeFunc, argsFunc):
        super().__init__(f"Funcao '{nomeFunc}' com os argumentos {argsFunc} nao definida")

class FuncaoRedefinidaException(LanguageException):
    def __init__(self, nomeFunc, argsFunc):
        super().__init__(f"Funcao '{nomeFunc}' com os argumentos {argsFunc} redefinida")

#endregion

#region Tipos

class TipoInvalidoException(LanguageException):
    def __init__(self, nome, num_subtipos):
        subtipos = "" if num_subtipos == 0 else f"<{num_subtipos}>"
        super().__init__(f"Utilização de um tipo inválido '{nome}{subtipos}'")

class TipoVariavelException(LanguageException):
    def __init__(self, nomeVar, tipoVar, tipoVal):
        super().__init__(f"Variavel '{nomeVar}' do tipo {tipoVar} a receber um valor do tipo {tipoVal}")

class TipoCastException(LanguageException):
    def __init__(self, tipoCast, tipoExp):
        super().__init__(f"Cast inválido de uma expressao do tipo {tipoExp} para o tipo {tipoCast}")

class TipoAtribuicaoBinariaException(LanguageException):
    def __init__(self, nomeVar, atribBinaria):
        super().__init__(f"Variavel '{nomeVar}' de tipo nao numerico utilizada numa atribuicao binaria")

class TipoOperadorBinException(LanguageException):
    def __init__(self, operador, tipoEsq, tipoDir):
        super().__init__(f"Tipos de dados '{tipoEsq}' e '{tipoDir}' invalidos no operador binario '{operador}'")

class TipoOperadorUnException(LanguageException):
    def __init__(self, operador, tipo):
        super().__init__(f"Tipo de dados '{tipo}' invalido no operador unario '{operador}'")

class CondicaoIfException(LanguageException):
    def __init__(self):
        super().__init__(f"A condicao da operação If não corresponde a um valor do tipo bool")

class CondicaoWhileException(LanguageException):
    def __init__(self):
        super().__init__(f"A condicao do ciclo While não corresponde a um valor do tipo bool")

class CondicaoForException(LanguageException):
    def __init__(self):
        super().__init__(f"A condicao do ciclo For não corresponde a um valor do tipo bool")

#endregion

#region Outras

class NomeProibidoException(LanguageException):
    def __init__(self, nome):
        super().__init__(f"A palavra '{nome}' nao pode ser utilizada como nome de variavel / funcao")

#endregion