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