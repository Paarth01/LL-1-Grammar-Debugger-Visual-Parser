from grammar_core import Grammar
from transform import eliminate_left_recursion, left_factor
from first_follow import compute_first, compute_follow
from parse_table import generate_parse_table, has_conflicts
from parser_ll1 import parse
from lexer import tokenize

grammar_input = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""

test_string = "id + id * id"

g = Grammar()
g.parse_from_string(grammar_input)

print("\n--- Original Grammar ---")
print(g.display())

g_no_lr = eliminate_left_recursion(g)
g_trans = left_factor(g_no_lr)
print("\n--- Transformed Grammar ---")
print(g_trans.display())

first = compute_first(g_trans)
follow = compute_follow(g_trans, first)
print("\n--- FIRST Sets ---")
for k, v in first.items(): print(f"{k}: {v}")

print("\n--- FOLLOW Sets ---")
for k, v in follow.items(): print(f"{k}: {v}")

table = generate_parse_table(g_trans, first, follow)
print(f"\n--- Parse Table Conflicts: {has_conflicts(table)} ---")

tokens = tokenize(test_string, use_lexer=True)
success, trace, tree = parse(g_trans, table, follow, tokens)
print(f"\n--- Parsing Success: {success} ---")
for t in trace:
    print(t)
