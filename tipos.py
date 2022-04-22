from language_notes import *

class Tipo:
    def __init__(self, nome, num_subtipos_variavel, num_subtipos, subtipos):
        # Inicializar
        self._nome = nome
        self._num_subtipos_variavel = num_subtipos_variavel
        self._num_subtipos = num_subtipos
        # Caso o numero de subtipos seja variavel, a variavel _num_subtipos
        # é inicializada com o numero minimo de subtipos valido
        self._subtipos = None
        if subtipos != None:
            self._setSubtipos(subtipos)

    def _setSubtipos(self, subtipos):
        erro = None
        # Verificar que os subtipos ainda nao foram atribuidos
        if self._subtipos != None:
            raise Exception()
        # Atualizar os subtipos
        self._subtipos = subtipos
        # Se o tipo tiver um numero de subtipos fixo
        if not self._num_subtipos_variavel and len(subtipos) != self._num_subtipos:
            erro = TipoInvalido(self)
            self._subtipos = [Tipo_Anything()] * self._num_subtipos
        # Se o tipo tiver um numero de subtipos variavel
        elif self._num_subtipos_variavel:
            if len(subtipos) < self._num_subtipos:
                erro = TipoInvalido(self)
                self._subtipos = [Tipo_Anything()] * self._num_subtipos
            self._num_subtipos = len(subtipos)
        return erro

    def isAnyOf(self, tipos):
        for tipo in tipos:
            if isinstance(self, tipo):
                return True
        return False

    @staticmethod
    def fromNome(nome, subtipos):
        erro = None
        for subclass in Tipo.__subclasses__():
            tipo = subclass()
            if tipo._nome == nome:
                if tipo._subtipos is None:
                    erro = tipo._setSubtipos(subtipos)
                return tipo, erro
        # Se nao encontrou
        tipo_invalido = Tipo(nome, False, len(subtipos), subtipos)
        erro = TipoInvalido(tipo_invalido)
        tipo = Tipo_Anything()
        return tipo, erro

    def _validarSubtipos(self, tipoFinal, atribuicao : bool):
        # Validar o numero de subtipos
        if self._num_subtipos != tipoFinal._num_subtipos:
            return False
        # Validar os subtipos
        for subtipo, subtipoFinal in zip(self._subtipos, tipoFinal._subtipos):
            if atribuicao:
                if not subtipo.atribuicaoValida(subtipoFinal):
                    return False
            else:
                if not subtipo.castValido(subtipoFinal):
                    return False
        return True

    #region Metodos internos

    def __repr__(self):
        if self._num_subtipos == 0:
            return self._nome
        elif self._subtipos != None:
            subtipos = [s.__repr__() for s in self._subtipos]
            subtipos = ", ".join(subtipos)
            return f"{self._nome}&lt;{subtipos}&gt;"
        else:
            return f"{self._nome}&lt;{self._num_subtipos}&gt;"

    def __eq__(self, other):
        if isinstance(other, Tipo):
            return self._nome == other._nome and self._num_subtipos == other._num_subtipos
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    #endregion

# Utilizado para funcoes sem return
class Tipo_Void(Tipo):
    def __init__(self):
        super().__init__("void", False, 0, [])
    
    def atribuicaoValida(self, tipoFinal):
        return False
    
    def castValido(self, tipoFinal):
        return False

    def validarAcesso(self, tipoExpr):
        erro = AcessoTipo(self)
        tipo = Tipo_Anything()
        return tipo, erro

# Utilizado para listas vazias e erros
class Tipo_Anything(Tipo):
    def __init__(self):
        super().__init__("anything", False, 0, [])
            
    def atribuicaoValida(self, tipoFinal):
        return True
    
    def castValido(self, tipoFinal):
        return True
        
    def validarAcesso(self, tipoExpr):
        erro = AcessoTipo(self)
        tipo = Tipo_Anything()
        return tipo, erro

class Tipo_Int(Tipo):
    def __init__(self):
        super().__init__("int", False, 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Int, Tipo_Float })
    
    def castValido(self, tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Int, Tipo_Float })
        
    def validarAcesso(self, tipoExpr):
        erro = AcessoTipo(self)
        tipo = Tipo_Anything()
        return tipo, erro

class Tipo_Float(Tipo):
    def __init__(self):
        super().__init__("float", False, 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Float })
    
    def castValido(self,tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Int, Tipo_Float })
        
    def validarAcesso(self, tipoExpr):
        erro = AcessoTipo(self)
        tipo = Tipo_Anything()
        return tipo, erro

class Tipo_Bool(Tipo):
    def __init__(self):
        super().__init__("bool", False, 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Bool })
    
    def castValido(self,tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Bool })
        
    def validarAcesso(self, tipoExpr):
        erro = AcessoTipo(self)
        tipo = Tipo_Anything()
        return tipo, erro

class Tipo_List(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("List", False, 1, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_List }):
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self,tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_List }):
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False
            
    def validarAcesso(self, tipoExpr):
        # Validar o tipo da expressao
        erro = None
        if not isinstance(tipoExpr, Tipo_Int):
            erro = AcessoTipoKey(self, tipoExpr, Tipo_Int())
        # Obter o tipo do resultado
        tipo, _ = Tipo.fromNome(self._subtipos[0]._nome, self._subtipos[0]._subtipos)
        return tipo, erro

class Tipo_Set(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("Set", False, 1, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Set }):
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self,tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Set, Tipo_List }):
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False
            
    def validarAcesso(self, tipoExpr):
        erro = AcessoTipo(self)
        tipo = Tipo_Anything()
        return tipo, erro

class Tipo_Map(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("Map", False, 2, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Map }):
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Map }):
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False
            
    def validarAcesso(self, tipoExpr):
        # Validar o tipo da expressao
        erro = None
        if type(tipoExpr) is not type(self._subtipos[0]):
            erro = AcessoTipoKey(self, tipoExpr, self._subtipos[0])
        # Obter o tipo do resultado
        tipo, _ = Tipo.fromNome(self._subtipos[1]._nome, self._subtipos[1]._subtipos)
        return tipo, erro

class Tipo_Tuple(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("Tuple", True, 2, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Tuple }):
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Tuple }):
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False
            
    def validarAcesso(self, tipoExpr):
        # Validar o tipo da expressao
        erro = None
        if not isinstance(tipoExpr, Tipo_Int):
            erro = AcessoTipoKey(self, tipoExpr, Tipo_Int())
        # Obter o tipo do resultado (Tipo_Anything)
        tipo = Tipo_Anything()
        return tipo, erro