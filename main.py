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

    int z;
    z = 1;
    z++;

    List<List<List<int>>> l = (List<List<List<int>>>) «
        [[1,2], [2,3]],
        [[3,-4]],
        []
    »;

    Map<int, List<int>> m = {
        1: [],
        2: [],
        3: []
    };

    List<float> lm = m[0];

    Set<bool> s = « True, False, False »;
    List<bool> zzz = (List<bool>) s;
    int iii = 4;
    bool bbb = zzz[iii];

    Tuple<bool, bool, int> tuple = ( True, False, (int) 12.0 );
    int b1 = tuple[0];
    int b2 = tuple[0] * 2;
}

int bar(int a) { }
"""

l = Lark(grammar)
i = MyInterpreter()

tree = l.parse(frase)
i.visit(tree)