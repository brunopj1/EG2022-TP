from linguagem import *

_frase = """
int a = 4;
a = 2;
int x = -1 + (3 * a - 4) && 2;
int y = -1;

if (1) {
    int b = x + 3 * y;
}

int b = 1;
b += b;

while (b > 1) {
    int k = b + 2;
}

for (int i = 0, int j = 10; i <= j; i++, j--) {
    int k = i + j;
}
"""

frase = """
int a = (int) (1.0 + 2 * 1.5);
bool b = False;
while (b) {
}
bool c = False;
c = !c;
"""

l = Lark(grammar)
i = MyInterpreter()

tree = l.parse(frase)
i.visit(tree)