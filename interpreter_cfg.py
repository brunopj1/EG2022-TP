from lark import Tree, Token
from lark.visitors import Interpreter

from aux_classes import *

# Cores:
# green -> start
# red   -> stop
# blue  -> corpo vazio

class InterpreterCFG(Interpreter):
    
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
        self.funcaoAtual.cfg.node(id, desc, shape=shape, color=color)
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
                self.funcaoAtual.cfg.edge(elemFrom.id, elemTo.id, constraint="true", label=_label)

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
        corpo_first, corpo_last = self.visit(tree.children[6])
        # Ligar o nodo inicial ao corpo
        self.adicionarAresta(start, corpo_first)
        # Adicionar o nodo final
        stop = self.adicionarNodo("stop", shape="house", color="red")
        # Ligar o corpo ao nodo final
        self.adicionarAresta(corpo_last, stop)
        # Atualizar a funcao atual
        self.funcaoAtual = None

    def corpo(self, tree):
        corpo_first = None
        corpo_last = None
        # Visitar o corpo
        for elem in tree.children:
            # Visitar a instrucao
            inst_first, inst_last = self.visit(elem.children[0])
            # Guardar o primeiro
            if corpo_first is None:
                corpo_first = inst_first
            # Adicionar a ligação
            if corpo_last is not None:
                self.adicionarAresta(corpo_last, inst_first)
            # Atualizar o ultimo nodo
            corpo_last = inst_last
        # Se o corpo for vazio
        if len(tree.children) == 0:
            corpo_first = self.adicionarNodo("{ }", color="blue")
            corpo_last = [ corpo_first ]
        # Retornar os nodos
        return corpo_first, corpo_last

    #endregion

    #region Declaracoes / Atribuicoes / Funcao Call

    def decl(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo, [ nodo ]

    def decl_atrib(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo, [ nodo ]

    def atrib(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo, [ nodo ]

    def funcao_call(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo, [ nodo ]

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
                # Obter a condicao
                if elem.data == "cond_if":
                    texto = self.obterTexto(elem.children[0])
                else:
                    texto = texto = self.obterTexto(elem.children[0].children[0])
                if_atual = self.adicionarNodo("if (" + texto + ")", shape="diamond")
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
            ultimos_nodos.extend(corpo_last)
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

    # TODO verificar se é possivel especificar a posicao vertical dos nodos
    def ciclo_while(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("while (" + texto + ")", shape="diamond")
        # Criar os nodos do corpo
        corpo_first, corpo_last = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo_first, label="True")
        # Ligar os nodos finais a condicao
        self.adicionarAresta(corpo_last, condicao)
        # Retornar o nodo da condição
        condicao.out_label = "False"
        return condicao, condicao

    def ciclo_do_while(self, tree):
        # Criar os nodos do corpo
        corpo_first, corpo_last = self.visit(tree.children[0])
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("while (" + texto + ")", shape="diamond")
        # Ligar o corpo à condição
        self.adicionarAresta(corpo_last, condicao)
        # Ligar a condicao ao corpo
        self.adicionarAresta(condicao, corpo_first, label="True")
        # Retornar o nodo da condição
        condicao.out_label = "False"
        return corpo_first, condicao

    def ciclo_for(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("for (" + texto + ")", shape="diamond")
        # Criar os nodos do corpo
        corpo_first, corpo_last = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo_first, label="True")
        # Ligar os nodos finais a condicao
        self.adicionarAresta(corpo_last, condicao)
        # Retornar o nodo da condição
        condicao.out_label = "False"
        return condicao, condicao

    def ciclo_foreach(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("foreach (" + texto + ")", shape="diamond")
        # Criar os nodos do corpo
        corpo_first, corpo_last = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo_first, label="Has Element")
        # Ligar os nodos finais a condicao
        self.adicionarAresta(corpo_last, condicao)
        # Retornar o nodo da condição
        condicao.out_label = "Is Empty"
        return condicao, condicao

    #endregion
