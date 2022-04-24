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
		self.posicaoFim = None

#region Variaveis

class VariavelNaoDefinida(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel <b>{nomeVar}</b> nao definida.",
            LanguageNoteType.ERROR			
		)

class VariavelRedefinida(LanguageNote):
    def __init__(self, nomeVar, posicaoPrimeiraDef):
        super().__init__(
			f"Variavel <b>{nomeVar}</b> redefinida.<br>Definida previamente na linha {posicaoPrimeiraDef[0]}, coluna {posicaoPrimeiraDef[1]}.",
			LanguageNoteType.ERROR
		)

class VariavelNaoInicializada(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel <b>{nomeVar}</b> lida mas nao inicializada.",
			LanguageNoteType.ERROR
		)

class VariavelNaoUtilizada(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel <b>{nomeVar}</b> nao utilizada.",
			LanguageNoteType.WARNING
		)

class VariavelNaoLida(LanguageNote):
    def __init__(self, nomeVar):
        super().__init__(
			f"Variavel <b>{nomeVar}</b> atribuida mas nao lida.",
			LanguageNoteType.WARNING
		)

#endregion

#region Funcoes

class FuncaoNaoDefinida(LanguageNote):
	def __init__(self, nomeFunc, argsFunc):
		args = ", ".join([str(x) for x in argsFunc])
		funcao = nomeFunc + " ( " + args + " )"
		super().__init__(
			f"Funcao <b>{funcao}</b> nao definida.",
			LanguageNoteType.ERROR
		)

class FuncaoRedefinida(LanguageNote):
	def __init__(self, nomeFunc, argsFunc, posicaoPrimeiraDef):
		args = ", ".join([str(x) for x in argsFunc])
		funcao = nomeFunc + " ( " + args + " )"
		super().__init__(
			f"Funcao <b>{funcao}</b> redefinida.<br>Definida previamente na linha {posicaoPrimeiraDef[0]}, coluna {posicaoPrimeiraDef[1]}.",
			LanguageNoteType.ERROR
		)

#endregion

#region Tipos

class TipoInvalido(LanguageNote):
    def __init__(self, tipo):
        super().__init__(
			f"Utilizacao de um tipo invalido <b>{tipo}</b>.",
			LanguageNoteType.ERROR
		)

class EstruturaTiposIncompativeis(LanguageNote):
    def __init__(self, tipo1, tipo2):
        super().__init__(
			f"Estrutura com elementos de tipos incompativeis <b>{tipo1}</b> e <b>{tipo2}</b>.",
			LanguageNoteType.ERROR
		)

class AtribuicaoInvalida(LanguageNote):
    def __init__(self, tipoIn, tipoOut):
        super().__init__(
			f"Atribuicao invalida de uma expressao do tipo <b>{tipoIn}</b> para o tipo <b>{tipoOut}</b>.",
			LanguageNoteType.ERROR
		)

class CastInvalido(LanguageNote):
    def __init__(self, tipoCast, tipoExp):
        super().__init__(
			f"Cast invalido de uma expressao do tipo <b>{tipoExp}</b> para o tipo <b>{tipoCast}</b>.",
			LanguageNoteType.ERROR
		)

class AcessoInvalido(LanguageNote):
    def __init__(self, tipo):
        super().__init__(
			f"Acesso invalido a um valor do tipo <b>{tipo}</b>.",
			LanguageNoteType.ERROR
		)

class ChaveAcessoInvalida(LanguageNote):
    def __init__(self, tipoEstrutura, tipoKey, tipoKeyEsperada):
        super().__init__(
			f"Acesso invalido a uma estrutura do tipo <b>{tipoEstrutura}</b> com uma chave do tipo <b>{tipoKey}</b>.<br>Esperada uma chave do tipo <b>{tipoKeyEsperada}</b>.",
			LanguageNoteType.ERROR
		)

class IteracaoInvalida(LanguageNote):
    def __init__(self, tipo):
        super().__init__(
			f"Iteracao invalida de um valor do tipo <b>{tipo}</b>.",
			LanguageNoteType.ERROR
		)

#endregion

#region Operacoes

class OperadorBinarioInvalido(LanguageNote):
    def __init__(self, operador, tipoEsq, tipoDir):
        super().__init__(
			f"Tipos de dados <b>{tipoEsq}</b> e <b>{tipoDir}</b> invalidos no operador binario <b>{operador}</b>.",
			LanguageNoteType.ERROR
		)

class OperadorUnarioInvalido(LanguageNote):
    def __init__(self, operador, tipo):
        super().__init__(
			f"Tipo de dados <b>{tipo}</b> invalido no operador unario <b>{operador}</b>.",
			LanguageNoteType.ERROR
		)

class CondicaoIfInvalida(LanguageNote):
    def __init__(self):
        super().__init__(
			f"A condicao da operacao <b>If</b> nao corresponde a um valor do tipo <b>bool</b>.",
			LanguageNoteType.WARNING
		)

class CondicaoWhileInvalida(LanguageNote):
	def __init__(self, isDoWhile):
		ciclo = "Do While" if isDoWhile else "While"
		super().__init__(
			f"A condicao do ciclo <b>{ciclo}</b> nao corresponde a um valor do tipo <b>bool</b>.",
			LanguageNoteType.WARNING
		)

class CondicaoForInvalida(LanguageNote):
    def __init__(self):
        super().__init__(
			f"A condicao do ciclo <b>For</b> nao corresponde a um valor do tipo <b>bool</b>.",
			LanguageNoteType.WARNING
		)

class IfsAninhadosAgrupaveis(LanguageNote):
    def __init__(self):
        super().__init__(
			f"Os <b>If</b>s aninhados podem ser agrupados num so <b>If</b>.",
			LanguageNoteType.WARNING
		)

#endregion

#region Outras

class NomeProibido(LanguageNote):
	def __init__(self, nome, isVariavel):
		tipo = "variavel" if isVariavel else "funcao"
		super().__init__(
			f"A palavra <b>{nome}</b> nao pode ser utilizada como o nome de uma {tipo}.",
			LanguageNoteType.ERROR
		)

#endregion

#region Relatorio

class NumeroAcessosVariaveis(LanguageNote):
	def __init__(self, variaveis):
		linhas = []
		for var in variaveis:
			linhas.append(f"Variavel <b>{var.nome}</b> do tipo <b>{var.tipo}</b>: {var.num_reads} reads; {var.num_writes} writes.")
		message = "<br>".join(linhas)
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

class NumeroTipos(LanguageNote):
	def __init__(self, tipos):
		numTipos = len(tipos.keys())
		linhas = [f"O codigo contem <b>{numTipos} tipos</b> diferentes.<br>"]
		for tipo, num in tipos.items():
			linhas.append(f"Ocorreram <b>{num}</b> ocorrencias do tipo <b>{tipo}</b>.")
		message = "<br>".join(linhas)
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

class NumeroOperacoes(LanguageNote):
	def __init__(self, numOperacoes, operacoes):
		linhas = [f"O codigo contem <b>{numOperacoes} operacoes</b>.<br>"]
		for nome, num in operacoes.items():
			linhas.append(f"Ocorreram <b>{num}</b> operacoes do tipo <b>{nome}</b>.")
		message = "<br>".join(linhas)
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

class NumeroOperacoesDepth(LanguageNote):
	def __init__(self, depths):
		linhas = []
		for depth, num in depths.items():
			linhas.append(f"Ocorreram <b>{num}</b> operacoes com profundeza <b>{depth}</b>.")
		message = "<br>".join(linhas)
		super().__init__(
			message,
			LanguageNoteType.INFO
		)

#endregion