from gramatica import grammar
from interpreter_analisador import InterpreterAnalisador
from interpreter_cfg import InterpreterCFG
from lark import Lark
from interpreter_sdg import InterpreterSDG
from report_generator import generateReport

codigo = """
void main() {
    int i = 0;
    int max = 100;
    int res = 0.5;
    while (i < max) {
        if (i % 2) {
            res += i;
        }
    }
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