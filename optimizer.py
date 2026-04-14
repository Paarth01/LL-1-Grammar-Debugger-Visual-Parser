import re

def optimize_tac(tac_code_string):
    """
    Performs basic local optimizations on the Three Address Code:
    - Algebraic Simplifications (e.g., x + 0 -> x)
    - Constant Folding (e.g., 3 + 4 -> 7)
    """
    if not tac_code_string:
        return ""
        
    instructions = tac_code_string.split('\n')
    optimized = []
    
    for inst in instructions:
        if not inst.strip() or inst.startswith('//'):
            optimized.append(inst)
            continue
            
        # Match binary operations: res = left op right
        m_bin = re.match(r'^(\w+)\s*=\s*(\w+)\s*([\+\-\*/])\s*(\w+)$', inst)
        if m_bin:
            res_var, left, op, right = m_bin.groups()
            
            # Algebraic simplifications
            if op == '+' and right == '0':
                optimized.append(f"{res_var} = {left}")
                continue
            if op == '+' and left == '0':
                optimized.append(f"{res_var} = {right}")
                continue
            if op == '*' and right == '1':
                optimized.append(f"{res_var} = {left}")
                continue
            if op == '*' and left == '1':
                optimized.append(f"{res_var} = {right}")
                continue
            if op == '*' and (right == '0' or left == '0'):
                optimized.append(f"{res_var} = 0")
                continue
                
            # Constant folding
            if left.isdigit() and right.isdigit():
                v_left = int(left)
                v_right = int(right)
                try:
                    if op == '+': res = v_left + v_right
                    elif op == '-': res = v_left - v_right
                    elif op == '*': res = v_left * v_right
                    elif op == '/': res = v_left // v_right
                    optimized.append(f"{res_var} = {res}")
                    continue
                except ZeroDivisionError:
                    pass

        # If no optimization applies, preserve instruction
        optimized.append(inst)
        
    return "\n".join(optimized)
