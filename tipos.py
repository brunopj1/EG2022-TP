class Tipo:
    def __init__(self, nome, num_subtipos, subtipos):
        # Inicializar
        self._nome = nome
        self._num_subtipos = num_subtipos
        if subtipos != None:
            self._setSubtipos(subtipos)
        else:
            subtipos = None

    def _setSubtipos(self, subtipos):
        if len(subtipos) != self._num_subtipos:
            # TODO fazer uma exception pra isto
            raise Exception("Subtipos Inválidos")
        self._subtipos = subtipos

    @staticmethod
    def fromNome(nome, subtipos = []):
        for subclass in Tipo.__subclasses__():
            tipo = subclass()
            if tipo._nome == nome:
                tipo._setSubtipos(subtipos)
                return tipo
        # Se nao encontrou
        # TODO mudar para a exception normal
        raise Exception("Tipo Inválido")

    def _validarSubtipos(self, tipoFinal, atribuicao : bool):
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
        super().__init__("void", 0, [])
    
    def atribuicaoValida(tipoFinal):
        return False
    
    def castValido(tipoFinal):
        return False

# Utilizado para listas vazias
class Tipo_Empty(Tipo):
    def __init__(self):
        super().__init__("empty", 0, [])
            
    def atribuicaoValida(self, tipoFinal):
        return True
    
    def castValido(self, tipoFinal):
        return True

class Tipo_Int(Tipo):
    def __init__(self):
        super().__init__("int", 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal._nome in {self._nome, "float"}
    
    def castValido(self,tipoFinal):
        return tipoFinal._nome in {self._nome, "float"}

class Tipo_Float(Tipo):
    def __init__(self):
        super().__init__("float", 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal._nome in {self._nome}
    
    def castValido(self,tipoFinal):
        return tipoFinal._nome in {self._nome, "int"}

class Tipo_Bool(Tipo):
    def __init__(self):
        super().__init__("bool", 0, [])

    def atribuicaoValida(self, tipoFinal):
        return tipoFinal._nome in {self._nome}
    
    def castValido(self,tipoFinal):
        return tipoFinal._nome in {self._nome}

class Tipo_List(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("List", 1, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal._nome in {self._nome}:
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self,tipoFinal):
        if tipoFinal._nome in {self._nome}:
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False

class Tipo_Set(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("Set", 1, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal._nome in {self._nome}:
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self,tipoFinal):
        if tipoFinal._nome in {self._nome, "List"}:
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False

class Tipo_Map(Tipo):
    def __init__(self, subtipos = None):
        super().__init__("Map", 2, subtipos)

    def atribuicaoValida(self, tipoFinal):
        if tipoFinal._nome in {self._nome}:
            return self._validarSubtipos(tipoFinal, True)
        else:
            return False
    
    def castValido(self,tipoFinal):
        if tipoFinal._nome in {self._nome}:
            return self._validarSubtipos(tipoFinal, False)
        else:
            return False