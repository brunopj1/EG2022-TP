from lark import Tree, Token
from lark.visitors import Interpreter

from aux_classes import *

# Cores:
# green         -> nodo start
# chocolate     -> nodos condicionais
# darkgoldenrod -> nodos ciclos
# darkviolet    -> variaveis globais
# deeppink      -> argumentos

class InterpreterSDG(Interpreter):
    
    def __init__(self, codigo, funcoes):
        self.codigo = codigo.split("\n")

        self.funcoes = funcoes
        self.variaveisGlobais = {} # nome -> texto
        self.variaveisFuncao = {} # nome -> nodo

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
        self.funcaoAtual.sdg.node(id, desc, color=color, shape=shape)
        # Retornar o nodos
        return NodoGrafo(id, desc, color, shape)

    def adicionarAresta(self, nodosFrom, nodosTo, constraint, color=None):
        if not isinstance(nodosFrom, list):
            nodosFrom = [ nodosFrom ]
        if not isinstance(nodosTo, list):
            nodosTo = [ nodosTo ]
        # Inserir os nodos
        for elemFrom in nodosFrom:
            for elemTo in nodosTo:
                self.funcaoAtual.sdg.edge(elemFrom.id, elemTo.id, color=color, constraint=str(constraint))

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
            # Visitar a funcao
            if elem.data == "funcao":
                self.visit(elem)
            # Registar a variavel global
            else:
                nomeVar = elem.children[1].value
                texto = self.obterTexto(elem)
                self.variaveisGlobais[nomeVar] = texto

    def funcao(self, tree):
        # Obter a funcao
        self.funcaoAtual = self.funcoes[self.funcaoIdx]
        self.funcaoIdx += 1
        self.instrucaoIdx = 0
        self.variaveisFuncao.clear()
        # Adicionar o nodo inicial
        start = self.adicionarNodo("start", shape="invhouse", color="green")
        # Adicionar os nodos das variaveis globais
        for nome, texto in self.variaveisGlobais.items():
            nodo = self.adicionarNodo("global\n" + texto, color = "darkviolet")
            self.variaveisFuncao[nome] = nodo
        # Adicionar os nodos dos argumentos
        argumentos = self.visit(tree.children[3])
        for nome, texto in argumentos.items():
            nodo = self.adicionarNodo("arg\n" + texto, color="deeppink")
            self.variaveisFuncao[nome] = nodo
        # Adicionar os nodos do corpo
        corpo = self.visit(tree.children[6])
        # Ligar o nodo inicial ao corpo
        self.adicionarAresta(start, corpo, constraint=True, color="blue")
        # Atualizar a funcao atual
        self.funcaoAtual = None

    def funcao_args(self, tree):
        variables = {}
        for tipo, nome in zip(tree.children[0::2], tree.children[1::2]):
            texto = self.obterTexto(tipo, nome)
            variables[nome] = texto
        return variables

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
        # Registar o nodo como a origem da variavel
        nomeVar = tree.children[1].value
        self.variaveisFuncao[nomeVar] = nodo
        # Retornar o nodo
        return nodo

    def decl_atrib(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        # Registar o nodo como a origem da variavel
        nomeVar = tree.children[1].value
        self.variaveisFuncao[nomeVar] = nodo
        # Ligar as variaveis usadas na expr ao nodo
        variaveis = self.visit(tree.children[2])
        for var in variaveis:
            nodoVar = self.variaveisFuncao[var]
            self.adicionarAresta(nodoVar, nodo, constraint=True, color="green")
        # Retornar o nodo
        return nodo

    def atrib(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        # Obter as variaveis usadas na expr
        elem = tree.children[1].children[0]
        if elem.data == "atrib_simples":
            variaveis = self.visit(elem.children[0])
        elif elem.data == "atrib_bin":
            variaveis = self.visit(elem.children[1])
        else: # elem.data == "atrib_bin"
            variaveis = set()
        # Ligar as variaveis usadas na expr ao nodo
        for var in variaveis:
            nodoVar = self.variaveisFuncao[var]
            self.adicionarAresta(nodoVar, nodo, constraint=True, color="green")
        # Ligar a operacao à variavel escrita
        if isinstance(tree.children[0], Token) and tree.children[0].type == "VAR_NOME":
            nomeVar = tree.children[0].value
            nodoVar = self.variaveisFuncao[nomeVar]
            self.adicionarAresta(nodo, nodoVar, constraint=False, color="green")
        # Retornar o nodo
        return nodo

    # Utilizado nas operacoes
    def funcao_call(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree))
        return nodo

    # Utilizado nas expressoes
    def funcao_call_args(self, tree):
        variables = set()
        for elem in tree.children:
            variables.update(self.visit(elem))
        return variables

    #endregion

    #region Condicionais

    def cond(self, tree):
        if_first = None
        if_last = None
        # Visitar as opções do if
        for elem in tree.children:
            # Adicionar o nodo do if
            if elem.data != "cond_else":
                # Obter o texto e as variaveis da condicao
                if elem.data == "cond_if":
                    texto = self.obterTexto(elem.children[0])
                    texto = "if (" + texto + ")"
                    variaveis = self.visit(elem.children[0])
                else:
                    texto = texto = self.obterTexto(elem.children[0].children[0])
                    texto = "else if (" + texto + ")"
                    variaveis = self.visit(elem.children[0].children[0])
                # Inserir o nodo da condicao
                nodo_atual = self.adicionarNodo(texto, color="chocolate")
                # Ligar a condicao às variaveis usadas
                for var in variaveis:
                    nodoVar = self.variaveisFuncao[var]
                    self.adicionarAresta(nodoVar, nodo_atual, constraint=True, color="green")
                # Guardar o primeiro if
                if if_first is None:
                    if_first = nodo_atual
                # Ligar os ifs
                else:
                    self.adicionarAresta(if_last, nodo_atual, constraint=True, color="blue")
                # Guardar o ultimo if
                if_last = nodo_atual
                # Inserir o nodo "then"
                nodo_atual = self.adicionarNodo("then", color="chocolate")
                self.adicionarAresta(if_last, nodo_atual, constraint=True, color="blue")
            # Registar que existe else
            else:
                nodo_atual = self.adicionarNodo("else", color="chocolate")
                self.adicionarAresta(if_last, nodo_atual, constraint=True, color="blue")
            # Adicionar os nodos do corpo
            corpo = self.visit(elem)
            self.adicionarAresta(nodo_atual, corpo, constraint=True, color="blue")
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
        condicao = self.adicionarNodo("while (" + texto + ")", color="darkgoldenrod")
        # Ligar a condicao às variaveis usadas
        variaveis = self.visit(tree.children[0])
        for var in variaveis:
            nodoVar = self.variaveisFuncao[var]
            self.adicionarAresta(nodoVar, condicao, constraint=True, color="green")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo, constraint=True, color="blue")
        # Retornar o nodo da condição
        return condicao

    def ciclo_do_while(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[1])
        condicao = self.adicionarNodo("do while (" + texto + ")", color="darkgoldenrod")
        # Ligar a condicao às variaveis usadas
        variaveis = self.visit(tree.children[1])
        for var in variaveis:
            nodoVar = self.variaveisFuncao[var]
            self.adicionarAresta(nodoVar, condicao, constraint=True, color="green")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[0])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo, constraint=True, color="blue")
        # Retornar o nodo da condição
        return condicao

    def ciclo_for(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("for (" + texto + ")", color="darkgoldenrod")
        # Obter os nodos de fluxo do for e as variaveis da expressao
        nodos_head, variaveis = self.visit(tree.children[0])
        # Ligar os nodos da head do for a condicao
        for nodo in nodos_head:
            self.adicionarAresta(condicao, nodo, constraint=True, color="blue")
        # Ligar a condicao às variaveis usadas
        for var in variaveis:
            nodoVar = self.variaveisFuncao[var]
            self.adicionarAresta(nodoVar, condicao, constraint=True, color="green")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo, constraint=True, color="blue")
        # Retornar o nodo da condição
        return condicao

    def ciclo_for_head(self, tree):
        nodos = []
        variaveis = set()
        for elem in tree.children:
            # Determinar as variaveis da expressao
            if elem.data == "ciclo_for_head_2":
                variaveis = self.visit(elem.children[0])   
            # Determinar os nodos de fluxo
            else:
                for inst in elem.children:
                    nodos.append(self.visit(inst))
        return nodos, variaveis

    def ciclo_foreach(self, tree):
        # Criar o nodo da condição
        texto = self.obterTexto(tree.children[0])
        condicao = self.adicionarNodo("foreach (" + texto + ")", color="darkgoldenrod")
        # Obter o nome e nodo da variavel de controlo
        nodo_head, variaveis = self.visit(tree.children[0])
        # Ligar o nodo da variavel ao foreach
        self.adicionarAresta(condicao, nodo_head, constraint=True, color="blue")
        # Ligar a condicao às variaveis usadas
        for var in variaveis:
            nodoVar = self.variaveisFuncao[var]
            self.adicionarAresta(nodoVar, condicao, constraint=True, color="green")
        # Criar os nodos do corpo
        corpo = self.visit(tree.children[1])
        # Ligar o corpo à condição
        self.adicionarAresta(condicao, corpo, constraint=True, color="blue")
        # Retornar o nodo da condição
        return condicao

    def ciclo_foreach_head(self, tree):
        nodo = self.adicionarNodo(self.obterTexto(tree.children[0], tree.children[1]))
        # Registar o nodo como a origem da variavel
        nomeVar = tree.children[1].value
        self.variaveisFuncao[nomeVar] = nodo
        # Ligar as variaveis usadas na expr ao nodo
        variaveis = self.visit(tree.children[2])
        for var in variaveis:
            nodoVar = self.variaveisFuncao[var]
            self.adicionarAresta(nodoVar, nodo, constraint=True, color="green")
        # Retornar o nodo
        return nodo, variaveis

    #endregion

    #region Expressoes

    def expr(self, tree):
        variables = set()
        for val in tree.find_data("val"):
            elem = val.children[0]
            # Se for uma variavel
            if isinstance(elem, Token) and elem.type == "VAR_NOME":
                variables.add(elem.value)
            # Se for uma funcao call
            elif isinstance(elem, Tree) and elem.data == "funcao_call":
                variables.update(self.visit(elem.children[1]))
        return variables

    #endregion