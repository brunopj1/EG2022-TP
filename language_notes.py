from email import message
from enum import Enum

class LanguageNoteType(Enum):
    ERROR   = 0
    WARNING = 1
    INFO    = 2

class LanguageNote():
    def __init__(self, message, tipo):
        self.message = message
        self.tipo = tipo
        self.posicao = None

#region Variaveis

class VariavelNaoDefinida(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel '{nomeVar}' nao definida",
            LanguageNoteType.ERROR			
		)

class VariavelRedefinida(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel '{nomeVar}' redefinida",
			LanguageNoteType.ERROR
		)

class VariavelNaoInicializada(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel '{nomeVar}' lida mas nao inicializada",
			LanguageNoteType.ERROR
		)

class VariavelNaoUtilizada(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel '{nomeVar}' nao utilizada",
			LanguageNoteType.WARNING
		)

class VariavelNaoLida(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel '{nomeVar}' atribuida mas nao lida",
			LanguageNoteType.WARNING
		)

#endregion

#region Funcoes

class FuncaoNaoDefinida(LanguageNote):
    def __init__(self, nomeFunc, argsFunc):
        super().__init__(
			f"Funcao '{nomeFunc}' com os argumentos {argsFunc} nao definida",
			LanguageNoteType.ERROR
		)

class FuncaoRedefinida(LanguageNote):
    def __init__(self, nomeFunc, argsFunc):
        super().__init__(
			f"Funcao '{nomeFunc}' com os argumentos {argsFunc} redefinida",
			LanguageNoteType.ERROR
		)

#endregion

#region Tipos

class TipoInvalido(LanguageNote):
    def __init__(self, tipo):
        super().__init__(
			f"Utilizacao de um tipo invalido '{tipo}'",
			LanguageNoteType.ERROR
		)

class AtribuicaoInvalida(LanguageNote):
    def __init__(self, tipoIn, tipoOut):
        super().__init__(
			f"Atribuicao invalida de uma expressao do tipo {tipoIn} para o tipo {tipoOut}",
			LanguageNoteType.ERROR
		)

class CastInvalido(LanguageNote):
    def __init__(self, tipoCast, tipoExp):
        super().__init__(
			f"Cast invalido de uma expressao do tipo {tipoExp} para o tipo {tipoCast}",
			LanguageNoteType.ERROR
		)

class AcessoInvalido(LanguageNote):
    def __init__(self, tipo):
        super().__init__(
			f"Acesso invalido a um valor do tipo '{tipo}'",
			LanguageNoteType.ERROR
		)

class ChaveAcessoInvalida(LanguageNote):
    def __init__(self, tipoEstrutura, tipoKey, tipoKeyEsperada):
        super().__init__(
			f"Acesso invalido a uma estrutura do tipo '{tipoEstrutura}' com uma chave do tipo '{tipoKey}' (esperada uma chave do tipo '{tipoKeyEsperada}')",
			LanguageNoteType.ERROR
		)

class IteracaoInvalida(LanguageNote):
    def __init__(self, tipo):
        super().__init__(
			f"Iteracao invalida de um valor do tipo '{tipo}'",
			LanguageNoteType.ERROR
		)

class EstruturaTiposIncompativeis(LanguageNote):
    def __init__(self, tipo1, tipo2):
        super().__init__(
			f"Estrutura com elementos de tipos incompativeis '{tipo1}' e '{tipo2}'",
			LanguageNoteType.ERROR
		)

class OperadorBinarioInvalido(LanguageNote):
    def __init__(self, operador, tipoEsq, tipoDir):
        super().__init__(
			f"Tipos de dados '{tipoEsq}' e '{tipoDir}' invalidos no operador binario '{operador}'",
			LanguageNoteType.ERROR
		)

class OperadorUnarioInvalido(LanguageNote):
    def __init__(self, operador, tipo):
        super().__init__(
			f"Tipo de dados '{tipo}' invalido no operador unario '{operador}'",
			LanguageNoteType.ERROR
		)

#endregion

#region Operacoes

class CondicaoIfInvalida(LanguageNote):
    def __init__(self):
        super().__init__(
			f"A condicao da operacao If nao corresponde a um valor do tipo bool",
			LanguageNoteType.WARNING
		)

class CondicaoWhileInvalida(LanguageNote):
    def __init__(self):
        super().__init__(
			f"A condicao do ciclo While nao corresponde a um valor do tipo bool",
			LanguageNoteType.WARNING
		)

class CondicaoForInvalida(LanguageNote):
    def __init__(self):
        super().__init__(
			f"A condicao do ciclo For nao corresponde a um valor do tipo bool",
			LanguageNoteType.WARNING
		)

class IfsAninhadosAgrupaveis(LanguageNote):
    def __init__(self):
        super().__init__(
			f"Os If's aninhados podem ser agrupados num so If",
			LanguageNoteType.WARNING
		)

#endregion

#region Outras

class NomeProibido(LanguageNote):
    def __init__(self, nome):
        super().__init__(
			f"A palavra '{nome}' nao pode ser utilizada como nome de variavel / funcao",
			LanguageNoteType.ERROR
		)

#endregion

#region Relatorio

class NumeroAcessosVariaveis(LanguageNote):
	def __init__(self, variaveis):
		message = ""
		for var in variaveis:
			message += f"Variavel '<b>{var.nome}</b>' do tipo <b>{var.tipo}</b>: {var.num_reads} reads; {var.num_writes} writes.<br>"
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

class NumeroTipos(LanguageNote):
	def __init__(self, tipos):
		numTipos = len(tipos.keys())
		message = f"O codigo contem <b>{numTipos} tipos</b> diferentes.<br><br>"
		for tipo, num in tipos.items():
			message += f"Ocorreram {num} ocorrencias do tipo <b>{tipo}</b>.<br>"
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

class NumeroOperacoes(LanguageNote):
	def __init__(self, numOperacoes, operacoes):
		message = f"O codigo contem <b>{numOperacoes} operacoes</b>.<br><br>"
		for nome, num in operacoes.items():
			message += f"Ocorreram {num} operacoes do tipo <b>{nome}</b>.<br>"
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

class NumeroOperacoesDepth(LanguageNote):
	def __init__(self, depths):
		message = ""
		for depth, num in depths.items():
			message += f"Ocorreram <b>{num}</b> operacoes com <b>profundeza {depth}</b>.<br>"
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

#endregion