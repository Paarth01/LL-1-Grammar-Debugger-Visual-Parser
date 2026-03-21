from grammar_core import Grammar
from transform import eliminate_left_recursion
from first_follow import compute_first, compute_follow
from parse_table import generate_parse_table, has_conflicts
from parser_ll1 import parse

grammar_input = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""

test_string = "id + id * id"

g = Grammar()
g.parse_from_string(grammar_input)

print("\n--- Original Grammar ---")
print(g.display())

g_trans = eliminate_left_recursion(g)
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

success, trace, tree = parse(g_trans, table, test_string)
print(f"\n--- Parsing Success: {success} ---")
for t in trace:
    print(t)
