from gramatica import grammar
from interpreter_analisador import InterpreterAnalisador
from interpreter_cfg import InterpreterCFG
from lark import Lark
from interpreter_sdg import InterpreterSDG
from report_generator import generateReport
import graphviz

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

codigo = """
int glob_a = 0;
float glob_b = 1.0;

int foo(int i) { }

void main(int arg0, float arg1) {
    int x = 0;
    int y = 0;
    x += y;
    if (x || y * foo(x) + arg0 && glob_b) {
        y++;
        arg1 += foo(x + y);
    }
    else { }
}

void teste_ciclo() {
    int i = 0;
    int max = 100;
    while(i < max) {
        glob_a += i * foo(i);
        i++;
    }
}

void teste_ciclo_1() {
    int i = 0;
    int max = 100;
    do {
        glob_a += i * foo(i);
        i++;
    } while(i < max);
}

void teste_ciclo_2() {
    for (int i = 0, int max = 100; i < max; i++) {
        glob_a += i * foo(i);
    }
}
"""

l = Lark(grammar, propagate_positions=True)
tree = l.parse(codigo)

ia = InterpreterAnalisador()
ia.visit(tree)

#icfg = InterpreterCFG(codigo, ia.funcoesOrd)
#icfg.visit(tree)

isdg = InterpreterSDG(codigo, ia.funcoesOrd)
isdg.visit(tree)

#i.gerarNotesInfo()
#generateReport(i.notas, codigo, "report")

for funcoes in ia.funcoes.values():
    for func in funcoes:
        graph = func.sdg
        #print(graph.pipe(encoding='utf-8'))
        graph.render(filename="./graphs/" + func.nome)