def generate_tree_dot(root_node):
    """
    Generates a DOT language string for a Graphviz parse tree.
    This avoids needing the python graphviz package since Streamlit can render DOT strings natively.
    """
    lines = []
    lines.append('digraph ParseTree {')
    lines.append('    node [shape=ellipse, fontname="Helvetica", style="filled", fillcolor="#e1f5fe"];')
    lines.append('    edge [color="#1565c0"];')
    
    def traverse(node):
        label = node.label.replace('"', '\\"') # escape quotes
        node_id = f"node_{node.id_num}"
        
        # Style terminal/epsilon nodes differently if we want
        if label == 'epsilon':
            lines.append(f'    {node_id} [label="{label}", fillcolor="#ffcdd2", fontcolor="#c62828"];')
        else:
            lines.append(f'    {node_id} [label="{label}"];')
            
        for child in node.children:
            child_id = f"node_{child.id_num}"
            lines.append(f'    {node_id} -> {child_id};')
            traverse(child)
            
    if root_node:
        traverse(root_node)
        
    lines.append('}')
    return '\n'.join(lines)