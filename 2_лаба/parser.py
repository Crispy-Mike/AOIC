"""Парсинг логических выражений: & (AND), | (OR), ! (NOT), -> (IMPLIES), ~ (XOR)."""

from typing import List, Optional, Set


class Token:
    VARIABLE = 'VARIABLE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    IMPLIES = 'IMPLIES'
    XOR = 'XOR'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'

    def __init__(self, token_type: str, value: str):
        self.type = token_type
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value})"


class Lexer:
    VALID_VARIABLES: Set[str] = {'a', 'b', 'c', 'd', 'e'}

    def __init__(self, text: str):
        self.text = text.replace(' ', '').replace('\t', '').replace('\n', '')
        self.pos = 0
        self.current_char: Optional[str] = self.text[0] if self.text else None

    def advance(self) -> None:
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.current_char is not None:
            if self.current_char in ' \t\n':
                self.advance()
                continue
            if self.current_char == '&':
                tokens.append(Token(Token.AND, '&'))
                self.advance()
            elif self.current_char == '|':
                tokens.append(Token(Token.OR, '|'))
                self.advance()
            elif self.current_char == '!':
                tokens.append(Token(Token.NOT, '!'))
                self.advance()
            elif self.current_char == '-' and self.peek() == '>':
                tokens.append(Token(Token.IMPLIES, '->'))
                self.advance()
                self.advance()
            elif self.current_char == '~':
                tokens.append(Token(Token.XOR, '~'))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(Token.LPAREN, '('))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(Token.RPAREN, ')'))
                self.advance()
            elif self.current_char.isalpha():
                var_name = self.current_char.lower()
                if var_name not in self.VALID_VARIABLES:
                    raise ValueError(f"Недопустимая переменная: {var_name}. "
                                   f"Разрешены: {self.VALID_VARIABLES}")
                tokens.append(Token(Token.VARIABLE, var_name))
                self.advance()
            else:
                raise ValueError(f"Недопустимый символ: {self.current_char}")
        tokens.append(Token(Token.EOF, ''))
        return tokens


class ASTNode:
    def evaluate(self, variables: dict) -> bool:
        raise NotImplementedError

    def get_variables(self) -> Set[str]:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class VariableNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, variables: dict) -> bool:
        return bool(variables.get(self.name, False))

    def get_variables(self) -> Set[str]:
        return {self.name}

    def __str__(self) -> str:
        return self.name


class NotNode(ASTNode):
    def __init__(self, operand: ASTNode):
        self.operand = operand

    def evaluate(self, variables: dict) -> bool:
        return not self.operand.evaluate(variables)

    def get_variables(self) -> Set[str]:
        return self.operand.get_variables()

    def __str__(self) -> str:
        return f"!({self.operand})"


class AndNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def evaluate(self, variables: dict) -> bool:
        return self.left.evaluate(variables) and self.right.evaluate(variables)

    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def __str__(self) -> str:
        return f"({self.left}&{self.right})"


class OrNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def evaluate(self, variables: dict) -> bool:
        return self.left.evaluate(variables) or self.right.evaluate(variables)

    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def __str__(self) -> str:
        return f"({self.left}|{self.right})"


class ImpliesNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def evaluate(self, variables: dict) -> bool:
        return (not self.left.evaluate(variables)) or self.right.evaluate(variables)

    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def __str__(self) -> str:
        return f"({self.left}->{self.right})"


class XorNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def evaluate(self, variables: dict) -> bool:
        return self.left.evaluate(variables) != self.right.evaluate(variables)

    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def __str__(self) -> str:
        return f"({self.left}~{self.right})"


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else Token(Token.EOF, '')

    def advance(self) -> None:
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else Token(Token.EOF, '')

    def parse(self) -> ASTNode:
        result = self.parse_or_expression()
        if self.current_token.type != Token.EOF:
            raise ValueError(f"Ожидался конец выражения, получено: {self.current_token}")
        return result

    def parse_or_expression(self) -> ASTNode:
        node = self.parse_xor_expression()
        while self.current_token.type == Token.OR:
            self.advance()
            node = OrNode(node, self.parse_xor_expression())
        return node

    def parse_xor_expression(self) -> ASTNode:
        node = self.parse_and_expression()
        while self.current_token.type == Token.XOR:
            self.advance()
            node = XorNode(node, self.parse_and_expression())
        return node

    def parse_and_expression(self) -> ASTNode:
        node = self.parse_implies_expression()
        while self.current_token.type == Token.AND:
            self.advance()
            node = AndNode(node, self.parse_implies_expression())
        return node

    def parse_implies_expression(self) -> ASTNode:
        node = self.parse_primary()
        while self.current_token.type == Token.IMPLIES:
            self.advance()
            node = ImpliesNode(node, self.parse_primary())
        return node

    def parse_primary(self) -> ASTNode:
        token = self.current_token
        if token.type == Token.NOT:
            self.advance()
            return NotNode(self.parse_primary())
        if token.type == Token.VARIABLE:
            self.advance()
            return VariableNode(token.value)
        if token.type == Token.LPAREN:
            self.advance()
            node = self.parse_or_expression()
            if self.current_token.type != Token.RPAREN:
                raise ValueError("Ожидалась закрывающая скобка")
            self.advance()
            return node
        raise ValueError(f"Неожиданный токен: {token}")


def parse_expression(expression: str) -> ASTNode:
    lexer = Lexer(expression)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def get_all_variables(expression: str) -> Set[str]:
    ast = parse_expression(expression)
    return ast.get_variables()
