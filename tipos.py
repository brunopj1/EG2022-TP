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
        # Verificar que os subtipos ainda nao foram atribuidos
        if self._subtipos != None:
            raise Exception()
        # Se o tipo tiver um numero de subtipos fixo
        if not self._num_subtipos_variavel and len(subtipos) != self._num_subtipos:
            # TODO fazer uma exception pra isto
            raise Exception("Subtipos Inválidos")
        # Se o tipo tiver um numero de subtipos variavel
        if self._num_subtipos_variavel:
            if len(subtipos) < self._num_subtipos:
                # TODO fazer uma exception pra isto
                raise Exception("Subtipos Inválidos")
            self._num_subtipos = len(subtipos)
        # Guardar subtipos
        self._subtipos = subtipos

    def isAnyOf(self, tipos):
        for tipo in tipos:
            if isinstance(self, tipo):
                return True
        return False

    @staticmethod
    def fromNome(nome, subtipos):
        for subclass in Tipo.__subclasses__():
            tipo = subclass()
            if tipo._nome == nome:
                if subtipos != []:
                    tipo._setSubtipos(subtipos)
                return tipo
        # Se nao encontrou
        # TODO mudar para a exception normal
        raise Exception("Tipo Inválido")

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
            return f"{self._nome}<{subtipos}>"
        else:
            return f"{self._nome}<{self._num_subtipos}>"

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
    
    def atribuicaoValida(tipoFinal):
        return False
    
    def castValido(tipoFinal):
        return False

# Utilizado para listas vazias
class Tipo_Empty(Tipo):
    def __init__(self):
        super().__init__("empty", False, 0, [])
            
    def atribuicaoValida(self, tipoFinal):
        return True
    
    def castValido(self, tipoFinal):
        return True

class Tipo_Int(Tipo):
    def __init__(self):
        super().__init__("int", False, 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Int, Tipo_Float })
    
    def castValido(self,tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Int, Tipo_Float })

class Tipo_Float(Tipo):
    def __init__(self):
        super().__init__("float", False, 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Float })
    
    def castValido(self,tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Int, Tipo_Float })

class Tipo_Bool(Tipo):
    def __init__(self):
        super().__init__("bool", False, 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Bool })
    
    def castValido(self,tipoFinal):
        return tipoFinal.isAnyOf({ Tipo_Bool })

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

class Tipo_Map(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("Map", False, 2, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Map }):
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self,tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Map }):
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False

class Tipo_Tuple(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("Tuple", True, 2, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Tuple }):
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self,tipoFinal):
        if tipoFinal.isAnyOf({ Tipo_Tuple }):
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False