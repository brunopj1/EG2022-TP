grammar = """
start  : codigo
codigo : (funcao | (decl_atrib ";"))*

!funcao          : type FUNC_NOME "(" funcao_args ")" "{" corpo "}"
funcao_args      : (type VAR_NOME ("," type VAR_NOME)*)?
funcao_call      : FUNC_NOME "(" funcao_call_args ")"
funcao_call_args : (expr ("," expr)*)?

corpo        : (operacao | operacao_end)*
operacao     : (cond | ciclo_while | ciclo_for | ciclo_foreach)
operacao_end : (decl | decl_atrib | atrib | funcao_call | ciclo_do_while) ";"

decl          : type VAR_NOME
decl_atrib    : type VAR_NOME "=" expr
atrib         : (VAR_NOME | expr) atrib_aux
atrib_aux     : atrib_simples | atrib_bin | atrib_un
atrib_simples : "=" expr
atrib_bin     : OP_BIN_ATRIB "=" expr
atrib_un      : OP_UN_ATRIB
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

ciclo_foreach      : "foreach" "(" ciclo_foreach_head ")" "{" corpo "}"
ciclo_foreach_head : type VAR_NOME "in" expr

expr      : expr_or
expr_or   : (expr_or OP_EXPR_OR expr_or)
          | expr_and
expr_and  : (expr_and OP_EXPR_AND expr_and)
          | expr_eq
expr_eq   : (expr_eq OP_EXPR_EQ expr_eq)
          | expr_ord
expr_ord  : (expr_ord OP_EXPR_ORD expr_ord)
          | expr_add
expr_add  : (expr_add OP_EXPR_ADD expr_add)
          | expr_mul
expr_mul  : (expr_mul OP_EXPR_MUL expr_mul)
          | expr_un
expr_un   : expr_op_un expr_un
          | expr_symb
expr_symb : val
          | expr "[" expr "]"
          | "(" expr ")"

expr_op_un   : (OP_EXPR_UN | op_expr_cast)
op_expr_cast : "(" type ")"

OP_EXPR_OR  : "||"
OP_EXPR_AND : "&&"
OP_EXPR_EQ  : "==" | "!="
OP_EXPR_ORD : "<" | "<=" | ">" | ">="
OP_EXPR_ADD : "+" | "-"
OP_EXPR_MUL : "*" | "/" | "%"
OP_EXPR_UN  : "+" | "-" | "!"

type    : TYPE_NOME subtype?
subtype : "<" type ("," type)* ">"

val    : num | BOOL | VAR_NOME | struct | funcao_call
struct : list | set | map | tuple
num    : INT | FLOAT
INT    : /\d+/
FLOAT  : /\d+\.\d+/
BOOL   : "True" | "False"

list  : "[" (expr ("," expr)*)? "]"
set   : "«" (expr ("," expr)*)? "»"
map   : "{" (expr ":" expr ("," expr ":" expr)*)? "}"
tuple : "(" expr ("," expr)* ")"

VAR_NOME  : /[a-zA-Z_]\w*/
TYPE_NOME : /[a-zA-Z_]\w*/
FUNC_NOME : /[a-zA-Z_]\w*/

%import common.WS
%ignore WS
"""
