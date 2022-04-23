from gramatica import grammar
from interpreter import MyInterpreter
from lark import Lark
from report_generator import generateReport

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
}

int bar(int a) { }
"""

frase = """
void main(int a) {
    a = 0;
}

void foo(List<List<float>> list) {
    int i = 1;
    i = 2;
    i += 1;
    i++;

    if (True) {
        i++;
    }
    else if (False) {
        if (False) {

        }
        else {

        }
    }
    else if (False && True) {
        if (True) {
            if(True) {

            }
        }
    }
    else {

    }

    Map<int, List<int>> map;

    int List = 1;
}
"""

frase = """
void main() {
    foreach (List<int> i in [[1, 2], [3, 4], [5, 6]]) {
        i[0]++;
    }

    foreach(Tuple<int, List<int>> entry in { 1: [1, 2], 2: [3, 4], 3: [4, 5] }) {
    }

    List<List<List<int>>> l = [];
    int i = l[0][0][0];
}

List<int> foo() {
}

void bar() {
    List<int> list;
    list[0] += True;
}

"""

frase = """
void main() {
    int i;
    int j;

    while (True) {
        i = 0;
        j = 1;
        i++;
    }

    if (True) {
        i++;
    }
    i++;
}
"""

frase = """
void main(bool b) {
    int a;
    int a;
    c += True;
}

void main(bool c) {
    int x = y + 2.1;
    int y = x[0];
    List<int> l = [1, 2, 3];
    x = l[3.1];
    
    foreach(int i in l) {
        
    }
}

int foo() {
    List<int, int> l1;
    l1 = [2.1, 3];
    Tuple<int> t = (1);
    Ola<int> ola = 1;
    List l = [1, 2];
    if (1) { }
}
"""

frase = """
void main() {
    int i;
    int j;
    int k;

    if (True) {
        i = 0;
    }
    else if (False) {
        i = 1;
        j = 0;
    }
    else {
        i = 2;
        j = 1;
    }

    i++;
    j++;
}
"""

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
        }
        """
    ),
    (
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
    )
]

l = Lark(grammar)
i = MyInterpreter()

for num, (tag, codigo) in enumerate(testes):
    tree = l.parse(codigo)
    i.setupVariables()
    i.visit(tree)
    i.gerarNotesInfo()
    titulo = str(num) + "_" + tag
    generateReport(i.notas, titulo)

#l = Lark(grammar)
#tree = l.parse(frase)
#i = MyInterpreter()
#i.visit(tree)
#i.gerarNotesInfo()
#generateReport(i.notas)