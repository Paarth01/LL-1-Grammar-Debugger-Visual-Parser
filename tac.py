class TACGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.code.append(instruction)

    def parse_statements(self, tokens):
        while tokens.peek() is not None and tokens.peek() != '}':
            t = tokens.peek()
            if t == 'let':
                tokens.consume() # consume 'let'
                self.parse_assignment(tokens)
            elif t == 'if':
                self.parse_if(tokens)
            elif t == 'while':
                self.parse_while(tokens)
            elif t == '{':
                tokens.consume() # consume '{'
                self.parse_statements(tokens)
                if tokens.peek() == '}':
                    tokens.consume()
            elif t == ';':
                tokens.consume() # Empty statement or stray semicolon
            elif t == 'id':
                # Could be assignment like id = Expr
                # Let's check next token
                # To peek ahead:
                saved = tokens.pos
                tokens.consume()
                if tokens.peek() == '=':
                    tokens.pos = saved
                    self.parse_assignment(tokens)
                else:
                    tokens.pos = saved
                    self.parse_expression(tokens)
                    if tokens.peek() == ';':
                        tokens.consume()
            else:
                # E.g. raw expression
                self.parse_expression(tokens)
                if tokens.peek() == ';':
                    tokens.consume()

    def parse_assignment(self, tokens):
        var_name = tokens.consume() # id
        if tokens.peek() == '=':
            tokens.consume() # '='
        expr_result = self.parse_expression(tokens)
        self.emit(f"{var_name} = {expr_result}")
        if tokens.peek() == ';':
            tokens.consume()

    def parse_if(self, tokens):
        tokens.consume() # 'if'
        if tokens.peek() == '(': tokens.consume()
        cond_res = self.parse_expression(tokens)
        if tokens.peek() == ')': tokens.consume()
        
        else_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"ifFalse {cond_res} goto {else_label}")
        
        if tokens.peek() == '{': # Block
            tokens.consume()
            self.parse_statements(tokens)
            if tokens.peek() == '}': tokens.consume()
        else:
            self.parse_statements(tokens) # single statement?
            
        self.emit(f"goto {end_label}")
        self.emit(f"{else_label}:")
        
        if tokens.peek() == 'else':
            tokens.consume()
            if tokens.peek() == '{':
                tokens.consume()
                self.parse_statements(tokens)
                if tokens.peek() == '}': tokens.consume()
            else:
                self.parse_statements(tokens)
                
        self.emit(f"{end_label}:")

    def parse_while(self, tokens):
        tokens.consume() # 'while'
        
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"{start_label}:")
        
        if tokens.peek() == '(': tokens.consume()
        cond_res = self.parse_expression(tokens)
        if tokens.peek() == ')': tokens.consume()
        
        self.emit(f"ifFalse {cond_res} goto {end_label}")
        
        if tokens.peek() == '{':
            tokens.consume()
            self.parse_statements(tokens)
            if tokens.peek() == '}': tokens.consume()
        else:
            self.parse_statements(tokens)
            
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")

    def parse_expression(self, tokens, min_precedence=0):
        # Pratt parser for precedence
        precedences = {'+': 1, '-': 1, '*': 2, '/': 2}
        
        token = tokens.consume()
        if token == '(':
            left = self.parse_expression(tokens, 0)
            if tokens.peek() == ')':
                tokens.consume()
        elif token == 'num' or token == 'id':
            left = token
        elif token == 'call':
            # handle 'call id ( args )'
            # For TAC simplicity, treat as temp
            func_name = tokens.consume() # id
            if tokens.peek() == '(': tokens.consume()
            args = []
            while tokens.peek() and tokens.peek() != ')':
                if tokens.peek() == ',': tokens.consume()
                args.append(self.parse_expression(tokens, 0))
            if tokens.peek() == ')': tokens.consume()
            for arg in args:
                self.emit(f"param {arg}")
            left = self.new_temp()
            self.emit(f"{left} = call {func_name}, {len(args)}")
        else:
            # fallback
            left = token if token else "error"
            
        while tokens.peek() in precedences and precedences[tokens.peek()] >= min_precedence:
            op = tokens.consume()
            right = self.parse_expression(tokens, precedences[op] + 1)
            temp = self.new_temp()
            self.emit(f"{temp} = {left} {op} {right}")
            left = temp
            
        return left

class TokenStream:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t not in ('$', 'epsilon')]
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        if self.pos < len(self.tokens):
            val = self.tokens[self.pos]
            self.pos += 1
            return val
        return None

def generate_tac(tokens):
    """
    Main entry point to convert a stream of tokens into Three Address Code.
    Assumes tokens have correctly parsed the syntax.
    """
    stream = TokenStream(tokens)
    generator = TACGenerator()
    try:
        generator.parse_statements(stream)
    except Exception as e:
        generator.emit(f"// TAC Generation stopped prematurely due to unrecognized structure: {e}")
    
    # If the input was just a single expression without assignment, we might not have handled it nicely in statements.
    # Actually `parse_statements` handles raw expressions properly and emits nothing or temporaries.
    # What if the whole thing is just "id + id * id"? 
    # parse_statements will loop. id -> parse_expression -> temps generated. Done.
    
    return "\n".join(generator.code)
