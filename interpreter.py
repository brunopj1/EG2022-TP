from lark import Tree, Token
from lark.visitors import Interpreter
from functools import reduce

from aux_classes import *
from language_notes import *
from tipos import *

# TODO adicionar a linha e coluna do erro
# TODO se tiver tempo fazer returns

class MyInterpreter(Interpreter):

    def __init__(self):
        super().__init__()
        self.setupVariables()

    def setupVariables(self):
        # Variaveis do interpreter

        self.palavrasReservadas = set()
        self.palavrasReservadas.update({ "True", "False" })
        self.palavrasReservadas.update(Tipo.getNomeTipos())
        
        self.variaveis = []
        self.funcoes = {}

        self.scopeAtual = []
        self.proximoScope = 0

        self.depth = -1

        # Variaveis de relatorio

        self.registoVariaveis = []
        self.registoTipos = {}
        self.registoOperacoes = {}
        self.numeroOperacoes = 0
        self.registoDepths = {}

        self.notas = []

    #region Variaveis do Interpreter

    #region Metodos Auxiliares do Interpreter

    def addScope(self, mudarDepth):
        self.variaveis.append(dict())
        # Mudar a depth
        if mudarDepth:
            self.depth += 1
            self.registoDepths.setdefault(self.depth, 0)
            self.scopeAtual.append(self.proximoScope)
            self.proximoScope = 0

    def popScope(self, mudarDepth):
        vars = self.variaveis.pop(len(self.variaveis) - 1)
        # Mudar a depth
        if mudarDepth:
            self.depth -= 1
            idx = len(self.scopeAtual) - 1
            self.proximoScope = self.scopeAtual.pop(idx) + 1
        # Processar Warnings das variaveis
        for var in vars.values():
            if var.num_reads == 0:
                if var.num_writes == 0:
                    self.saveNote(VariavelNaoUtilizada(var.nome))
                else:
                    self.saveNote(VariavelNaoLida(var.nome))

    def getVariavel(self, nome):
        for scope in self.variaveis:
            if nome in scope.keys():
                return scope[nome]
        return None

    def definirVariavel(self, var):
        # Verificar se o nome da variavel e valido
        if var.nome in self.palavrasReservadas:
            self.saveNote(NomeProibido(var.nome))
            return
        # Verificar se a variavel existe
        old_var = self.getVariavel(var.nome)
        if old_var is not None:
            self.saveNote(VariavelRedefinida(var.nome))
            return
        # Definir a variavel
        scope = len(self.variaveis) - 1
        self.variaveis[scope][var.nome] = var
        # Guardar o registo da variavel
        self.registoVariaveis.append(var)
        # Guardar o registo do tipo
        self.registoTipos.setdefault(var.tipo, 0)
        self.registoTipos[var.tipo] += 1

    def definirFuncao(self, func):
        # Verificar se o nome da funcao e valido
        if func.nome in self.palavrasReservadas:
            self.saveNote(NomeProibido(func.nome))
            return
        # Verificar se a funcao existe
        self.funcoes.setdefault(func.nome, [])
        for other_func in self.funcoes[func.nome]:
            if func.args_tipo == other_func.args_tipo:
                self.saveNote(FuncaoRedefinida(func.nome, func.args_tipo))
                return
        # Definir a funcao
        self.funcoes[func.nome].append(func)

    def getTipoNumeroComum(self, tipo1, tipo2):
        if isinstance(tipo1, Tipo_Float) or isinstance(tipo2, Tipo_Float):
            return Tipo_Float()
        else:
            return Tipo_Int()

    def getMembrosExprBin(self, tree):
        tipoEsq = self.visit(tree.children[0])
        tipoDir = self.visit(tree.children[2])
        operador = tree.children[1].value
        return tipoEsq, tipoDir, operador

    def determinarSubtipoComum(self, elementos):
        subtipos = set()
        # Determinar todos os tipos
        for elem in elementos:
            subtipos.add(self.visit(elem))
        # Determinar o tipo comum
        while len(subtipos) > 1:
            it = iter(subtipos)
            tipo1 = next(it)
            tipo2 = next(it)
            # Se o tipo1 poder ser convertido no tipo2
            if tipo1.atribuicaoValida(tipo2):
                subtipos.remove(tipo1)
            # Se o tipo2 poder ser convertido no tipo1
            elif tipo2.atribuicaoValida(tipo1):
                subtipos.remove(tipo2)
            # Se nao houver conversao
            else:
                self.saveNote(EstruturaTiposIncompativeis(tipo1, tipo2))
                return Tipo_Unknown()
        # Retornar o tipo
        return subtipos.pop()

    #endregion

    #region Metodos Auxiliares de Relatorio

    def saveNote(self, note):
        self.notas.append(note)

    def gerarNotesInfo(self):
        self.saveNote(NumeroAcessosVariaveis(self.registoVariaveis))
        self.saveNote(NumeroTipos(self.registoTipos))
        self.saveNote(NumeroOperacoes(self.numeroOperacoes, self.registoOperacoes))
        self.saveNote(NumeroOperacoesDepth(self.registoDepths))
    
    #endregion

    #region Start

    def start(self, tree):
        self.visit(tree.children[0])

    def codigo(self, tree):
        # Criar um scope
        self.addScope(True)
        # Processar as operacoes
        for elem in tree.children:
            # Registar a operacao
            self.registoOperacoes.setdefault(elem.data, 0)
            self.registoOperacoes[elem.data] += 1
            # Contar o numero de operacoes
            if elem.data != "cond":
                self.numeroOperacoes += 1
            # Registar a operacao na depth atual
            if elem.data != "cond":
                self.registoDepths[self.depth] += 1
            # Visitar a operacao
            self.visit(elem)
        # Apagar o scope
        self.popScope(True)

    def corpo(self, tree):
        # Criar novo scope
        self.addScope(True)
        # Set de variaveis inicializadas no corpo
        varsInicializadas = set()
        # Validar operacoes
        for elem in tree.children:
            elem = elem.children[0]
            # Registar a operacao
            _elem = elem
            if _elem.data == "atrib":
                _elem = _elem.children[1].children[0]
            self.registoOperacoes.setdefault(_elem.data, 0)
            self.registoOperacoes[_elem.data] += 1
            # Contar o numero de operacoes
            if elem.data != "cond":
                self.numeroOperacoes += 1
            # Registar a operacao na depth atual
            if _elem.data != "cond":
                self.registoDepths[self.depth] += 1
            # Visitar a operacao
            var = self.visit(elem)
            if var is not None:
                varsInicializadas.add(var)
        # Apagar o scope
        self.popScope(True)
        # Retornar as variaveis inicializadas no corpo
        return varsInicializadas

    #endregion

    #region Funcoes

    def funcao(self, tree):
        # Criar um scope para os args
        self.addScope(False)
        # Definir a funcao
        nome = tree.children[1].value
        tipo_return = self.visit(tree.children[0])
        args = self.visit(tree.children[2])
        self.definirFuncao(Funcao(nome, tipo_return, args))
        # Validar o corpo
        self.visit(tree.children[3])
        # Apagar o scope
        self.popScope(False)

    def funcao_args(self, tree):
        args = []
        for idx in range(0, len(tree.children), 2):
            # Definir a variavel
            tipo = self.visit(tree.children[idx])
            nome = tree.children[idx + 1].value
            self.definirVariavel(Variavel(nome, tipo, self.scopeAtual, True))
            # Guardar a variavel
            args.append((tipo, nome))
        return args
   
    def funcao_call(self, tree):
        nome = tree.children[0].value
        args_tipo = self.visit(tree.children[1])
        # Verificar se existe alguma funcao com o mesmo nome
        if nome not in self.funcoes:
            self.saveNote(FuncaoNaoDefinida(nome, args_tipo))
            return Tipo_Unknown()
        # Verificar se existe alguma funcao com o mesmo nome e argumentos
        for func in self.funcoes[nome]:
            if len(func.args_tipo) == len(args_tipo):
                funcaoValida = True
                for func_arg, call_arg in zip(func.args_tipo, args_tipo):
                    if not call_arg.atribuicaoValida(func_arg):
                        funcaoValida = False
                        break
                if funcaoValida:
                    return func.tipo_ret
        # A funcao nao existe
        self.saveNote(FuncaoNaoDefinida(nome, args_tipo))
        return Tipo_Unknown()

    def funcao_call_args(self, tree):
        tipos = []
        for element in tree.children:
            tipo = self.visit(element)
            tipos.append(tipo)
        return tipos

    #endregion

    #region Declaracoes / Atribuicoes

    def decl(self, tree):
        # Validar variavel
        nome = tree.children[1].value
        tipo = self.visit(tree.children[0])
        # Definir a variavel
        self.definirVariavel(Variavel(nome, tipo, self.scopeAtual, False))
    
    def decl_atrib(self, tree):
        # Definir a variavel
        nomeVar = tree.children[1].value
        tipoVar = self.visit(tree.children[0])
        var = Variavel(nomeVar, tipoVar, self.scopeAtual, True)
        self.definirVariavel(var)
        # Registar uma operacao de write
        var.num_writes += 1
        # Validar expressao
        tipoExpr = self.visit(tree.children[2])
        if not tipoExpr.atribuicaoValida(tipoVar):
            self.saveNote(AtribuicaoInvalida(tipoExpr, tipoVar))

    def atrib(self, tree):
        varInicializada = None
        # Se for uma variavel
        if isinstance(tree.children[0], Token):
            nome = tree.children[0].value
            var = self.getVariavel(nome)
            # Verificar se a variavel existe
            if var is None:
                self.saveNote(VariavelNaoDefinida(nome))
                return
            tipoVar = var.tipo
            tipoVal = self.visit(tree.children[1].children[0])
            # Registar uma operacao de write
            var.num_writes += 1
            # Se a atribuicao for binaria ou unaria
            if tree.children[1].children[0].data != "atrib_simples":
                # Verificar se a variavel foi inicializada
                if not var.isInicializada(self.scopeAtual):
                    self.saveNote(VariavelNaoInicializada(nome))
            # Inicializar a variavel
            var.inicializar(self.scopeAtual)
            varInicializada = var
        # Se for uma expressao
        else: # isinstance(tree.children[0], Tree):
            tipoVar = self.visit(tree.children[0])
            tipoVal = self.visit(tree.children[1].children[0])
        
        # Verificar se o tipo da expressao é valido
        if not tipoVal.atribuicaoValida(tipoVar):
            self.saveNote(AtribuicaoInvalida(tipoVal, tipoVar))

        # Retornar a variavel inicializada
        return varInicializada

    def atrib_simples(self, tree):
        tipoExpr = self.visit(tree.children[0])
        return tipoExpr
    
    def atrib_bin(self, tree):
        tipoExpr = self.visit(tree.children[1])
        return tipoExpr

    def atrib_un(self, tree):
        return Tipo_Int()

    #endregion

    #region Condicionais

    def cond(self, tree):
        varsInicializadas = []
        for elem in tree.children:
            # Registar a operacao
            self.registoOperacoes.setdefault(elem.data, 0)
            self.registoOperacoes[elem.data] += 1
            # Contar o numero de operacoes
            self.numeroOperacoes += 1
            # Registar a operacao na depth atual
            self.registoDepths[self.depth] += 1
            # Visitar
            varsInicializadas.append(self.visit(elem))
        # Verificar se alguma variavel deve ser inicializada no scope externo
        if tree.children[len(tree.children) - 1].data == "cond_else":
            varsParaInicializar = reduce(lambda x, y: x.intersection(y), varsInicializadas)
            for var in varsParaInicializar:
                var.inicializar(self.scopeAtual)


    def cond_if(self, tree):
        # Validar a condicao do If
        tipo = self.visit(tree.children[0])
        if not isinstance(tipo, Tipo_Bool):
            self.saveNote(CondicaoIfInvalida())
        # Verificar se os If's se podem juntar
        operacoesCorpo = tree.children[1].children
        if len(operacoesCorpo) == 1:
            operacao = operacoesCorpo[0].children[0]
            if operacao.data == "cond" and len(operacao.children) == 1:
                self.saveNote(IfsAninhadosAgrupaveis())
        # Visitar o corpo
        varsInicializadas = self.visit(tree.children[1])
        # Retornar as variaveis inicializadas
        return varsInicializadas

    def cond_else_if(self, tree):
        varsInicializadas = self.visit(tree.children[0])
        # Retornar as variaveis inicializadas
        return varsInicializadas

    def cond_else(self, tree):
        varsInicializadas = self.visit(tree.children[0])
        # Retornar as variaveis inicializadas
        return varsInicializadas

    #endregion

    #region While

    def ciclo_while(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do While
        if not isinstance(tipo, Tipo_Bool):
            self.saveNote(CondicaoWhileInvalida(False))
        self.visit(tree.children[1])

    def ciclo_do_while(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do While
        if not isinstance(tipo, Tipo_Bool):
            self.saveNote(CondicaoWhileInvalida(True))
        self.visit(tree.children[1])

    #endregion

    #region For

    def ciclo_for(self, tree):
        # Criar novo scope (para as variaveis definidas no head)
        self.addScope(False)
        # Visitar o head e o corpo
        self.visit(tree.children[0])
        self.visit(tree.children[1])
        # Apagar o scope
        self.popScope(False)
    
    def ciclo_for_head(self, tree):
        for element in tree.children:
            self.visit(element)
    
    def ciclo_for_head_1(self, tree):
        for element in tree.children:
            self.visit(element)
    
    def ciclo_for_head_2(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do For
        if not isinstance(tipo, Tipo_Bool):
            self.saveNote(CondicaoForInvalida())
    
    def ciclo_for_head_3(self, tree):
        for element in tree.children:
            self.visit(element)

    def ciclo_foreach(self, tree):
        # Criar novo scope (para as variaveis definidas no head)
        self.addScope(False)
        # Visitar a head e o corpo
        self.visit(tree.children[0])
        self.visit(tree.children[1])
        # Apagar o scope
        self.popScope(False)

    # type VAR_NOME "in" expr
    def ciclo_foreach_head(self, tree):
        # Declarar a variavel
        tipoVar = self.visit(tree.children[0])
        nomeVar = tree.children[1].value
        self.definirVariavel(Variavel(nomeVar, tipoVar, self.scopeAtual, True))
        # Validar o tipo da variavel
        tipoVal = self.visit(tree.children[2])
        tipoIter, erro = tipoVal.validarIteracao()
        if erro is not None:
            self.saveNote(erro)
        if not tipoIter.atribuicaoValida(tipoVar):
            self.saveNote(AtribuicaoInvalida(tipoIter, tipoVar))

    #endregion

    #region Expressoes

    # Todas as funcoes de visita de expressoes retornam o tipo final da expressao
    def expr(self, tree):
        return self.visit(tree.children[0])
    
    def expr_or(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Bool()) or not tipoDir.atribuicaoValida(Tipo_Bool()):
                self.saveNote(OperadorBinarioInvalido(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_and(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Bool()) or not tipoDir.atribuicaoValida(Tipo_Bool()):
                self.saveNote(OperadorBinarioInvalido(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_eq(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq.atribuicaoValida(Tipo_Void()) or tipoDir.atribuicaoValida(Tipo_Void()):
                self.saveNote(OperadorBinarioInvalido(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_ord(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Float()) or not tipoDir.atribuicaoValida(Tipo_Float()):
                self.saveNote(OperadorBinarioInvalido(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_add(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Float()) or not tipoDir.atribuicaoValida(Tipo_Float()):
                self.saveNote(OperadorBinarioInvalido(operador, tipoEsq, tipoDir))
            return self.getTipoNumeroComum(tipoEsq, tipoDir)
    
    def expr_mul(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Float()) or not tipoDir.atribuicaoValida(Tipo_Float()):
                self.saveNote(OperadorBinarioInvalido(operador, tipoEsq, tipoDir))
            return self.getTipoNumeroComum(tipoEsq, tipoDir)

    def expr_un(self, tree):
        # Se nao houverem operadores
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        # Se houverem operadores
        else:
            tipoExp = self.visit(tree.children[1])
            operador = tree.children[0].children[0]

            # Se for cast
            if isinstance(operador, Tree) and operador.data == "op_expr_cast":
                tipoCast = self.visit(operador.children[0])
                # Verificar se o cast e valido
                if not tipoExp.castValido(tipoCast):
                    self.saveNote(CastInvalido(tipoCast, tipoExp))
                return tipoCast

            # Se for "+" ou "-"
            elif operador.value in {"+", "-"}:
                # Verificar se do operador e valido
                if not tipoExp.atribuicaoValida(Tipo_Float()):
                    self.saveNote(OperadorUnarioInvalido(operador.value, tipoExp))
                    return Tipo_Int()
                return tipoExp
            # Se for "!" converter para int
            elif operador.value == "!":
                # Verificar se do operador e valido
                if not tipoExp.atribuicaoValida(Tipo_Bool()):
                    self.saveNote(OperadorUnarioInvalido(operador.value, tipoExp))
                return Tipo_Bool()

    def expr_symb(self, tree):
        # Se for um valor ou uma expressao entre parenteses
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        # Se for um acesso a um tipo complexo
        else:
            # Obter o tipo de ambas as expressoes
            tipoVal = self.visit(tree.children[0])
            tipoKey = self.visit(tree.children[1])    
            # Validar o tipo final do acesso
            tipoFinal, erro = tipoVal.validarAcesso(tipoKey)
            if erro is not None:
                self.saveNote(erro)
            return tipoFinal

    #endregion

    #region Tipos

    # Retorna o tipo
    def type(self, tree):
        nome = tree.children[0].value
        # Processar subtipos
        if len(tree.children) == 2:
            subtipos = self.visit(tree.children[1])
        else:
            subtipos = []
        # Validar o tipo
        tipo, erro = Tipo.fromNome(nome, subtipos)
        if erro is not None:
            self.saveNote(erro)
        return tipo

    # Retorna a lista de subtipos
    def subtype(self, tree):
        subtipos = []
        for elem in tree.children:
            subtipos.append(self.visit(elem))
        return subtipos

    #endregion

    #region Valores

    # Retorna o tipo do valor
    def val(self, tree):
        element = tree.children[0]

        # Se for um numero
        if isinstance(element, Tree) and element.data == "num":
            if element.children[0].type.lower() == "int":
                return Tipo_Int()
            else: # element.children[0].type.lower() == "float":
                return Tipo_Float()

        # Se for um bool
        elif isinstance(element, Token) and element.type == "BOOL":
            return Tipo_Bool()

        # Se for uma variavel
        elif isinstance(element, Token) and element.type == "VAR_NOME":
            # Validar variavel
            nome = element.value
            var = self.getVariavel(nome)
            # Verificar se a variavel existe
            if var is None:
                self.saveNote(VariavelNaoDefinida(nome))
                return Tipo_Unknown()
            # Registar uma operacao de write
            var.num_reads += 1
            # Verificar se a variavel foi inicializada
            if not var.isInicializada(self.scopeAtual):
                self.saveNote(VariavelNaoInicializada(nome))
            return var.tipo

        # Se for um tipo complexo
        elif isinstance(element, Tree) and element.data == "struct":
            
            element = element.children[0]

            # Se estiver vazio
            if len(element.children) == 0:
                if element.data == "map":
                    subtipos = [Tipo_Unknown(), Tipo_Unknown()]
                else:
                    subtipos = [Tipo_Unknown()]
            # Se nao estiver vazio
            else:
                if element.data == "map":
                    subtipo1 = self.determinarSubtipoComum(element.children[0::2])
                    subtipo2 = self.determinarSubtipoComum(element.children[1::2])
                    subtipos = [subtipo1, subtipo2]
                elif element.data == "tuple":
                    subtipos = list(map(lambda elem : self.visit(elem), element.children))
                else:
                    subtipos = [self.determinarSubtipoComum(element.children)]
            # Retornar
            nome_tipo = element.data.capitalize()
            tipo, erro = Tipo.fromNome(nome_tipo, subtipos)
            if erro is not None:
                self.saveNote(erro)
            return tipo

        # Se for uma function call
        else:
            tipo = self.visit(element)
            return tipo

    #endregion