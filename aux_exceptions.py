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

class TipoVariavelException(LanguageException):
    def __init__(self, nomeVar, tipoVar, tipoVal):
        super().__init__(f"Variavel '{nomeVar}' do tipo {tipoVar} a receber um valor do tipo {tipoVal}")

class TipoAtribuicaoComplexaException(LanguageException):
    def __init__(self, nomeVar, atribBinaria):
        tipoAtrib = "binaria" if atribBinaria else "unaria"
        super().__init__(f"Variavel '{nomeVar}' de tipo nao numerico utilizada numa atribuicao {tipoAtrib}")

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

#region Operacoes

class TipoCastException(LanguageException):
    def __init__(self, tipoCast, tipoExp):
        super().__init__(f"Cast inválido de uma expressao do tipo {tipoExp} para o tipo {tipoCast}")

#endregion

#region Outras

class NomeProibidoException(LanguageException):
    def __init__(self, nome):
        super().__init__(f"A palavra '{nome}' nao pode ser utilizada como nome de variavel / funcao")

#endregion