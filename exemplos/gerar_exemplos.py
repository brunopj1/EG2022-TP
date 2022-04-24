from gramatica import grammar
from interpreter import MyInterpreter
from lark import Lark
from report_generator import generateReport

testes = [
(
# Titulo
"Variaveis", 
# Codigo
"""
int a = b;

void main() {
    int b;
    int a = b;
    int c;
    z = a;
}
"""
), (
# Titulo
"Funcoes", 
# Codigo
"""
void foo() { }
bool foo() { }

bool foo(int a) { }
void foo(int b) { }

bool foo(float a, int b) { }

void main() {
    int x = 2;
    bool b1 = foo(1, x);
    bool b2 = bar();
}
"""
), (
# Titulo
"Tipos_Invalidos_Incompativeis", 
# Codigo
"""
void main() {
    Batata b1;
    Batata<int> b2;
    List<int, float> l1;

    List<int> l2 = [ 1, True, 3 ];
}
"""
), (
# Titulo
"Atribuicoes_Casts", 
# Codigo
"""
void main() {
    int i = 2.1;
    i = (int) 2.1;
    i = (int) True;

    List<int> l1 = [ 2.1, 4, 5 ];
    List<int> l2 = (List<int>) [ 2.1, 4, 5 ];

    List<int> l3 = « 1, 2, 3 »;
    List<int> l4 = (List<int>) « 1, 2, 3 »;
    Set<int> s = (Set<int>) [ 1, 2, 3 ];

    List<int> l5 = [ 1, 2, 3 ];
    l5[0] = 99.9;
}
"""
), (
# Titulo
"Acesso_Subtipos", 
# Codigo
"""
void main() {
    List<float> l = [ 1, 2, 3 ];
    float f1 = l[2];
    float f2 = l[2.1];

    Map<float, float> m = {
        1.0: 1.5,
        2.0: 2.5,
        3.0: 3.5
    };

    float f3 = m[1.0];
    float f4 = m[1];
    float f5 = m[True];

    int i = 1[0];
}
"""
), (
# Titulo
"Iteracao_Subtipos", 
# Codigo
"""
void main() {
    List<float> l = [ 1, 2, 3 ];

    Map<float, float> m = {
        1.0: 1.5,
        2.0: 2.5,
        3.0: 3.5
    };

    foreach(float f in l) { }

    foreach(float f in m) { }

    foreach(Tuple<float, float> entry in m) { }

    foreach(int i in 15) { }
}
"""
), (
# Titulo
"Operadores_Condicoes_Invalidas", 
# Codigo
"""
void main() {
    int i = 1 * True;
    bool b = ! 2.0;
    int j = - True;

    if (1) { }
    while (1) { }
    do { } while (1);
    for (int a = 0; 1; a++) { }
}
"""
), (
# Titulo
"Ifs_Aninhados", 
# Codigo
"""
void main() {
    bool b = True;
    if (b) {
        if (!b) {

        }
        b = !b;
    }

    if (!b) {
        if (b) {
            if (b || !b) { 

            }
        }
    }
}
"""
), (
# Titulo
"Nome_Proibido", 
# Codigo
"""
void main() {
    float float = 3.5;
    int bool = 2;
    int List = 3 + 2;
    bool True = False;
}
"""
)
]

l = Lark(grammar, propagate_positions=True)
i = MyInterpreter()

for num, (tag, codigo) in enumerate(testes):
    tree = l.parse(codigo)
    i.setupVariables()
    i.visit(tree)
    i.gerarNotesInfo()
    titulo = str(num) + "_" + tag
    generateReport(i.notas, codigo, titulo)

#l = Lark(grammar)
#tree = l.parse(frase)
#i = MyInterpreter()
#i.visit(tree)
#i.gerarNotesInfo()
#generateReport(i.notas)