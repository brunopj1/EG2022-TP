from re import S


class Variavel:
    def __init__(self, nome, tipo, scopeCriacao, inicializada):
        self.nome = nome
        self.tipo = tipo

        self._scopeCriacao = scopeCriacao.copy()
        self._scopeInicializacao = scopeCriacao.copy() if inicializada else None

        self.num_reads = 0
        self.num_writes = 0

    #region Metodos Auxiliares

    def inicializar(self, scope):
        # Se nao estiver inicializada
        if self._scopeInicializacao is None:
            self._scopeInicializacao = scope.copy()
            return
        # Se o scope for interno ao de inicializacao
        size = len(scope)
        sizeI = len(self._scopeInicializacao)
        if size >= sizeI and scope[0:sizeI] == self._scopeInicializacao:
            return
        # Se o scope for externo ao de inicializacao
        if size < sizeI and scope == self._scopeInicializacao[0:size]:
            self._scopeInicializacao = scope.copy()
            return
        # Se o scope for posterior ao de inicializacao
        size = min(len(scope), len(self._scopeInicializacao))
        for i in range(size):
            if scope[i] > self._scopeInicializacao[i]:
                self._scopeInicializacao = scope.copy()
                return

    def isInicializada(self, scope):
        # Verificar se foi inicializado alguma vez
        if self._scopeInicializacao is None:
            return False
        # Verificar se foi inicializada no scope de criacao
        if self._scopeInicializacao == self._scopeCriacao:
            return True
        # Verificar se o scope atual é igual ou interno ao de inicializacao
        size = len(scope)
        sizeI = len(self._scopeInicializacao)
        if size >= sizeI and scope[0:sizeI] == self._scopeInicializacao:
            return True
        # Caso contrario
        return False

    #endregion

class Funcao:
    def __init__(self, nome, tipo_ret, args):
        self.nome = nome
        self.tipo_ret = tipo_ret
        self.args_tipo = []
        self.args_nome = []
        for tipo, nome in args:
            self.args_tipo.append(tipo)
            self.args_nome.append(nome)