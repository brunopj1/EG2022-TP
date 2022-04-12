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
    while (b) {
    }
    bool c = False;
    c = !c;
}

int bar(int a) { }
"""

l = Lark(grammar)
i = MyInterpreter()

tree = l.parse(frase)
i.visit(tree)