from lark import Lark, Tree, Token
from lark.visitors import Interpreter

from aux_classes import *
from aux_exceptions import *

class MyInterpreter(Interpreter):

    #region Variaveis do Interpreter

    scopes = []
    funcoes = {}
    palavrasReservadas = {"True", "False"}

    #endregion

    #region Metodos Auxiliares

    def getVariavel(self, nome):
        for scope in self.scopes:
            if nome in scope.keys():
                return scope[nome]
        return None

    def definirVariavel(self, var):
        # Verificar se o nome da variavel e valido
        if var.nome in self.palavrasReservadas:
            raise NomeProibidoException(var.nome)
        # Verificar se a variavel existe
        old_var = self.getVariavel(var.nome)
        if old_var is not None:
            raise VariavelRedefinidaException(var.nome)
        # Definir a variavel
        scope = len(self.scopes) - 1
        self.scopes[scope][var.nome] = var

    def inicializarVariavel(self, nome):
        for scope in self.scopes:
            if nome in scope.keys():
                scope[nome].inicializada = True
                return

    def definirFuncao(self, func):
        # Verificar se o nome da funcao e valido
        if func.nome in self.palavrasReservadas:
            raise NomeProibidoException(func.nome)
        # Verificar se a funcao existe
        self.funcoes.setdefault(func.nome, [])
        for other_func in self.funcoes[func.nome]:
            if func.args_tipo == other_func.args_tipo:
                raise FuncaoRedefinidaException(func.nome, func.args_tipo)
        # Definir a funcao
        self.funcoes[func.nome].append(func)

    def validarFuncaoCall(self, nome, args_tipo):
        # Verificar se existe alguma funcao com o mesmo nome
        if nome not in self.funcoes:
            raise FuncaoNaoDefinidaException(nome, args_tipo)
        # Verificar se existe alguma funcao com o mesmo nome e argumentos
        tipo_ret = None
        for func in self.funcoes[nome]:
            if func.args_tipo == args_tipo:
                tipo_ret = func.tipo_ret
                break
        if tipo_ret is None:
            raise FuncaoNaoDefinidaException(nome, args_tipo)
        return tipo_ret
    
    def validarAtribuicao(self, nomeVar, tipoVar, tipoVal):
        conversoesValidas = {
            "void"  : {},
            "int"   : {},
            "float" : {"int"},
            "bool"  : {}
        }
        if tipoVar != tipoVal and tipoVal not in conversoesValidas[tipoVar]:
            TipoVariavelException(nomeVar, tipoVar, tipoVal)

    def validarCast(self, tipoCast, tipoExp):
        conversoesValidas = {
            "void"  : {},
            "int"   : {"float", "bool"},
            "float" : {"int", "bool"},
            "bool"  : {}
        }
        if tipoCast != tipoExp and tipoExp not in conversoesValidas[tipoCast]:
            raise TipoCastException(tipoCast, tipoExp)

    def getMembrosExprBin(self, tree):
        tipoEsq = self.visit(tree.children[0])
        tipoDir = self.visit(tree.children[2])
        operador = tree.children[1].value
        return tipoEsq, tipoDir, operador

    #endregion

    #region Start

    def start(self, tree):
        try:
            self.visit(tree.children[0])
            print("O código é válido")
        except LanguageException as e:
            print(f"Erro: {e}")

    def codigo(self, tree):
        # Criar um scope para as variaveis globais
        self.scopes.append(dict())
        # Processar as operacoes
        for elem in tree.children:
            self.visit(elem)
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)

    #endregion

    #region Funcoes

    def funcao(self, tree):
        nome = tree.children[1].value
        tipo_return = self.visit(tree.children[0])
        if len(tree.children) == 3:
            args_tipo = []
            args_nome = []
        else:
            args_tipo, args_nome = self.visit(tree.children[2])
        # Definir a funcao
        self.definirFuncao(Funcao(nome, args_tipo, args_nome, tipo_return))
        # Criar um scope para os args e adiciona-los
        self.scopes.append(dict())
        for tipo, nome in zip(args_tipo, args_nome):
            self.definirVariavel(Variavel(nome, tipo, True))
        # Validar o corpo
        idx = len(tree.children) - 1
        self.visit(tree.children[idx])
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)

    def funcao_args(self, tree):
        args_tipo = []
        args_nome = []
        for idx in range(0, len(tree.children), 2):
            args_tipo.append(self.visit(tree.children[idx]))
            args_nome.append(tree.children[idx + 1].value)
        return args_tipo, args_nome
   
    def funcao_call(self, tree):
        nome = tree.children[0].value
        if len(tree.children) == 2:
            args_tipo = self.visit(tree.children[1])
        else:
            args_tipo = []
        # Validar a funcao
        tipo_ret = self.validarFuncaoCall(nome, args_tipo)
        return tipo_ret

    def funcao_call_args(self, tree):
        tipos = []
        for element in tree.children:
            tipo = self.visit(element)
            tipos.append(tipo)
        return tipos

    def corpo(self, tree):
        # Criar novo scope
        self.scopes.append(dict())
        # Validar operacoes
        for elemento in tree.children:
            self.visit(elemento.children[0])
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)

    #endregion

    #region Declaracoes / Atribuicoes

    def decl(self, tree):
        # Validar variavel
        nome = tree.children[1].value
        tipo = self.visit(tree.children[0])
        self.definirVariavel(Variavel(nome, tipo, False))
    
    def decl_atrib(self, tree):
        # Definir a variavel
        nome = tree.children[1].value
        tipo = self.visit(tree.children[0])
        self.definirVariavel(Variavel(nome, tipo, True))
        # Validar expressao
        tipoExpr = self.visit(tree.children[2])
        self.validarAtribuicao(nome, tipo, tipoExpr)

    def atrib(self, tree):
        # Validar a variavel
        nome = tree.children[0].value
        var = self.getVariavel(nome)

        # Verificar se a variavel existe
        if var is None:
            raise VariavelNaoDefinidaException(nome)

        # Verificar se o tipo da expressao é valido
        tipoExpr = self.visit(tree.children[1])
        self.validarAtribuicao(nome, var.tipo, tipoExpr)
        
        # Se a atribuicao for binaria ou unaria
        if tree.children[1].children[0].data != "atrib_simples":
            # Verificar se a variavel foi inicializada
            if not var.inicializada:
                raise VariavelNaoInicializadaException(nome)
            # Verificar se a variavel pode ser utilizada numa atribuicao complexa
            if var.tipo not in {"int", "float"}:
                atribuicaoBin = tree.children[1].children[0].data == "atrib_bin"
                raise TipoAtribuicaoComplexaException(nome, atribuicaoBin)

        # Inicializar a variavel
        if not var.inicializada:
            self.inicializarVariavel(nome)
    
    def atrib_aux(self, tree):
        return self.visit(tree.children[0])

    def atrib_simples(self, tree):
        tipoExpr = self.visit(tree.children[0])
        return tipoExpr
    
    def atrib_bin(self, tree):
        tipoExpr = self.visit(tree.children[1])
        return tipoExpr

    def atrib_un(self, tree):
        return "int"

    #endregion

    #region Condicionais

    def cond(self, tree):
        for element in tree.children:
            self.visit(element)

    def cond_if(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do If
        if tipo != "bool":
            raise CondicaoIfException()
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
        if tipo != "bool":
            raise CondicaoWhileException()
        self.visit(tree.children[1])

    def ciclo_do_while(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do While
        if tipo != "bool":
            raise CondicaoWhileException()
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
        if tipo != "bool":
            raise CondicaoForException()
    
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
            if tipoEsq != "bool" or tipoDir != "bool":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_and(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq != "bool" or tipoDir != "bool":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_eq(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq == "void" or tipoDir == "void":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_ord(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq != "bool" or tipoDir != "bool":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_add(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq not in {"int", "float"} or tipoDir not in {"int", "float"}:
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "float" if "float" in {tipoEsq, tipoDir} else "int"
    
    def expr_mul(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq not in {"int", "float"} or tipoDir not in {"int", "float"}:
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "float" if "float" in {tipoEsq, tipoDir} else "int"

    def expr_un(self, tree):
        # Se nao houverem operadores
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        # Se houverem operadores
        else:
            tipoExp = self.visit(tree.children[1])
            operador = tree.children[0].children[0]

            # Se for cast
            if isinstance(operador, Tree):
                tipoCast = self.visit(operador.children[0])
                # Verificar se o cast e valido
                self.validarCast(tipoCast, tipoExp)
                return tipoCast

            # Se for "+" ou "-"
            elif operador.value in {"+", "-"}:
                # Verificar se do operador e valido
                if tipoExp not in {"int", "float"}:
                    raise TipoOperadorUnException(operador.value, tipoExp)
                return tipoExp
            # Se for "!" converter para int
            elif operador.value == "!":
                # Verificar se do operador e valido
                if tipoExp != "bool":
                    raise TipoOperadorUnException(operador.value, tipoExp)
                return tipoExp

    def expr_symb(self, tree):
        return self.visit(tree.children[0])

    #endregion

    #region Outros

    # Retorna o tipo em formato string
    def type(self, tree):
        return tree.children[0].value

    # Retorna o tipo do valor
    def val(self, tree):
        element = tree.children[0]

        # Se for um numero
        if isinstance(element, Tree) and element.data == "num":
            tipo = element.children[0].type.lower()
            return tipo

        # Se for uma function call
        elif isinstance(element, Tree) and element.data == "funcao_call":
            tipo = self.visit(element)
            return tipo

        # Se for um bool
        elif element.type == "BOOL":
            return "bool" 

        # Se for uma variavel
        elif element.type == "VAR":
            # Validar variavel
            nome = element.value
            var = self.getVariavel(nome)
            # Verificar se a variavel existe
            if var is None:
                raise VariavelNaoDefinidaException(nome)
            # Verificar se a variavel foi inicializada
            if not var.inicializada:
                raise VariavelNaoInicializadaException(nome)
            return var.tipo

    #endregion