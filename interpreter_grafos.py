from lark import Tree, Token
from lark.visitors import Interpreter

from aux_classes import *

class InterpreterGrafos(Interpreter):
    
    def __init__(self, funcoes):
        self.funcoes = funcoes
        self.funcaoIdx = 0
        self.funcaoAtual = None

    #region Start / Funcoes

    def start(self, tree):
        for elem in tree.children[0].children:
            self.visit(elem)

    def funcao(self, tree):
        # Obter a funcao
        self.funcaoAtual = self.funcoes[self.funcaoIdx]
        self.funcaoIdx += 1
        # Adicionar o nodo inicial
        self.funcaoAtual.controlFlowGraph.node('start', 'start', shape="invhouse", color="green")
        # Adicionar os nodos do corpo
        self.visit(tree.children[6])
        # TODO Ligar o nodo inicial ao corpo
        # Atualizar a funcao atual
        self.funcaoAtual = None

    #endregion

    #region Declaracoes / Atribuicoes

    def decl(self, tree):
        pass

    def decl_atrib(self, tree):
        pass

    def atrib(self, tree):
        pass

    #endregion

    #region Condicionais + Ciclos
    
    def cond(self, tree):
        pass

    def ciclo_while(self, tree):
        pass

    def ciclo_for(self, tree):
        pass

    def ciclo_foreach(self, tree):
        pass

    def funcao_call(self, tree):
        pass

    def ciclo_do_while(self, tree):
        pass

    #endregion
