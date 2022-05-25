from lark import Tree, Token
from lark.visitors import Interpreter

from aux_classes import *

# Cores:
# green -> start
# red   -> condicionais
# blue  -> ciclos

class InterpreterSDG(Interpreter):
    
    def __init__(self, codigo, funcoes):
        self.codigo = codigo.split("\n")
        self.funcoes = funcoes
        self.funcaoAtual = None
        self.funcaoIdx = 0
        self.instrucaoIdx = 0

    #region Metodos do Interpreter

    def adicionarNodo(self, desc, color=None, shape=None):
        # Determinar o id
        id = "i" + str(self.instrucaoIdx)
        # Atualizar o numero de nodos
        self.instrucaoIdx += 1
        # Inserir o nodo
        self.funcaoAtual.sdg.node(id, desc, shape=shape, color=color)
        # Retornar o nodos
        return NodoGrafo(id, desc, color, shape)

    def adicionarAresta(self, nodosFrom, nodosTo, label=None):
        if not isinstance(nodosFrom, list):
            nodosFrom = [ nodosFrom ]
        if not isinstance(nodosTo, list):
            nodosTo = [ nodosTo ]
        # Inserir os nodos
        for elemFrom in nodosFrom:
            for elemTo in nodosTo:
                _label = elemFrom.out_label if elemFrom.out_label is not None else label
                self.funcaoAtual.sdg.edge(elemFrom.id, elemTo.id, constraint="true", label=_label)

    def obterTexto(self, elem_from, elem_to=None):
        if elem_to is None:
            elem_to = elem_from

        linha = elem_from.line - 1
        coluna0 = elem_from.column - 1
        coluna1 = elem_to.end_column - 1

        return self.codigo[linha][coluna0:coluna1]

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
        self.instrucaoIdx = 0
        # Adicionar o nodo inicial
        start = self.adicionarNodo("start", shape="invhouse", color="green")
        # Adicionar os nodos do corpo
        corpo = self.visit(tree.children[6])
        # Ligar o nodo inicial ao corpo
        self.adicionarAresta(start, corpo)
        # Atualizar a funcao atual
        self.funcaoAtual = None

    def corpo(self, tree):
        corpo = []
        # Visitar o corpo
        for elem in tree.children:
            # Visitar a instrucao
            inst = self.visit(elem.children[0])
            corpo.append(inst)
        # Retornar os nodos
        return corpo

    #endregion

    #region Declaracoes / Atribuicoes / Funcao Call

    def decl(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo

    def decl_atrib(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo

    def atrib(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo

    def funcao_call(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo

    #endregion

    #region Condicionais

    def cond(self, tree):
        if_first = None
        if_last = None
        # Visitar as opções do if
        for elem in tree.children:
            # Adicionar o nodo do if
            if elem.data != "cond_else":
                # Obter a condicao
                if elem.data == "cond_if":
                    texto = self.obterTexto(elem.children[0])
                    texto = "if (" + texto + ")"
                else:
                    texto = texto = self.obterTexto(elem.children[0].children[0])
                    texto = "else if (" + texto + ")"
                nodo_atual = self.adicionarNodo(texto, color="red")
                # Guardar o primeiro if
                if if_first is None:
                    if_first = nodo_atual
                # Ligar os ifs
                else:
                    self.adicionarAresta(if_last, nodo_atual)
                # Guardar o ultimo if
                if_last = nodo_atual
                # Inserir o nodo "then"
                nodo_atual = self.adicionarNodo("then", color="red")
                self.adicionarAresta(if_last, nodo_atual)
            # Registar que existe else
            else:
                nodo_atual = self.adicionarNodo("else", color="red")
                self.adicionarAresta(if_last, nodo_atual)
            # Adicionar os nodos do corpo
            corpo = self.visit(elem)
            self.adicionarAresta(nodo_atual, corpo)
        # Retornar o nodo do primeiro if
        return if_first

    def cond_if(self, tree):
        return self.visit(tree.children[1])

    def cond_else_if(self, tree):
        return self.visit(tree.children[0])

    def cond_else(self, tree):
        return self.visit(tree.children[0])

    #endregion

    #region Ciclos

    def ciclo_while(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("while (" + texto + ")", color="blue")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo)
        # Retornar o nodo da condição
        return condicao

    def ciclo_do_while(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("do while (" + texto + ")", color="blue")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[0])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo)
        # Retornar o nodo da condição
        return condicao

    def ciclo_for(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("for (" + texto + ")", color="blue")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo)
        # Retornar o nodo da condição
        return condicao

    def ciclo_foreach(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("foreach (" + texto + ")", color="blue")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo)
        # Retornar o nodo da condição
        return condicao

    #endregion
