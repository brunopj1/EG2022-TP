from gramatica import grammar
from interpreter_analisador import InterpreterAnalisador
from interpreter_cfg import InterpreterCFG
from lark import Lark
from interpreter_sdg import InterpreterSDG
from report_generator import generateReport

testes = [
(
# Titulo
"if", 
# Codigo
"""
int a = 10;

void foo(bool b) {
    int i = a - 2;
    int j = i - a;
    int res = 0;
    if (b) {
        if (i > j) {
            res = 10;
        }
    }
    else {
        res = 100;
    }
    res *= i;
}
"""
), (
# Titulo
"while", 
# Codigo
"""
int a = 10;

void foo(bool b) {
    int i = a - 2;
    int j = i - a;
    int res = 0;
    while (b) {
        res++;
        if (res > j + i) {
            b = False;
        }
    }
    res *= i;
}
"""
), (
# Titulo
"do_while", 
# Codigo
"""
int a = 10;

void foo(bool b) {
    int i = a - 2;
    int j = i - a;
    int res = 0;
    do {
        res++;
        if (res > j + i) {
            b = False;
        }
    } while (b);
    res *= i;
}
"""
), (
# Titulo
"for", 
# Codigo
"""
int a = 10;

void foo(bool b) {
    int res = 0;
    for (int i = a - 2, int j = i - a; b; ) {
        res++;
        if (res > j + i) {
            b = False;
        }
    }
    res *= 10;
}
"""
), (
# Titulo
"foreach", 
# Codigo
"""
int a = 10;

void foo(bool b) {
    int i = a - 2;
    int j = i - a;
    int res = 0;
    List<int> l = [ 1, 2, 3, 4, 5 ];
    foreach (int elem in l) {
        if (b) {
            res += elem;
        }
        if (res > j + i) {
            b = False;
        }
    }
    res *= i;
}
"""
), (
# Titulo
"foreach_in_range", 
# Codigo
"""
List<int> range(int start, int stop, int step) {
    List<int> l = [];
    int idx = 0;
    while (start < stop) {
        l[idx] = start;
        start += step;
        idx++;
    }
}

List<int> range(int start, int stop) {
    List<int> l = range(start, stop, 1); 
}

void sum() {
    int sum = 0;
    foreach (int val in range(10, 200, 5)) {
        sum += val;
    }
}
"""
)
]

# Criar o Lark
l = Lark(grammar, propagate_positions=True)

# Para cada exemplo
for num, (tag, codigo) in enumerate(testes):

    # Remover as linhas desnecessarias
    codigo = codigo[1:-1]

    # Dar parse ao programa
    tree = l.parse(codigo)
    
    # Detetar erros
    ia = InterpreterAnalisador()
    ia.visit(tree)
    ia.gerarNotesInfo()

    #TODO se houver erros nao gerar os grafos

    # Gerar os CFG
    icfg = InterpreterCFG(codigo, ia.funcoesOrd)
    icfg.visit(tree)

    # Gerar os SDG
    isdg = InterpreterSDG(codigo, ia.funcoesOrd)
    isdg.visit(tree)

    # Gerar o relatorio
    titulo = "./exemplos/" + str(num) + "_" + tag
    generateReport(ia.notas, ia.funcoesOrd, codigo, titulo)