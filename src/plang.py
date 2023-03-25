############################
# Constants
############################

WHITESPACES     = " \n\t"
DIGITS          = "1234567890"

############################
# Position
############################

class Position:
    def __init__(self, filename: str, srcText: str, idx: int, ln: int, col: int) -> None:
        self.filename = filename    # filename
        self.srcText = srcText      # source text in file with filename
        self.idx = idx              # index 
        self.ln = ln                # line number
        self.col = col              # column number

    def advance(self, currentChar: str):
        """
        increment the position, while checking if the currentChar is a newline
        @params
            currentChar     str     change position, if currentChar is newline then increase line number
        @returns
            Position
        """
        self.idx += 1
        self.col += 1

        # if newline then reset the col to 1 and increase line number by 1
        if currentChar == "\n":
            self.ln += 1
            self.col = 1
        return self
    
    def copy(self):
        return Position(self.filename, self.srcText, self.idx, self.ln, self.col)

    def __repr__(self) -> str:
        return f"[{self.idx}:{self.ln}:{self.col}]"

############################
# Errors
############################

class Error:
    def __init__(self, errName: str, errDetails: str, startPos: Position, endPos: Position) -> None:
        self.errName = errName          # Error Name
        self.errDetails = errDetails    # Error Details
        self.startPos = startPos        # Start Position of the Error
        self.endPos = endPos            # End Position of the Error

    def __repr__(self) -> str:
        res = ""
        res += f"{self.errName}: {self.errDetails}"
        return res

class IllegalCharError(Error):
    def __init__(self, errDetails: str, startPos: Position, endPos: Position) -> None:
        super().__init__("IllegalCharError", errDetails, startPos, endPos)

class SyntaxError(Error):
    def __init__(self, errDetails: str, startPos: Position, endPos: Position) -> None:
        super().__init__("SyntaxError", errDetails, startPos, endPos)

############################
# Tokens
############################

TT_INT      = "INT"
TT_PLUS     = "PLUS"
TT_MINUS    = "MINUS"
TT_MULTIPLY = "MULTIPLY"
TT_DIVIDE   = "DIVIDE"
TT_LPAREN   = "LPAREN"
TT_RPAREN   = "RPAREN"
TT_EOF      = "EOF"

class Token:
    def __init__(self, type: str, lexical: str, startPos: Position, endPos: Position) -> None:
        self.type = type
        self.lexical = lexical
        self.startPos = startPos
        self.endPos = endPos

    def __repr__(self) -> str:
        return f"{self.type}:{self.lexical}:{self.startPos}:{self.endPos}"

############################
# Lexer
############################

class Lexer:
    def __init__(self, filename: str, srcText: str) -> None:
        self.srcText = srcText                              # source text
        self.curPos = Position(filename, srcText, 0, 1, 1)  # current position in the srcText
        self.prevPos = Position(filename, srcText, 0, 1, 1) # Previous position in the srcText

    # Helper functions

    def isEnd(self) -> bool:
        """
        Check if the current position index is out-of-bound of the srcText
        @returns
            True if outofbound, otherwise False
        """
        return self.curPos.idx >= len(self.srcText)
    
    def peek(self) -> str:
        """
        Peek at the current position index
        @return
            empty string if isEnd() is true otherwise returns string at current index
        """
        if self.isEnd(): return ""
        return self.srcText[self.curPos.idx]
    
    def advance(self) -> None:
        if self.isEnd(): return
        self.curPos.advance(self.peek())

    def getInt(self) -> None:
        lexical = ""
        
        while not self.isEnd() and self.peek() in DIGITS:
            lexical += self.peek()
            self.advance()

        self.tokens.append(Token(TT_INT, lexical, self.prevPos.copy(), self.curPos.copy()))

    # Main function

    def getTokens(self) -> list[Token, Error]:
        self.tokens = []

        while not self.isEnd():
            self.prevPos = self.curPos.copy()   # Store the previous token

            if self.peek() in WHITESPACES:
                self.advance()
            elif self.peek() in DIGITS:
                self.getInt()
            elif self.peek() == "+":
                self.advance()
                self.tokens.append(Token(TT_PLUS, "+", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "-":
                self.advance()
                self.tokens.append(Token(TT_MINUS, "-", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "*":
                self.advance()
                self.tokens.append(Token(TT_MULTIPLY, "*", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "/":
                self.advance()
                self.tokens.append(Token(TT_DIVIDE, "/", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "(":
                self.advance()
                self.tokens.append(Token(TT_LPAREN, "(", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == ")":
                self.advance()
                self.tokens.append(Token(TT_RPAREN, ")", self.prevPos.copy(), self.curPos.copy()))
            else:
                illegalChar = self.peek()
                self.advance()
                return None, IllegalCharError(f"character '{illegalChar}' is unexpected.", 
                                              self.prevPos.copy(), 
                                              self.curPos.copy())
            
        self.tokens.append(Token(TT_EOF, "", self.curPos.copy(), self.curPos.copy())) # Add an EOF token at end
        return self.tokens, None

############################
# Ast Nodes
############################

class AstNode:
    def __init__(self, startPos: Position, endPos: Position) -> None:
        self.startPos = startPos
        self.endPos = endPos

class LiteralNode(AstNode):
    def __init__(self, literal: Token) -> None:
        super().__init__(literal.startPos, literal.endPos)
        self.literal = literal

    def __repr__(self) -> str:
        return f"{self.literal.lexical}"

class BinaryNode(AstNode):
    def __init__(self, left: AstNode, op: Token, right: AstNode) -> None:
        super().__init__(left.startPos, right.endPos)
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} {self.op.lexical} {self.right})"

############################
# Parser
############################

class Parser:
    def __init__(self, filename: str, srcText: str, tokens: list[Token]) -> None:
        self.filename = filename
        self.srcText = srcText
        self.tokens = tokens
        self.idx = 0

    # Helper functions

    def isEnd(self) -> bool:
        return self.idx >= len(self.tokens)
    
    def peek(self) -> Token:
        if self.isEnd() or self.tokens[self.idx].type == TT_EOF:
            return self.tokens[-1]
        return self.tokens[self.idx]
    
    def advance(self) -> Token:
        if self.isEnd(): return
        res = self.peek()
        self.idx += 1
        return res

    # Grammar

    def term(self) -> tuple[BinaryNode, Error]:
        left, error = self.factor()
        if error: return None, error

        while self.peek().type in [TT_PLUS, TT_MINUS]:
            op = self.advance()
            right, error = self.factor()
            if error: return None, error
            left = BinaryNode(left, op, right)

        return left, None

    def factor(self) -> tuple[BinaryNode, Error]:
        left, error = self.primary()
        if error: return None, error

        while self.peek().type in [TT_MULTIPLY, TT_DIVIDE]:
            op = self.advance()
            right, error = self.primary()
            if error: return None, error
            left = BinaryNode(left, op, right)

        return left, None

    def primary(self) -> tuple[LiteralNode, Error]:
        if self.peek().type == TT_INT:
            return LiteralNode(self.advance()), None
        return None, SyntaxError("Expected a primary", self.peek().startPos, self.peek().endPos)
    
    # Main function

    def parse(self) -> tuple[AstNode, Error]:
        ast, error = self.term()

############################
# pLang Functionality
############################

def run(filename, srcText: str) -> None:
    """
    run a given srcText
    """
    lexer = Lexer(filename, srcText)
    tokens, error = lexer.getTokens()
    
    if error: 
        print(error)
        return
    else: print(tokens)

    parser = Parser(filename, srcText, tokens)
    ast, error = parser.parse()

    if error: print(error)
    else: print(ast)

def repl() -> None:
    """
    Read-Evaluate-Print-Loop
    """
    try:
        while True:
            srcText = input("pLang> ")
            run("<stdin>", srcText)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        exit(1)
    except EOFError:
        exit(2)

def runFile(fpath: str) -> None:
    """
    run the file with the given fpath
    """
    srcText = ""
    with open(fpath) as f:
        srcText = f.read()
    
    run(fpath, srcText)