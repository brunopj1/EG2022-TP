class Variavel:
    def __init__(self, nome, tipo, inicializada):
        self.nome = nome
        self.tipo = tipo
        self.inicializada = inicializada

class Funcao:
    def __init__(self, nome, args_tipo, args_nome, tipo_ret):
        self.nome = nome
        self.args_tipo = args_tipo
        self.args_nome = args_nome
        self.tipo_ret = tipo_ret