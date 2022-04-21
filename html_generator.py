def html_generator(erros, warnings, infos):
    counterE = 1
    counterW = 1
    counterI = 1

    page = '''
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="w3.css">
        </head>
        <body>
    '''

    for e in erros:
        page += f'''
        <div id="erro{counterE}" class="w3-round-xlarge w3-panel" style="border: 2px solid red;">
            <h3 style="display:inline-block">{e.tipo}</h3>  <div style="display:inline-block; text-align: right; float:right">Linha: {e.linha}, Coluna: {e.coluna}</div>
            <p>{e.erro}</p> 
        </div>
        '''
        counterE += 1

    for w in warnings:
        page += f'''
        <div id="erro{counterW}" class="w3-round-xlarge w3-panel" style="border: 2px solid red;">
            <h3 style="display:inline-block">{w.tipo}</h3>  <div style="display:inline-block; text-align: right; float:right">Linha: {w.linha}, Coluna: {w.coluna}</div>
            <p>{w.warning}</p> 
        </div>
        '''
        counterW += 1

    for i in infos:
        page += f'''
        <div id="erro{counterI}" class="w3-round-xlarge w3-panel" style="border: 2px solid red;">
            <h3 style="display:inline-block">{i.tipo}</h3>  <div style="display:inline-block; text-align: right; float:right">Linha: {i.linha}, Coluna: {i.coluna}</div>
            <p>{i.info}</p> 
        </div>
        '''
        counterI += 1

    page += '''
        </body>

    </html>
    '''

    f = open("output.html", "w")
    f.write(page)
    f.close
