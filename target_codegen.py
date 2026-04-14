import re

def generate_assembly(tac_string):
    """
    Converts optimized TAC into generic pseudo-assembly instructions
    usable for educational purposes (simulates MIPS/x86 logic).
    """
    if not tac_string:
        return ""
        
    instructions = tac_string.split('\n')
    asm = []
    
    # Generic register set
    registers = ['R1', 'R2', 'R3', 'R4', 'R5']
    reg_idx = 0
    var_to_reg = {}
    
    def get_reg(var):
        nonlocal reg_idx
        if var in var_to_reg:
            return var_to_reg[var]
            
        r = registers[reg_idx]
        var_to_reg[var] = r
        reg_idx = (reg_idx + 1) % len(registers)
        return r

    for inst in instructions:
        if not inst.strip() or inst.startswith('//'):
            asm.append(inst)
            continue
            
        # Labels for loops/branches
        if inst.endswith(':'):
            asm.append(inst)
            continue
            
        # Unconditional Jump
        if inst.startswith('goto '):
            lbl = inst.split(' ')[1]
            asm.append(f"    JMP {lbl}")
            continue
            
        # Conditional Jump
        m_if = re.match(r'^ifFalse\s+(\w+)\s+goto\s+(\w+)$', inst)
        if m_if:
            cond_var, lbl = m_if.groups()
            r = get_reg(cond_var)
            if not cond_var.isdigit():
                asm.append(f"    LOAD {r}, {cond_var}")
            else:
                asm.append(f"    MOVI {r}, {cond_var}")
            asm.append(f"    CJMP_FALSE {r}, {lbl}")
            continue
            
        # Binary Operation
        m_bin = re.match(r'^(\w+)\s*=\s*(\w+)\s*([\+\-\*/])\s*(\w+)$', inst)
        if m_bin:
            res_var, left, op, right = m_bin.groups()
            op_map = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
            
            rl = get_reg(left)
            if not left.isdigit(): asm.append(f"    LOAD {rl}, {left}")
            else: asm.append(f"    MOVI {rl}, {left}")
            
            rr = get_reg(right)
            if not right.isdigit(): asm.append(f"    LOAD {rr}, {right}")
            else: asm.append(f"    MOVI {rr}, {right}")
            
            res_r = get_reg(res_var)
            asm.append(f"    {op_map[op]} {res_r}, {rl}, {rr}")
            asm.append(f"    STORE {res_var}, {res_r}")
            continue
            
        # Single variable assignment
        m_assign = re.match(r'^(\w+)\s*=\s*(\w+)$', inst)
        if m_assign:
            res_var, val = m_assign.groups()
            r = get_reg(val)
            if not val.isdigit(): asm.append(f"    LOAD {r}, {val}")
            else: asm.append(f"    MOVI {r}, {val}")
            
            res_r = get_reg(res_var)
            asm.append(f"    MOV {res_r}, {r}")
            asm.append(f"    STORE {res_var}, {res_r}")
            continue
            
    return "\n".join(asm)
