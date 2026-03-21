def generate_parse_table(grammar, first_sets, follow_sets):
    """
    Generates the LL(1) parsing table.
    Returns a dictionary: table[nt][term] = list of production RHS
    If a cell contains more than 1 production, there is a conflict.
    """
    terminals_and_eof = grammar.terminals | {'$'}
    table = {nt: {t: [] for t in terminals_and_eof} for nt in grammar.non_terminals}
    
    for nt, prods in grammar.rules.items():
        for prod in prods:
            # First find FIRST(prod)
            prod_first = set()
            can_derive_epsilon = True
            
            if prod != ['epsilon']:
                for sym in prod:
                    prod_first.update(first_sets[sym] - {'epsilon'})
                    if 'epsilon' not in first_sets[sym]:
                        can_derive_epsilon = False
                        break
            else:
                can_derive_epsilon = True

            for t in prod_first:
                if t != 'epsilon':
                    if prod not in table[nt][t]:
                        table[nt][t].append(prod)
                
            if can_derive_epsilon:
                for t in follow_sets[nt]:
                    if prod not in table[nt][t]:
                        table[nt][t].append(prod)
                        
    return table

def has_conflicts(parse_table):
    """Checks if the given parse_table has any LL(1) conflicts."""
    for nt, row in parse_table.items():
        for t, prods in row.items():
            if len(prods) > 1:
                return True
    return False
