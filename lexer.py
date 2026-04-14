import re

def tokenize(input_string, use_lexer=True):
    """
    Tokenizes the input string.
    If use_lexer is True, it uses a generic regex to split identifiers, numbers, 
    multi-character operators, and symbols.
    If use_lexer is False, it falls back to strict space-separated splitting.
    """
    if not use_lexer:
        return input_string.strip().split()
        
    # Matches:
    # 1. Common multi-character operators (==, <=, >=, !=, &&, ||, ->, =>)
    # 2. Words (identifiers, keywords, supporting optional trailing apostrophes like E')
    # 3. Numbers (digits with optional decimals)
    # 4. Individual non-whitespace characters (symbols like +, -, *, /, (, ))
    pattern = r"==|<=|>=|!=|&&|\|\||->|=>|[a-zA-Z_]\w*\'*|\d+(?:\.\d+)?|[^\w\s]"
    
    tokens = [match.group(0) for match in re.finditer(pattern, input_string)]
    return tokens