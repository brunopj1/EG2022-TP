from lark import Lark, Tree, Token
from lark.visitors import Interpreter

from aux_classes import *
from aux_exceptions import *

class MyInterpreter(Interpreter):

    #region Init

    def __init__(self):
        super().__init__()

        # Variaveis auxiliares
        self.palavrasReservadas = set()
        self.tipos = set()
        self.funcoes = {}
        self.scopes = []

        # Definir as palavras reservadas
        self.palavrasReservadas.add("True")
        self.palavrasReservadas.add("False")

        # Definir os tipos atomicos
        self.tipos.add(RegistoTipo("void",  0)) # Utilizado para funcoes que nao tem return
        self.tipos.add(RegistoTipo("empty", 0)) # Utilizado para estruturas vazias
        self.tipos.add(RegistoTipo("int",   0))
        self.tipos.add(RegistoTipo("float", 0))
        self.tipos.add(RegistoTipo("bool",  0))

        # Definir os tipos complexos
        self.tipos.add(RegistoTipo("List",  1))
        self.tipos.add(RegistoTipo("Set",  1))
        self.tipos.add(RegistoTipo("Map",  2))

        # Definir as atribuicoes validas
        self.atribuicoesValidas = { # { tipoVar : tipoVal }
            # Tipos atomicos
            RegistoTipo("void",  0) : set(),
            RegistoTipo("empty", 0) : set(),
            RegistoTipo("int",   0) : set(),
            RegistoTipo("float", 0) : { RegistoTipo("int", 0) },
            RegistoTipo("bool",  0) : set(),
            # Tipos complexos
            RegistoTipo("List", 1) : set(),
            RegistoTipo("Set",  1) : set(),
            RegistoTipo("Map",  2) : set()
        }

        # Definir os casts validos
        self.castsValidos = { # { tipoCast : tipoExp }
            # Tipos atomicos
            RegistoTipo("void",  0) : set(),
            RegistoTipo("empty", 0) : set(),
            RegistoTipo("int",   0) : { RegistoTipo("float", 0), RegistoTipo("bool", 0) },
            RegistoTipo("float", 0) : { RegistoTipo("int", 0), RegistoTipo("bool", 0) },
            RegistoTipo("bool",  0) : set(),
            # Tipos complexos
            RegistoTipo("List", 1) : { RegistoTipo("Set",  1) },
            RegistoTipo("Set",  1) : set(),
            RegistoTipo("Map",  2) : set()
        }

        # Permitir a atribuicao de tipos para "empty"
        for tipoOut, tiposIn in self.atribuicoesValidas.items():
            if tipoOut.nome != "empty":
                tiposIn.add(RegistoTipo("empty", 0))

        # Permitir o cast de tipos para "empty"
        for tipoOut, tiposIn in self.castsValidos.items():
            if tipoOut.nome != "empty":
                tiposIn.add(RegistoTipo("empty", 0))

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
        if not self.validarConversaoAux(tipoVal, tipoVar, self.atribuicoesValidas):
            raise TipoVariavelException(nomeVar, tipoVar, tipoVal)

    def validarCast(self, tipoCast, tipoExp):
        if not self.validarConversaoAux(tipoExp, tipoCast, self.castsValidos):
            raise TipoCastException(tipoCast, tipoExp)

    def validarConversaoAux(self, tipoIn, tipoOut, tabelaConversao):
        # Converter os tipos
        _tipoIn = RegistoTipo(tipoIn.nome, len(tipoIn.subtipos))
        _tipoOut = RegistoTipo(tipoOut.nome, len(tipoOut.subtipos))
        # Se os tipos principais + numero de subtipos nao forem compativeis
        if _tipoIn != _tipoOut and _tipoIn not in tabelaConversao[_tipoOut]:
            return False
        # Se os subtipos nao forem compativeis
        for subtipoVar, subtipoVal in zip(tipoIn.subtipos, tipoOut.subtipos):
            if not self.validarConversaoAux(subtipoVar, subtipoVal, tabelaConversao):
                return False
        # Atribuicao e valida
        return True

    def isTipoNumero(self, tipo):
        return tipo in {Tipo("int", []), Tipo("float", [])}

    def getMembrosExprBin(self, tree):
        tipoEsq = self.visit(tree.children[0])
        tipoDir = self.visit(tree.children[2])
        operador = tree.children[1].value
        return tipoEsq, tipoDir, operador

    def determinarSubtipoVal(self, elementos):
        subtipos = set()
        # Determinar todos os tipos
        for elem in elementos:
            subtipos.add(self.visit(elem))
        # Determinar o tipo comum
        if len(subtipos) > 1:
            self.determinarSubtipoComum(subtipos)
        # Retornar o tipo
        return subtipos.pop()

    def determinarSubtipoComum(self, tipos):
        while len(tipos) > 1:
            it = iter(tipos)
            tipo1 = next(it)
            tipo2 = next(it)
            # Se o tipo1 poder ser convertido no tipo2
            if self.validarConversaoAux(tipo1, tipo2, self.atribuicoesValidas):
                tipos.remove(tipo1)
            # Se o tipo2 poder ser convertido no tipo1
            elif self.validarConversaoAux(tipo2, tipo1, self.atribuicoesValidas):
                tipos.remove(tipo2)
            # Se nao houver conversao
            else:
                raise TipoEstruturaException()

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
        args = self.visit(tree.children[2])
        # Definir a funcao
        self.definirFuncao(Funcao(nome, tipo_return, args))
        # Criar um scope para os args e adiciona-los
        self.scopes.append(dict())
        for tipo, nome in args:
            self.definirVariavel(Variavel(nome, tipo, True))
        # Validar o corpo
        self.visit(tree.children[3])
        # Apagar o scope
        self.scopes.pop(len(self.scopes) - 1)

    def funcao_args(self, tree):
        args = []
        for idx in range(0, len(tree.children), 2):
            tipo = self.visit(tree.children[idx])
            nome = tree.children[idx + 1].value
            args.append((tipo, nome))
        return args
   
    def funcao_call(self, tree):
        nome = tree.children[0].value
        args_tipo = self.visit(tree.children[1])
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
            if not self.isTipoNumero(var.tipo):
                raise TipoAtribuicaoBinariaException(nome)

        # Inicializar a variavel
        if not var.inicializada:
            var.inicializada = True
    
    def atrib_aux(self, tree):
        return self.visit(tree.children[0])

    def atrib_simples(self, tree):
        tipoExpr = self.visit(tree.children[0])
        return tipoExpr
    
    def atrib_bin(self, tree):
        tipoExpr = self.visit(tree.children[1])
        return tipoExpr

    def atrib_un(self, tree):
        return Tipo("int", [])

    #endregion

    #region Condicionais

    def cond(self, tree):
        for element in tree.children:
            self.visit(element)

    def cond_if(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do If
        if tipo != Tipo("bool", []):
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
        if tipo != Tipo("bool", []):
            raise CondicaoWhileException()
        self.visit(tree.children[1])

    def ciclo_do_while(self, tree):
        tipo = self.visit(tree.children[0])
        # Validar a condicao do While
        if tipo != Tipo("bool", []):
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
        if tipo != Tipo("bool", []):
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
            if tipoEsq != Tipo("bool", []) or tipoDir != Tipo("bool", []):
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return Tipo("bool", [])
    
    def expr_and(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq != Tipo("bool", []) or tipoDir != Tipo("bool", []):
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return Tipo("bool", [])
    
    def expr_eq(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if tipoEsq == Tipo("void", []) or tipoDir[0] == Tipo("void", []):
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return Tipo("bool", [])
    
    def expr_ord(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not self.isTipoNumero(tipoEsq) or not self.isTipoNumero(tipoDir):
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            return Tipo("bool", [])
    
    def expr_add(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not self.isTipoNumero(tipoEsq) or not self.isTipoNumero(tipoDir):
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            tipo = Tipo("float", []) if Tipo("float", []) in {tipoEsq, tipoDir} else Tipo("int", [])
            return tipo
    
    def expr_mul(self, tree):
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        else:
            tipoEsq, tipoDir, operador = self.getMembrosExprBin(tree)
            # Validar tipos
            if not self.isTipoNumero(tipoEsq) or not self.isTipoNumero(tipoDir):
                raise TipoOperadorBinException(operador, tipoEsq, tipoDir)
            tipo = Tipo("float", []) if Tipo("float", []) in {tipoEsq, tipoDir} else Tipo("int", [])
            return tipo

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
                self.validarCast(tipoCast, tipoExp)
                return tipoCast

            # Se for "+" ou "-"
            elif operador.value in {"+", "-"}:
                # Verificar se do operador e valido
                if not self.isTipoNumero(tipoExp):
                    raise TipoOperadorUnException(operador.value, tipoExp)
                return tipoExp
            # Se for "!" converter para int
            elif operador.value == "!":
                # Verificar se do operador e valido
                if tipoExp != Tipo("bool", []):
                    raise TipoOperadorUnException(operador.value, tipoExp)
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
            num_subtipos = len(subtipos)
        else:
            subtipos = []
            num_subtipos = 0
        # Validar o tipo
        if RegistoTipo(nome, num_subtipos) not in self.tipos:
            raise TipoInvalidoException(nome, num_subtipos)
        return Tipo(nome, subtipos)

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
            return Tipo(element.children[0].type.lower(), [])

        # Se for um bool
        elif isinstance(element, Token) and element.type == "BOOL":
            return Tipo("bool", [])

        # Se for uma variavel
        elif isinstance(element, Token) and element.type == "VAR_NOME":
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

        # Se for uma function call
        elif isinstance(element, Tree) and element.data == "funcao_call":
            tipo = self.visit(element)
            return tipo

        # Se for um tipo complexo
        else:
            element = element.children[0]

            # Se estiver vazio
            if len(element.children) == 0:
                if element.data == "map":
                    subtipos = [ Tipo("empty", []), Tipo("empty", []) ]
                else:
                    subtipos = [ Tipo("empty", []) ]
            # Se nao estiver vazio
            else:
                if element.data == "map":
                    subtipo1 = self.determinarSubtipoVal(element.children[0::2])
                    subtipo2 = self.determinarSubtipoVal(element.children[1::2])
                    subtipos = [ subtipo1, subtipo2 ]
                else:
                    subtipos = [ self.determinarSubtipoVal(element.children) ]
            # Retornar
            nome_tipo = element.data.capitalize()
            return Tipo(nome_tipo, subtipos)

    #endregion