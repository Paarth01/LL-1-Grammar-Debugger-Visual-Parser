import re
from lexer import tokenize
class Grammar:
    def __init__(self, start_symbol=None):
        self.rules = {}  # dict of NonTerminal -> list of lists of symbols. e.g. {'E': [['E', '+', 'T'], ['T']]}
        self.start_symbol = start_symbol
        self.non_terminals = set()
        self.terminals = set()

    def parse_from_string(self, text):
        """Parses a grammar from a multi-line string. Each line should be like 'E -> E + T | T'"""
        self.rules = {}
        self.non_terminals = set()
        self.start_symbol = None
        
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if '->' not in line:
                raise ValueError(f"Invalid production rule format (missing '->'): {line}")
            
            lhs, rhs_str = line.split('->', 1)
            lhs = lhs.strip()
            self.non_terminals.add(lhs)
            
            if not self.start_symbol:
                self.start_symbol = lhs
                
            if lhs not in self.rules:
                self.rules[lhs] = []
                
            for prod in rhs_str.split('|'):
                # Try auto-tokenization to split symbols like E+T into E, +, T
                tokens = tokenize(prod.strip(), use_lexer=True)
                if not tokens:
                    tokens = ['epsilon']
                self.rules[lhs].append(tokens)
                
                
        # Make sure all LHS keys exist in non_terminals
        for nt in self.rules.keys():
            self.non_terminals.add(nt)
            
        self.compute_terminals()

    def compute_terminals(self):
        """Extracts terminals by looking at all symbols in RHS that are not in LHS"""
        self.terminals = set()
        for lhs, prods in self.rules.items():
            for prod in prods:
                for sym in prod:
                    if sym not in self.non_terminals and sym != 'epsilon':
                        self.terminals.add(sym)

    def display(self):
        """Returns string representation of the grammar for UI display"""
        output = []
        for lhs, prods in self.rules.items():
            rhs = ' | '.join([' '.join(prod) for prod in prods])
            output.append(f"{lhs} -> {rhs}")
        return '\n'.join(output)
