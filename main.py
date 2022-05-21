from gramatica import grammar
from interpreter_analisador import InterpreterAnalisador
from interpreter_grafos import InterpreterGrafos
from lark import Lark
from report_generator import generateReport

codigo = """
void main() {
    int a = 1;
    int b = 2;
    int c = a + b;
    if (True) { }
    else if (True) {
        if (False) {
            a++;
        }
        b++;
    }
    else { }
}
"""

l = Lark(grammar, propagate_positions=True)
tree = l.parse(codigo)

ia = InterpreterAnalisador()
ia.visit(tree)

ig = InterpreterGrafos(ia.funcoesOrd)

#i.gerarNotesInfo()
#generateReport(i.notas, codigo, "report")

for funcoes in ia.funcoes.values():
    for func in funcoes:
        print(func.numInstrucoes)
        graph = func.controlFlowGraph
        graph.render(filename='ola', format="svg")