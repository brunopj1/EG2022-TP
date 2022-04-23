from language_notes import LanguageNoteType

#region Templates HTML

templatePage = '''
<!DOCTYPE html>
<head>
    <title>Report</title>
    <meta charset="UTF-8">
</head>
<style>
    body { display: flex; flex-direction: column; gap: 20px; }
    .note { margin: 20px; padding: 0px 20px 0px 20px; border-radius: 20px; width: 85%; margin: auto; position: relative; background-color: white; border: 4px solid; border-width: 4px; }
    .note-titulo { position: relative; top: -15px; }
    .note-descricao { position: relative; top: -15px; }
    .note-codigo { padding: 10px; border-radius: 10px; position: relative; top: -15px; background-color: rgb(180, 180, 180); }
    .note-codigo-highlight { color: blue; }
    .note-posicao { position: absolute; top: 5px; right: 10px; }
</style>
<body>$(NOTAS)</body>
</html>
'''

templateNota = '''
<div class="note" style="border-color: $(COLOR);">
    <h1 class="note-titulo">$(NOME)</h1>
    <p class="note-descricao">$(DESCRICAO)</p>
    <div class="note-codigo"><code><pre>$(CODIGO)</pre></code></div>
    <div class="note-posicao">$(POSICAO)</div>
    </div>
'''

# TODO <span class="note-codigo-highlight">print("ola");</span>

#endregion

def generateReport(notas, nomeFicheiro):

    content = ""

    for n in notas:

        if n.tipo == LanguageNoteType.ERROR:
            color = "red"
            posicao = f"Linha: {n.posicao[0]}, Coluna: {n.posicao[1]}"
        elif n.tipo == LanguageNoteType.WARNING:
            color = "orange"
            posicao = f"Linha: {n.posicao[0]}, Coluna: {n.posicao[1]}"
        else: #n.tipo == LanguageNoteType.INFO
            color = "blue"
            posicao = ""

        contentNota = templateNota.replace("$(NOME)", n.__class__.__name__, 1)
        contentNota = contentNota.replace("$(DESCRICAO)", n.message, 1)
        contentNota = contentNota.replace("$(CODIGO)", "Teste ;)", 1)
        contentNota = contentNota.replace("$(POSICAO)", posicao, 1)
        contentNota = contentNota.replace("$(COLOR)", color, 1)
        content += contentNota

    page = templatePage.replace("$(NOTAS)", content, 1)

    f = open(nomeFicheiro + ".html", "w")
    f.write(page)
    f.close