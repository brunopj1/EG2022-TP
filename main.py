from gramatica import grammar
from interpreter import MyInterpreter
from lark import Lark
from report_generator import generateReport

codigo = """
void main() {
    int a;
}
"""

l = Lark(grammar, propagate_positions=True)
i = MyInterpreter()
i.setupVariables()

tree = l.parse(codigo)
i.visit(tree)
i.gerarNotesInfo()
generateReport(i.notas, codigo, "report")