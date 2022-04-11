from linguagem import *

frase = """

int foo(int a) {
    a++;
}

void foo() {
    int a = (int) (1.0 + 2 * 1.5);
    bool b = False;
    foo((float) 3 + a);
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