class TreeNode:
    def __init__(self, label, id_num):
        self.label = label
        self.id_num = id_num
        self.children = []

def parse(grammar, parse_table, follow_sets, tokens):
    """
    Simulates the LL(1) predictive parsing table on a list of tokens.
    Uses Panic Mode error recovery.
    Returns: success (bool), trace (list of dicts), and root (TreeNode)
    """
    tokens = tokens.copy()
    tokens.append('$')
    
    trace = []
    node_counter = 0
    
    root = TreeNode(grammar.start_symbol, node_counter)
    node_counter += 1
    
    # Stack stores tuples of (symbol, tree_node)
    stack = [('$', None), (grammar.start_symbol, root)]
    
    idx = 0
    success = True
    
    while len(stack) > 0:
        top_sym, top_node = stack[-1]
        
        if idx < len(tokens):
            current_token = tokens[idx]
        else:
            current_token = '$'
            
        current_stack_str = " ".join([s for s, _ in stack])
        current_input_str = " ".join(tokens[idx:])
        
        if top_sym == '$' and current_token == '$':
            trace.append({
                'stack': current_stack_str,
                'input': current_input_str,
                'action': 'Accept'
            })
            break
            
        if top_sym == current_token:
            trace.append({
                'stack': current_stack_str,
                'input': current_input_str,
                'action': f"Match {current_token}"
            })
            stack.pop()
            idx += 1
        elif top_sym in grammar.terminals or top_sym == '$':
            trace.append({
                'stack': current_stack_str,
                'input': current_input_str,
                'action': f"Error: Expected '{top_sym}' missing. Synchronizing (popped)."
            })
            stack.pop()
            success = False
        elif top_sym in grammar.non_terminals:
            prods = parse_table[top_sym].get(current_token, [])
            if len(prods) == 0:
                if current_token in follow_sets.get(top_sym, set()):
                    trace.append({
                        'stack': current_stack_str,
                        'input': current_input_str,
                        'action': f"Error: No rule for {top_sym} on {current_token}. Synchronizing (popped {top_sym})."
                    })
                    stack.pop()
                else:
                    trace.append({
                        'stack': current_stack_str,
                        'input': current_input_str,
                        'action': f"Error: Unexpected '{current_token}'. Skipping."
                    })
                    idx += 1
                success = False
            elif len(prods) > 1:
                trace.append({
                    'stack': current_stack_str,
                    'input': current_input_str,
                    'action': f"Error: Conflict for {top_sym} on {current_token}. Halting."
                })
                success = False
                break
            else:
                prod = prods[0]
                action_str = f"Output {top_sym} -> {' '.join(prod)}"
                trace.append({
                    'stack': current_stack_str,
                    'input': current_input_str,
                    'action': action_str
                })
                stack.pop()
                
                children_nodes = []
                for sym in prod:
                    child = TreeNode(sym, node_counter)
                    node_counter += 1
                    children_nodes.append((sym, child))
                    if top_node:
                        top_node.children.append(child)
                        
                if prod != ['epsilon']:
                    for sym, child in reversed(children_nodes):
                        stack.append((sym, child))
        else:
            trace.append({
                'stack': current_stack_str,
                'input': current_input_str,
                'action': f"Error: Unknown symbol on stack '{top_sym}'. Halting."
            })
            success = False
            break

    return success, trace, root
