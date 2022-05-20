from gramatica import grammar
from interpreter import MyInterpreter
from lark import Lark
from report_generator import generateReport

codigo = """
void main() {
    int a = 1;
    int b = 2;
    int c = a + b;
}
"""

l = Lark(grammar, propagate_positions=True)
i = MyInterpreter()
i.setupVariables()

tree = l.parse(codigo)
i.visit(tree)

#i.gerarNotesInfo()
#generateReport(i.notas, codigo, "report")

for funcoes in i.funcoes.values():
    for func in funcoes:
        print(func.numInstrucoes)
        graph = func.controlFlowGraph
        graph.render(filename='ola', format="svg")