from lib2to3.pgen2 import grammar
from lark import Lark, Tree, Token
from lark.visitors import Interpreter

from aux_classes import *
from aux_exceptions import *

grammar = """
start        : corpo
corpo        : (operacao | operacao_end)*
operacao     : (cond | ciclo_while | ciclo_for)
operacao_end : (decl | decl_atrib | atrib | ciclo_do_while) ";"

decl          : TYPE VAR
decl_atrib    : TYPE VAR "=" expr
atrib         : atrib_simples | atrib_bin | atrib_un
atrib_simples : VAR "=" expr
atrib_bin     : VAR OP_BIN_ATRIB "=" expr
atrib_un      : VAR OP_UN_ATRIB
OP_BIN_ATRIB  : "+" | "-" | "*" | "/" | "%"
OP_UN_ATRIB   : "++" | "--"

cond         : cond_if cond_else_if* cond_else?
cond_if      : "if" "(" expr ")" "{" corpo "}"
cond_else_if : "else" cond_if
cond_else    : "else" "{" corpo "}"

ciclo_while    : "while" "(" expr ")" "{" corpo "}"
ciclo_do_while : "do" "{" corpo "}" "while" "(" expr ")"

ciclo_for        : "for" "(" ciclo_for_head ")" "{" corpo "}"
ciclo_for_head   : ciclo_for_head_1? ";" ciclo_for_head_2? ";" ciclo_for_head_3?
ciclo_for_head_1 : (decl | decl_atrib | atrib) ("," (decl | decl_atrib | atrib))*
ciclo_for_head_2 : expr
ciclo_for_head_3 : atrib ("," atrib)*

expr         : expr_or
expr_or      : (expr_or OP_EXPR_OR expr_or)
             | expr_and
expr_and     : (expr_and OP_EXPR_AND expr_and)
             | expr_eq
expr_eq      : (expr_eq OP_EXPR_EQ expr_eq)
             | expr_ord
expr_ord     : (expr_ord OP_EXPR_ORD expr_ord)
             | expr_add
expr_add     : (expr_add OP_EXPR_ADD expr_add)
             | expr_mul
expr_mul     : (expr_mul OP_EXPR_MUL expr_mul)
             | expr_un
expr_un      : expr_op_un expr_un
             | expr_symb
expr_symb    : (NUM | BOOL | VAR | "(" expr ")")

expr_op_un   : (OP_EXPR_UN | op_expr_cast)
op_expr_cast : "(" TYPE ")"

OP_EXPR_OR   : "||"
OP_EXPR_AND  : "&&"
OP_EXPR_EQ   : "==" | "!="
OP_EXPR_ORD  : "<" | "<=" | ">" | ">="
OP_EXPR_ADD  : "+" | "-"
OP_EXPR_MUL  : "*" | "/" | "%"
OP_EXPR_UN   : "+" | "-" | "!"

TYPE : "int" | "float" | "bool"
VAR  : /[a-zA-Z_]\w*/
NUM  : /\d+(\.\d+)?/
BOOL : "True" | "False"

%import common.WS
%ignore WS
"""

class MyInterpreter(Interpreter):

    #region Variaveis

    scopes = []

    palavrasReservadas = {"True", "False"}

    #endregion

    #region Metodos Auxiliares

    def definirVariavel(self, var):
        if var.nome in self.palavrasReservadas:
            raise NomeVariavelProibidoException(var.nome)
        scope = len(self.scopes) - 1
        self.scopes[scope][var.nome] = var

    def getVariavel(self, nome):
        for scope in self.scopes:
            if nome in scope.keys():
                return scope[nome]
        return None

    def inicializarVariavel(self, nome):
        for scope in self.scopes:
            if nome in scope.keys():
                scope[nome].inicializada = True
                return

    def atribuicaoValida(self, tipoVar, tipoVal):
        conversoesValidas = {
            "int"   : {},
            "float" : {"int"},
            "bool"  : {}
        }
        return tipoVar == tipoVal or tipoVal in conversoesValidas[tipoVar]

    def castValido(self, tipoCast, tipoExp):
        conversoesValidas = {
            "int"   : {"float", "bool"},
            "float" : {"int", "bool"},
            "bool"  : {}
        }
        return tipoCast == tipoExp or tipoExp in conversoesValidas[tipoCast]

    #endregion

    #region Corpo

    def start(self, tree):
        try:
            self.visit(tree.children[0])
            print("O código é válido")
        except LanguageException as e:
            print(f"Erro: {e}")


    def corpo(self, tree):
        # Criar novo scope
        self.scopes.append(dict())
        # Validar operacoes
        for elemento in tree.children:
            self.visit(elemento)
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)

    def operacao(self, tree):
        self.visit(tree.children[0])
    
    def operacao_end(self, tree):
        self.visit(tree.children[0])

    #endregion

    #region Declaracoes / Atribuicoes

    def decl(self, tree):
        # Validar variavel
        nome = tree.children[1].value
        var = self.getVariavel(nome)
        if var is not None:
            raise VariavelRedefinidaException(nome)
        # Declarar a variavel
        tipo = tree.children[0].value
        self.definirVariavel(Variavel(nome, tipo, False))
    
    def decl_atrib(self, tree):
        # Validar expressao
        tipoExpr = self.visit(tree.children[2])
        # Validar variavel
        nome = tree.children[1].value
        tipo = tree.children[0].value
        var = self.getVariavel(nome)
        # Verificar se a variavel existe
        if var is not None:
            raise VariavelRedefinidaException(nome)
        # Verificar se o tipo da expressao é valido
        if not self.atribuicaoValida(tipo, tipoExpr):
            raise TipoVariavelException(nome, tipo, tipoExpr)
        # Declarar a variavel
        self.definirVariavel(Variavel(nome, tipo, True))

    def atrib(self, tree):
        self.visit(tree.children[0])
    
    def atrib_simples(self, tree):
        # Validar expressao
        tipoExpr = self.visit(tree.children[1])
        # Validar variavel
        nome = tree.children[0].value
        var = self.getVariavel(nome)
        # Verificar se a variavel existe
        if var is None:
            raise VariavelNaoDefinidaException(nome)
        # Verificar se o tipo da expressao é valido
        if not self.atribuicaoValida(var.tipo, tipoExpr):
            raise TipoVariavelException(nome, var.tipo, tipoExpr)
        # Inicializar a variavel
        self.inicializarVariavel(nome)
    
    def atrib_bin(self, tree):
        # Validar expressao
        tipoExpr = self.visit(tree.children[2])
        # Validar variavel
        nome = tree.children[0].value
        var = self.getVariavel(nome)
        # Verificar se a variavel existe
        if var is None:
            raise VariavelNaoDefinidaException(nome)
        # Verificar se a variavel foi inicializada
        if not var.inicializada:
            raise VariavelNaoInicializadaException(nome)
        # Verificar se a variavel pode ser utilizada numa atribuicao binaria
        if var.tipo not in {"int", "float"}:
            raise TipoAtribuicaoComplexaException(nome, True)
        # Verificar se o tipo da expressao é valido
        if not self.atribuicaoValida(var.tipo, tipoExpr):
            raise TipoVariavelException(nome, var.tipo, tipoExpr)

    def atrib_un(self, tree):
        # Validar variavel
        nome = tree.children[0].value
        var = self.getVariavel(nome)
        # Verificar se a variavel existe
        if var is None:
            raise VariavelNaoDefinidaException(nome)
        # Verificar se a variavel foi inicializada
        if not var.inicializada:
            raise VariavelNaoInicializadaException(nome)
        # Verificar se a variavel pode ser utilizada numa atribuicao unaria
        if var.tipo not in {"int", "float"}:
            raise TipoAtribuicaoComplexaException(nome, False)

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

    def expr(self, tree):
        return self.visit(tree.children[0])
    
    def expr_or(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            operador = tree.children[1].value
            tipoEsq = self.visit(tree.children[0])
            tipoDir = self.visit(tree.children[2])
            # Validar tipos
            if tipoEsq != "bool" or tipoDir != "bool":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_and(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            operador = tree.children[1].value
            tipoEsq = self.visit(tree.children[0])
            tipoDir = self.visit(tree.children[2])
            # Validar tipos
            if tipoEsq != "bool" or tipoDir != "bool":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_eq(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            operador = tree.children[1].value
            tipoEsq = self.visit(tree.children[0])
            tipoDir = self.visit(tree.children[2])
            # Validar tipos
            if tipoEsq != "bool" or tipoDir != "bool":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_ord(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            operador = tree.children[1].value
            tipoEsq = self.visit(tree.children[0])
            tipoDir = self.visit(tree.children[2])
            # Validar tipos
            if tipoEsq != "bool" or tipoDir != "bool":
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "bool"
    
    def expr_add(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            operador = tree.children[1].value
            tipoEsq = self.visit(tree.children[0])
            tipoDir = self.visit(tree.children[2])
            # Validar tipos
            if tipoEsq not in {"int", "float"} or tipoDir not in {"int", "float"}:
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return "float" if "float" in {tipoEsq, tipoDir} else "int"
    
    def expr_mul(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            operador = tree.children[1].value
            tipoEsq = self.visit(tree.children[0])
            tipoDir = self.visit(tree.children[2])
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
                tipoCast = operador.children[0].value
                # Verificar se o cast e valido
                if not self.castValido(tipoCast, tipoExp):
                    raise TipoCastException(tipoCast, tipoExp)
                return tipoCast
            # Se for "+" ou "-"
            elif operador.value == "+" or operador.value == "-":
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
        element = tree.children[0]

        # Se o filho for uma expr
        if isinstance(element, Tree):
            return self.visit(element)

        # Se o filho for um numero
        elif element.type == "NUM":
            val = element.value
            return "float" if "." in val else "int"

        # Se o filho for um bool
        elif element.type == "BOOL":
            return "bool" 

        # Se o filho for uma variavel
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