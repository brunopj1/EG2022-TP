import re
from language_notes import LanguageNoteType

#region Templates HTML

templatePage = '''
<!DOCTYPE html>
<head>
    <title>Report</title>
    <meta charset="UTF-8">
</head>
<style>
    body { display: flex; flex-direction: column; gap: 20px; font-family: Verdana, sans-serif; font-size: 15px; line-height: 1.5 }
    pre {margin: 0px;}
    .note { margin: 20px; padding: 0px 20px 0px 20px; border-radius: 20px; width: 85%; margin: auto; position: relative; background-color: white; border: solid; border-width: 4px; border-color: red; }
    .note-titulo { position: relative; top: -15px; }
    .note-descricao { position: relative; top: -15px; }
    .note-codigo { padding: 10px; border-radius: 10px; position: relative; top: -15px; border: 2px solid black; }
    .codigo-even { background-color: rgb(200, 200, 200); }
    .codigo-odd { background-color: rgb(225, 225, 225); }
    .note-codigo-highlight { color: red; }
    .note-posicao { position: absolute; top: 5px; right: 10px; }
    .grafo { border: 2px solid black; }
</style>
<body>$(NOTAS)</body>
</html>
'''

templateNota = '''
<div class="note" style="border-color: $(COLOR);">
    <h1 class="note-titulo">$(NOME)</h1>
    <p class="note-descricao">$(DESCRICAO)</p>
    $(CODIGO)
    <div class="note-posicao">$(POSICAO)</div>
</div>
'''

templateCodigo = "<div class=\"note-codigo\"><code>$(CODIGO)</code></div>"

templateLinhaCodigo = "<pre class=\"codigo-$(PARIDADE)\">$(CODIGO)</pre>"

templateHighlightCodigo = "<b class=\"note-codigo-highlight\">$(CODIGO)</b>"

templateNotaGrafo = '''
<div class="note note-grafos" style="border-color: green;">
    <h1 class="note-titulo">$(FUNCAO)</h1>
    <h2 class="grafo-titulo">Control Flow Graph:</h2>
    <div class="grafo">
        $(CFG)
    </div>
    <h2 class="grafo-titulo">System Dependency Graph:</h2>
    <div class="grafo">
        $(SDG)
    </div>
    <h2 class="grafo-titulo">Complexidade de McCabe:</h2>
    <p class="grafo-texto">Numero de nodos: <b>$(NODOS)</b></p>
    <p class="grafo-texto">Numero de arestas: <b>$(ARESTAS)</b></p>
    <p class="grafo-texto">Complexidade: <b>$(COMPLEXIDADE)</b></p>
</div>
'''

#endregion

def fixHtmlSymbols(text):
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("«", "&laquo;")
    text = text.replace("»", "&raquo;")
    return text

def generateCodigoNota(nota, codigo):

    linhas = codigo.split("\n")

    # Determinar quais as linhas iniciais
    if nota.posicao[0] >= 2:
        linhaInicial = nota.posicao[0] - 2
        linhaInicialExcerto = 1
    else:
        linhaInicial = 0
        linhaInicialExcerto = 0

    # Determinar as linhas finais
    if nota.posicaoFim[0] <= len(linhas) - 1:
        linhaFinal = nota.posicaoFim[0] + 1
        linhaFinalExcerto = linhaFinal - linhaInicial - 2
    else:
        linhaFinal = nota.posicaoFim[0]
        linhaFinalExcerto = linhaFinal - linhaInicial - 1

    # Processar as linhas
    linhas = linhas[linhaInicial:linhaFinal]
    novasLinhas = []

    tamanhoNum = len(str(linhaFinal + 1))
    for idx, linha in enumerate(linhas):

        # Variaveis uteis
        paridade = "even" if idx % 2 == 0 else "odd"
        num = str(linhaInicial + idx + 1)
        num = " " * (tamanhoNum - len(num)) + num

        # Inserir o highlight da linha
        if idx >= linhaInicialExcerto and idx <= linhaFinalExcerto:
            idxFrom = 0 if idx > linhaInicialExcerto else nota.posicao[1] - 1
            idxTo = len(linha) if idx < linhaFinalExcerto else nota.posicaoFim[1] - 1

            linha = [
                fixHtmlSymbols(linha[0       : idxFrom]),
                fixHtmlSymbols(linha[idxFrom : idxTo]),
                fixHtmlSymbols(linha[idxTo   : len(linha)])
            ]

            linha[1] = templateHighlightCodigo.replace("$(CODIGO)", linha[1], 1)

            linha = "".join(linha)

        # Se nao tiver highlight corrigir os simbolos
        else:
            linha = fixHtmlSymbols(linha)

        # Criar a linha
        novaLinha = templateLinhaCodigo.replace("$(CODIGO)", f" {num} | {linha}", 1)
        novaLinha = novaLinha.replace("$(PARIDADE)", paridade, 1)
        novasLinhas.append(novaLinha)
    
    # Returnar as linhas numa string
    novasLinhas = "\n".join(novasLinhas)
    excertoCodigo = templateCodigo.replace("$(CODIGO)", novasLinhas, 1)
    return excertoCodigo

def obterGrafoSVG(grafo):

    # Separar as linhas
    grafo_str = grafo.pipe(encoding='utf-8')

    # Procurar o codigo do svg
    svg = re.search(r"(<svg width=\")(?:[^\"]+)(\" height=\")(?:[^\"]+)(\"(?:.|\n)*</svg>)", grafo_str)

    # Ajustar o codigo do svg
    svg_str = svg.group(1) + "fit-content" + svg.group(2) + "fit-content" + svg.group(3)

    return svg_str

def generateReport(notas, funcoes, codigo, nomeFicheiro):

    content = ""

    # Adicionar as notas
    for n in notas:

        # Determinar a cor
        if n.tipo == LanguageNoteType.ERROR:
            color = "red"
        elif n.tipo == LanguageNoteType.WARNING:
            color = "orange"
        else: #n.tipo == LanguageNoteType.INFO
            color = "blue"

        # Determinar a posicao
        posicao = "" if n.posicao is None else f"Linha: {n.posicao[0]}, Coluna: {n.posicao[1]}"

        # Determinar o excerto de codigo
        excertoCodigo = ""
        if n.tipo != LanguageNoteType.INFO:
            excertoCodigo = generateCodigoNota(n, codigo)

        # Construir a nota em html
        contentNota = templateNota.replace("$(NOME)"    , n.__class__.__name__, 1)
        contentNota = contentNota.replace("$(DESCRICAO)", n.message           , 1)
        contentNota = contentNota.replace("$(CODIGO)"   , excertoCodigo       , 1)
        contentNota = contentNota.replace("$(POSICAO)"  , posicao             , 1)
        contentNota = contentNota.replace("$(COLOR)"    , color               , 1)
        content += contentNota

    # Adicionar os grafos
    for func in funcoes:

        # Funcao de processamento dos argumentos
        def ajustarArgsFunc(tipo, nome):
            return f"<span style=\"color: green\">{tipo}</span> <span style=\"color: cornflowerblue\">{nome}</span>"
        
        # Obter o nome da funcao
        args = [ajustarArgsFunc(tipo, nome) for tipo, nome in zip(func.args_tipo, func.args_nome)]
        nome = func.nome + "(" + ", ".join(args) + ")"

        # Obter grafos
        cfg = obterGrafoSVG(func.cfg)
        sdg = obterGrafoSVG(func.sdg)

        # Calcular a complexidade
        num_nodos = func.mccabe_nodos
        num_arestas = func.mccabe_arestas
        complexidade = num_arestas - num_nodos + 2

        # Gerar a nota
        contentNota = templateNotaGrafo.replace("$(FUNCAO)", nome             , 1)
        contentNota = contentNota.replace("$(CFG)"         , cfg              , 1)
        contentNota = contentNota.replace("$(SDG)"         , sdg              , 1)
        contentNota = contentNota.replace("$(NODOS)"       , str(num_nodos)   , 1)
        contentNota = contentNota.replace("$(ARESTAS)"     , str(num_arestas) , 1)
        contentNota = contentNota.replace("$(COMPLEXIDADE)", str(complexidade), 1)
        content += contentNota

    # Criar o ficheiro
    page = templatePage.replace("$(NOTAS)", content, 1)
    f = open(nomeFicheiro + ".html", "w")
    f.write(page)
    f.close