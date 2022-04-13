class RegistoTipo:
    def __init__(self, nome, num_subtipos):
        self.nome = nome
        self.num_subtipos = num_subtipos

    #region Funçoes internas

    def __repr__(self):
        if self.num_subtipos == 0:
            return self.nome
        else: 
            return f"{self.nome}<{self.num_subtipos}>"

    def __eq__(self, other):
        if isinstance(other, RegistoTipo):
            return self.nome == other.nome and self.num_subtipos == other.num_subtipos
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    #endregion

class Tipo:
    def __init__(self, nome, subtipos):
        self.nome = nome
        self.subtipos = subtipos

    #region Funçoes internas

    def __repr__(self):
        if len(self.subtipos) == 0:
            return self.nome
        else: 
            subtipos = [s.__repr__() for s in self.subtipos]
            subtipos = ", ".join(subtipos)
            return f"{self.nome}<{subtipos}>"

    def __eq__(self, other):
        if isinstance(other, Tipo):
            return self.nome == other.nome and self.subtipos == other.subtipos
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    #endregion

class Variavel:
    def __init__(self, nome, tipo, inicializada):
        self.nome = nome
        self.tipo = tipo
        self.inicializada = inicializada

class Funcao:
    def __init__(self, nome, tipo_ret, args):
        self.nome = nome
        self.tipo_ret = tipo_ret
        self.args_tipo = []
        self.args_nome = []
        for tipo, nome in args:
            self.args_tipo.append(tipo)
            self.args_nome.append(nome)