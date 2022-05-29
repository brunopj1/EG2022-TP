from gramatica import grammar
from interpreter_analisador import InterpreterAnalisador
from interpreter_cfg import InterpreterCFG
from lark import Lark
from interpreter_sdg import InterpreterSDG
from report_generator import generateReport

codigo = """
void fun_if() {
    int a = 1;
    int b = 2;
    int c = a + b;
    if (True) { }
    else if (True) {
        if (False) {
            a++;
        }
        else {
            b++;
            a--;
        }
        b++;
    }
    else { }
    a++;
}

void fun_while() {
    int a = 0;
    while (a < 100) {
        a++;
        if (a == 50) {
            a += 10;
        }
    }
    a = 100;
}

void fun_do_while() {
    int a = 0;
    do {
        a++;
        if (a == 50) {
            a += 10;
        }
    } while (a < 100);
    a = 100;
}

void fun_for() {
    int a = 1;
    int b = 0;
    for (int i = 0; i < 10; i++) {
        a *= i;
        if (a % 2 == 0) {
            b++;
        }
        else {
            b--;
        }
    }
    a = 100;
}

void fun_foreach() {
    int a = 1;
    int b = 0;
    foreach (int i in [1,2,3,4,5]) {
        a *= i;
        if (a % 2 == 0) {
            b++;
        }
        else {
            b--;
        }
    }
    a = 100;
}
"""

# Dar parse ao programa
l = Lark(grammar, propagate_positions=True)
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
generateReport(ia.notas, ia.funcoesOrd, codigo, "report")