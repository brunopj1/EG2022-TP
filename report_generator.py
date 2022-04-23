from language_notes import LanguageNoteType

#region Templates HTML

templatePage = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Report</title>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="w3.css">
    </head>
    <body>
        $(NOTAS)
    </body>
</html>
'''

templateNota = '''
<div class="w3-round-xlarge w3-panel" style="border: 2px solid $(COLOR);">
    <h3 style="display:inline-block">
        $(NOME)
    </h3>
    <div style="display: inline-block; text-align: right; float:right"> 
        $(POSICAO)
    </div>
    <p>
        $(DESCRICAO)
    </p> 
</div>
'''

#endregion

def generateReport(notas):

    content = ""

    for n in notas:

        if n.tipo == LanguageNoteType.ERROR:
            color = "red"
            posicao = "Linha: 0, Coluna: 0"
        elif n.tipo == LanguageNoteType.WARNING:
            color = "orange"
            posicao = "Linha: 0, Coluna: 0"
        else: #n.tipo == LanguageNoteType.INFO
            color = "blue"
            posicao = ""

        contentNota = templateNota.replace("$(NOME)", n.__class__.__name__, 1)
        contentNota = contentNota.replace("$(POSICAO)", posicao, 1)
        contentNota = contentNota.replace("$(DESCRICAO)", n.message, 1)
        contentNota = contentNota.replace("$(COLOR)", color, 1)
        content += contentNota

    page = templatePage.replace("$(NOTAS)", content, 1)

    f = open("output.html", "w")
    f.write(page)
    f.close