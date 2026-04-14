def compute_first(grammar):
    """
    Computes the FIRST sets for all symbols in the grammar.
    Returns a dictionary mapping symbol -> set of terminals (and 'epsilon').
    """
    first = {nt: set() for nt in grammar.non_terminals}
    for t in grammar.terminals:
        first[t] = {t}
    first['epsilon'] = {'epsilon'}
    
    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.rules.items():
            for prod in prods:
                # Add FIRST(prod) to FIRST(nt)
                for sym in prod:
                    before_len = len(first[nt])
                    # Add everything except epsilon
                    first[nt].update(first[sym] - {'epsilon'})
                    if len(first[nt]) > before_len:
                        changed = True
                    
                    if 'epsilon' not in first[sym]:
                        break
                else:
                    # If we reached the end and all symbols can derive epsilon
                    if 'epsilon' not in first[nt]:
                        first[nt].add('epsilon')
                        changed = True
                        
    return first

def compute_follow(grammar, first_sets):
    """
    Computes the FOLLOW sets for all non-terminals in the grammar.
    Returns a dictionary mapping non-terminal -> set of terminals (and '$').
    """
    follow = {nt: set() for nt in grammar.non_terminals}
    follow[grammar.start_symbol].add('$')
    
    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.rules.items():
            for prod in prods:
                for i, sym in enumerate(prod):
                    if sym in grammar.non_terminals:
                        next_first = set()
                        can_derive_epsilon = True
                        
                        # Find FIRST of the rest of the production
                        for next_sym in prod[i+1:]:
                            next_first.update(first_sets[next_sym] - {'epsilon'})
                            if 'epsilon' not in first_sets[next_sym]:
                                can_derive_epsilon = False
                                break
                        
                        # If loop finishes normally, can_derive_epsilon remains True
                        
                        before_len = len(follow[sym])
                        follow[sym].update(next_first)
                        
                        if can_derive_epsilon:
                            follow[sym].update(follow[nt])
                            
                        if len(follow[sym]) > before_len:
                            changed = True
                            
    return follow
