grammar = """
start        : funcao*

type        : ATOMIC_TYPE
ATOMIC_TYPE : "void" | "int" | "float" | "bool"

val         : NUM | BOOL | VAR | funcao_call
NUM         : /\d+(\.\d+)?/
BOOL        : "True" | "False"
VAR         : /[a-zA-Z_]\w*/
FUNC_NAME   : /[a-zA-Z_]\w*/

funcao           : type FUNC_NAME "(" funcao_args? ")" "{" corpo "}"
funcao_args      : type VAR ("," type VAR)*
funcao_call      : FUNC_NAME "(" funcao_call_args? ")"
funcao_call_args : expr ("," expr)*

corpo          : (operacao | operacao_end)*
operacao       : (cond | ciclo_while | ciclo_for)
operacao_end   : (decl | decl_atrib | atrib | funcao_call | ciclo_do_while) ";"

decl          : type VAR
decl_atrib    : type VAR "=" expr
atrib         : atrib_simples | atrib_bin | atrib_un
atrib_simples : VAR "=" expr
atrib_bin     : VAR OP_BIN_ATRIB "=" expr
atrib_un      : VAR OP_UN_ATRIB
OP_BIN_ATRIB  : "+" | "-" | "*" | "/" | "%"
OP_UN_ATRIB   : "++" | "--"

cond         : cond_if cond_else_if* cond_else?
cond_if      : "if" "(" expr ")" "{" corpo "}"
cond_else_if : "else" cond_if
cond_else    : "else" "{" corpo "}"

ciclo_while    : "while" "(" expr ")" "{" corpo "}"
ciclo_do_while : "do" "{" corpo "}" "while" "(" expr ")"

ciclo_for        : "for" "(" ciclo_for_head ")" "{" corpo "}"
ciclo_for_head   : ciclo_for_head_1? ";" ciclo_for_head_2? ";" ciclo_for_head_3?
ciclo_for_head_1 : (decl | decl_atrib | atrib) ("," (decl | decl_atrib | atrib))*
ciclo_for_head_2 : expr
ciclo_for_head_3 : atrib ("," atrib)*

expr         : expr_or
expr_or      : (expr_or OP_EXPR_OR expr_or)
             | expr_and
expr_and     : (expr_and OP_EXPR_AND expr_and)
             | expr_eq
expr_eq      : (expr_eq OP_EXPR_EQ expr_eq)
             | expr_ord
expr_ord     : (expr_ord OP_EXPR_ORD expr_ord)
             | expr_add
expr_add     : (expr_add OP_EXPR_ADD expr_add)
             | expr_mul
expr_mul     : (expr_mul OP_EXPR_MUL expr_mul)
             | expr_un
expr_un      : expr_op_un expr_un
             | expr_symb
expr_symb    : val | "(" expr ")"

expr_op_un   : (OP_EXPR_UN | op_expr_cast)
op_expr_cast : "(" type ")"

OP_EXPR_OR   : "||"
OP_EXPR_AND  : "&&"
OP_EXPR_EQ   : "==" | "!="
OP_EXPR_ORD  : "<" | "<=" | ">" | ">="
OP_EXPR_ADD  : "+" | "-"
OP_EXPR_MUL  : "*" | "/" | "%"
OP_EXPR_UN   : "+" | "-" | "!"

%import common.WS
%ignore WS
"""