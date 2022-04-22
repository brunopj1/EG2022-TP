from lark import Tree, Token
from lark.visitors import Interpreter

from aux_classes import *
from language_notes import *
from tipos import *

# TODO adicionar a linha e coluna do erro
# TODO variaveis nao inicializadas esta mal feito (scopes)
# TODO se tiver tempo fazer returns
# TODO se tiver tempo fazer foreach
# TODO se tiver tempo fazer warnings para variaveis nao usadas
# TODO nao declarar a variavel quando o tipo é invalido

class MyInterpreter(Interpreter):

    #region Variaveis do Interpreter

    # Variaveis de controlo
    scopes = []
    funcoes = {}
    palavrasReservadas = { "True", "False" }

    # Variaveis de relatorio
    registoVariaveis = []

    registoTipos = {}

    registoOperacoes = {}
    numeroOperacoes = 0

    registoDepths = {}
    depth = 0

    notas = []

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

    #region Metodos Auxiliares do Interpreter

    def getVariavel(self, nome):
        for scope in self.scopes:
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
        scope = len(self.scopes) - 1
        self.scopes[scope][var.nome] = var
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
                self.saveNote(TipoEstrutura(tipo1, tipo2))
                return Tipo_Anything()
        # Retornar o tipo
        return subtipos.pop()

    #endregion

    #region Start

    def start(self, tree):
        self.visit(tree.children[0])

    def codigo(self, tree):
        # Criar um scope para as variaveis globais
        self.scopes.append(dict())
        # Inicializar a depth 0
        self.registoDepths[0] = 0
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
        self.scopes.pop(len(self.scopes) - 1)

    def corpo(self, tree):
        # Criar novo scope
        self.scopes.append(dict())
        # Incrementar a depth
        self.depth += 1
        self.registoDepths.setdefault(self.depth, 0)
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
            self.visit(elem)
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)
        # Decrementar a depth
        self.depth -= 1

    #endregion

    #region Funcoes

    def funcao(self, tree):
        nome = tree.children[1].value
        tipo_return = self.visit(tree.children[0])
        args = self.visit(tree.children[2])
        # Definir a funcao
        self.definirFuncao(Funcao(nome, tipo_return, args))
        # Criar um scope para os args e adiciona-los
        self.scopes.append(dict())
        # Validar o corpo
        self.visit(tree.children[3])
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)

    def funcao_args(self, tree):
        args = []
        for idx in range(0, len(tree.children), 2):
            # Definir a variavel
            tipo = self.visit(tree.children[idx])
            nome = tree.children[idx + 1].value
            self.definirVariavel(Variavel(nome, tipo, True))

            # Guardar a variavel
            args.append((tipo, nome))
        return args
   
    def funcao_call(self, tree):
        nome = tree.children[0].value
        args_tipo = self.visit(tree.children[1])
        # Verificar se existe alguma funcao com o mesmo nome
        if nome not in self.funcoes:
            self.saveNote(FuncaoNaoDefinida(nome, args_tipo))
            return Tipo_Anything()
        # Verificar se existe alguma funcao com o mesmo nome e argumentos
        for func in self.funcoes[nome]:
            if func.args_tipo == args_tipo:
                return func.tipo_ret
        # A funcao nao existe
        self.saveNote(FuncaoNaoDefinida(nome, args_tipo))
        return Tipo_Anything()

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
        self.definirVariavel(Variavel(nome, tipo, False))
    
    def decl_atrib(self, tree):
        # Definir a variavel
        nomeVar = tree.children[1].value
        tipoVar = self.visit(tree.children[0])
        var = Variavel(nomeVar, tipoVar, True)
        self.definirVariavel(var)
        # Registar uma operacao de write
        var.num_writes += 1
        # Validar expressao
        tipoExpr = self.visit(tree.children[2])
        if not tipoExpr.atribuicaoValida(tipoVar):
            self.saveNote(TipoVariavel(nomeVar, tipoVar, tipoExpr))

    def atrib(self, tree):

        nome = tree.children[0].value
        var = self.getVariavel(nome)
        tipoExpr = self.visit(tree.children[1].children[0])

        # Verificar se a variavel existe
        if var is None:
            self.saveNote(VariavelNaoDefinida(nome))
            return

        # Registar uma operacao de write
        var.num_writes += 1

        # Registar uma operacao de read
        if tree.children[1].children[0].data != "atrib_simples":
            var.num_reads += 1

        # Verificar se o tipo da expressao é valido
        if not tipoExpr.atribuicaoValida(var.tipo):
            self.saveNote(TipoVariavel(nome, var.tipo, tipoExpr))
        
        # Se a atribuicao for binaria ou unaria
        if tree.children[1].children[0].data != "atrib_simples":
            # Verificar se a variavel foi inicializada
            if not var.inicializada:
                self.saveNote(VariavelNaoInicializada(nome))
            # Verificar se a variavel pode ser utilizada numa atribuicao complexa
            if not var.tipo.atribuicaoValida(Tipo_Float()):
                self.saveNote(TipoAtribuicaoBinaria(nome))

        # Inicializar a variavel
        if not var.inicializada:
            var.inicializada = True
    
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
        for elem in tree.children:
            # Registar a operacao
            self.registoOperacoes.setdefault(elem.data, 0)
            self.registoOperacoes[elem.data] += 1
            # Contar o numero de operacoes
            self.numeroOperacoes += 1
            # Registar a operacao na depth atual
            self.registoDepths[self.depth] += 1
            # Visitar
            self.visit(elem)

    def cond_if(self, tree):
        # Validar a condicao do If
        tipo = self.visit(tree.children[0])
        if not isinstance(tipo, Tipo_Bool):
            self.saveNote(CondicaoIf())
        # Verificar se os If's se podem juntar
        operacoesCorpo = tree.children[1].children
        if len(operacoesCorpo) == 1:
            operacao = operacoesCorpo[0].children[0]
            if operacao.data == "cond" and len(operacao.children) == 1:
                self.saveNote(IfsAninhados())
        # Visitar o corpo
        self.visit(tree.children[1])

    def cond_else_if(self, tree):
        self.visit(tree.children[0])

    def cond_else(self, tree):
        self.visit(tree.children[0])

    #endregion

    #region While

    def ciclo_while(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do While
        if not isinstance(tipo, Tipo_Bool):
            self.saveNote(CondicaoWhile())
        self.visit(tree.children[1])

    def ciclo_do_while(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do While
        if not isinstance(tipo, Tipo_Bool):
            self.saveNote(CondicaoWhile())
        self.visit(tree.children[1])

    #endregion

    #region For

    def ciclo_for(self, tree):
        # Criar novo scope (para as variaveis definidas no head)
        self.scopes.append(dict())
        # Visitar o head e o corpo
        self.visit(tree.children[0])
        self.visit(tree.children[1])
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)
    
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
            self.saveNote(CondicaoFor())
    
    def ciclo_for_head_3(self, tree):
        for element in tree.children:
            self.visit(element)

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
                self.saveNote(TipoOperadorBin(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_and(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Bool()) or not tipoDir.atribuicaoValida(Tipo_Bool()):
                self.saveNote(TipoOperadorBin(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_eq(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq.atribuicaoValida(Tipo_Void()) or tipoDir.atribuicaoValida(Tipo_Void()):
                self.saveNote(TipoOperadorBin(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_ord(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Float()) or not tipoDir.atribuicaoValida(Tipo_Float()):
                self.saveNote(TipoOperadorBin(operador, tipoEsq, tipoDir))
            return Tipo_Bool()
    
    def expr_add(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Float()) or not tipoDir.atribuicaoValida(Tipo_Float()):
                self.saveNote(TipoOperadorBin(operador, tipoEsq, tipoDir))
            return self.getTipoNumeroComum(tipoEsq, tipoDir)
    
    def expr_mul(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not tipoEsq.atribuicaoValida(Tipo_Float()) or not tipoDir.atribuicaoValida(Tipo_Float()):
                self.saveNote(TipoOperadorBin(operador, tipoEsq, tipoDir))
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
                    self.saveNote(TipoCast(tipoCast, tipoExp))
                return tipoCast

            # Se for "+" ou "-"
            elif operador.value in {"+", "-"}:
                # Verificar se do operador e valido
                if not tipoExp.atribuicaoValida(Tipo_Float()):
                    self.saveNote(TipoOperadorUn(operador.value, tipoExp))
                return tipoExp
            # Se for "!" converter para int
            elif operador.value == "!":
                # Verificar se do operador e valido
                if not tipoExp.atribuicaoValida(Tipo_Bool()):
                    self.saveNote(TipoOperadorUn(operador.value, tipoExp))
                return tipoExp

    def expr_symb(self, tree):
        return self.visit(tree.children[0])

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
                return Tipo_Anything()
            # Registar uma operacao de write
            var.num_writes += 1
            # Verificar se a variavel foi inicializada
            if not var.inicializada:
                self.saveNote(VariavelNaoInicializada(nome))
            return var.tipo

        # Se for um tipo complexo
        elif isinstance(element, Tree) and element.data == "struct":
            
            element = element.children[0]

            # Se estiver vazio
            if len(element.children) == 0:
                if element.data == "map":
                    subtipos = [Tipo_Anything(), Tipo_Anything()]
                else:
                    subtipos = [Tipo_Anything()]
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

        # Se for um acesso a um tipo complexo
        elif isinstance(element, Tree) and element.data == "struct_acesso":

            # Obter o tipo do valor
            if isinstance(element.children[0], Token) and element.children[0].type == "VAR_NOME":
                nome = element.children[0].value
                var = self.getVariavel(nome)
                # Verificar se a variavel existe
                if var is None:
                    self.saveNote(VariavelNaoDefinida(nome))
                    tipoVal = Tipo_Anything()
                else:
                    tipoVal = var.tipo
            else: # isinstance(element.children[0], Tree) and element.children[0].data == "struct"
                tipoVal = self.visit(element.children[0])
            
            # Obter o tipo da expr
            tipoExpr = self.visit(element.children[1])

            # Validar o tipo final do acesso
            tipoFinal, erro = tipoVal.validarAcesso(tipoExpr)
            if erro is not None:
                self.saveNote(erro)

            return tipoFinal

        # Se for uma function call
        else:
            tipo = self.visit(element)
            return tipo

    #endregion