from lark import Tree, Token
from lark.visitors import Interpreter
from numpy import isin

from aux_classes import *

class InterpreterGrafos(Interpreter):
    
    def __init__(self, funcoes):
        self.funcoes = funcoes
        self.funcaoIdx = 0
        self.funcaoAtual = None

    #region Metodos do Interpreter

    def adicionarNodo(self, desc, color=None, shape=None):
        # Determinar o id
        id = "i" + str(self.funcaoAtual.numInstrucoes)
        # Atualizar o numero de nodos
        self.funcaoAtual.numInstrucoes += 1
        # Inserir o nodo
        self.funcaoAtual.controlFlowGraph.node(id, desc, shape=shape, color=color)
        # Retornar o nodos
        return NodoGrafo(id, desc, color, shape)

    def adicionarAresta(self, nodoFrom, nodoTo, label=None):
        if not isinstance(nodoFrom, list):
            nodoFrom = [ nodoFrom ]
        # Inserir os nodos
        for elem in nodoFrom:
            _label = elem.out_label if elem.out_label is not None else label
            self.funcaoAtual.controlFlowGraph.edge(elem.id, nodoTo.id, constraint='true', label=_label)

    #endregion

    #region Start / Funcoes

    def start(self, tree):
        for elem in tree.children[0].children:
            if elem.data == "funcao":
                self.visit(elem)

    def funcao(self, tree):
        # Obter a funcao
        self.funcaoAtual = self.funcoes[self.funcaoIdx]
        self.funcaoIdx += 1
        # Adicionar o nodo inicial
        start = self.adicionarNodo("start", shape="invhouse", color="green")
        # Adicionar os nodos do corpo
        corpo_first, corpo_last = self.visit(tree.children[6])
        # Ligar o nodo inicial ao corpo
        self.adicionarAresta(start, corpo_first)
        # Atualizar a funcao atual
        self.funcaoAtual = None

    def corpo(self, tree):
        corpo_first = None
        corpo_last = None
        # Visitar o corpo
        for elem in tree.children:
            # Visitar a instrucao
            first, last = self.visit(elem.children[0])
            # Guardar o primeiro
            if corpo_first is None:
                corpo_first = first
            # Adicionar a ligação
            if corpo_last is not None:
                self.adicionarAresta(corpo_last, first)
            # Atualizar o ultimo nodo
            corpo_last = last
        # Se o corpo for vazio
        if len(tree.children) == 0:
            corpo_first = corpo_last = self.adicionarNodo("")
        # Retornar os nodos
        return corpo_first, corpo_last

    #endregion

    #region Declaracoes / Atribuicoes / Funcao Call

    def decl(self, tree):
        nodo = self.adicionarNodo(tree.data)
        return nodo, nodo

    def decl_atrib(self, tree):
        nodo = self.adicionarNodo(tree.data)
        return nodo, nodo

    def atrib(self, tree):
        nodo = self.adicionarNodo(tree.data)
        return nodo, nodo

    def funcao_call(self, tree):
        nodo = self.adicionarNodo(tree.data)
        return nodo, nodo

    #endregion

    #region Condicionais
    
    def cond(self, tree):
        if_first = None
        if_last = None
        tem_else = False
        ultimos_nodos = []
        # Visitar as opções do if
        for elem in tree.children:
            # Adicionar o nodo do if
            if elem.data != "cond_else":
                if_atual = self.adicionarNodo(elem.data, shape="diamond")
                # Guardar o primeiro if
                if if_first is None:
                    if_first = if_atual
                # Ligar os ifs
                else:
                    self.adicionarAresta(if_last, if_atual, label="False")
                # Guardar o ultimo if
                if_last = if_atual
            # Registar que existe else
            else:
                tem_else = True
            # Adicionar os nodos do corpo
            corpo_first, corpo_last = self.visit(elem)
            label = "False" if tem_else else "True"
            self.adicionarAresta(if_last, corpo_first, label=label)
            ultimos_nodos.append(corpo_last)
        # Se nao tiver enviar o ultimo if como ultimo nodo
        if not tem_else:
            if_last.out_label = "False"
            ultimos_nodos.append(if_last)
        return if_first, ultimos_nodos

    def cond_if(self, tree):
        return self.visit(tree.children[1])

    def cond_else_if(self, tree):
        return self.visit(tree.children[0])

    def cond_else(self, tree):
        return self.visit(tree.children[0])

    #endregion

    #region Ciclos

    def ciclo_while(self, tree):
        # TODO ciclos
        pass

    def ciclo_for(self, tree):
        # TODO ciclos
        pass

    def ciclo_foreach(self, tree):
        # TODO ciclos
        pass

    def ciclo_do_while(self, tree):
        # TODO ciclos
        pass

    #endregion
