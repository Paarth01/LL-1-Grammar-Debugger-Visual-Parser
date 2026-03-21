from grammar_core import Grammar

def eliminate_left_recursion(grammar):
    """
    Eliminates both direct and indirect left recursion from the given grammar.
    Returns a new Grammar object.
    Requires grammar rules to be structured correctly.
    """
    new_grammar = Grammar(grammar.start_symbol)
    
    # Needs ordered non-terminals for indirect recursion logic
    non_terms = list(grammar.rules.keys())
    
    # We will build rules iteratively. Deep copy the lists.
    rules = {nt: [list(p) for p in prods] for nt, prods in grammar.rules.items()}
    
    for i in range(len(non_terms)):
        A_i = non_terms[i]
        
        # Eliminate indirect left recursion
        for j in range(i):
            A_j = non_terms[j]
            # Replace A_i -> A_j gamma with A_i -> delta_1 gamma | delta_2 gamma ... where A_j -> delta_1 | delta_2
            new_A_i_prods = []
            for prod in rules[A_i]:
                if prod and prod[0] == A_j:
                    gamma = prod[1:]
                    for aj_prod in rules[A_j]:
                        if aj_prod == ['epsilon']:
                            new_A_i_prods.append(gamma if gamma else ['epsilon'])
                        else:
                            new_A_i_prods.append(aj_prod + gamma)
                else:
                    new_A_i_prods.append(prod)
            # Remove duplicate productions if any
            unique_prods = []
            for p in new_A_i_prods:
                if p not in unique_prods:
                    unique_prods.append(p)
            rules[A_i] = unique_prods
            
        # Eliminate immediate/direct left recursion for A_i
        alphas = []
        betas = []
        for prod in rules[A_i]:
            if prod and prod[0] == A_i:
                alphas.append(prod[1:] if len(prod) > 1 else ['epsilon'])
            else:
                betas.append(prod)
                
        # If there's direct left recursion
        if alphas:
            A_i_prime = A_i + "'"
            while A_i_prime in rules or A_i_prime in non_terms:
                A_i_prime += "'" # ensure unique name
                
            new_A_i_prods = []
            if not betas:
                # E.g., A -> A a. This technically derives nothing, but algorithm says:
                betas = [['epsilon']]
            
            for beta in betas:
                if beta == ['epsilon']:
                    new_A_i_prods.append([A_i_prime])
                else:
                    new_A_i_prods.append(beta + [A_i_prime])
            
            new_A_i_prime_prods = []
            for alpha in alphas:
                if alpha == ['epsilon']:
                    new_A_i_prime_prods.append([A_i_prime])
                else:
                    new_A_i_prime_prods.append(alpha + [A_i_prime])
            new_A_i_prime_prods.append(['epsilon'])
            
            rules[A_i] = new_A_i_prods
            rules[A_i_prime] = new_A_i_prime_prods
            non_terms.append(A_i_prime)

    new_grammar.rules = rules
    new_grammar.non_terminals = set(rules.keys())
    new_grammar.compute_terminals()
    return new_grammar
