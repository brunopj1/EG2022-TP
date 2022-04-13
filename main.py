from gramatica import grammar
from interpreter import Lark, MyInterpreter

frase = """

int foo(int a) {
    a++;
    int b = 1;
    b++;
    b += 2;
}

float PI = 3.14;

void foo() {
    int a = (int) (1.0 + 2 * PI);
    bool b = False;
    foo(3 + a);
    for (int z = 1; z < 14.3; z += (int) 2.3) {
    }
    bool c = False;
    c = !c;
    c += True;
}

int bar(int a) { }
"""

l = Lark(grammar)
i = MyInterpreter()

tree = l.parse(frase)
i.visit(tree)
#print(tree.pretty())