############################
# Constants
############################

WHITESPACES     = " \n\t"

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

    def getTokens(self) -> list[Token]:
        tokens = []

        while not self.isEnd():
            self.prevPos = self.curPos.copy()   # Store the previous token

            if self.peek() in WHITESPACES:
                self.advance()
            elif self.peek() == "+":
                self.advance()
                tokens.append(Token(TT_PLUS, "+", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "-":
                self.advance()
                tokens.append(Token(TT_MINUS, "-", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "*":
                self.advance()
                tokens.append(Token(TT_MULTIPLY, "*", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "/":
                self.advance()
                tokens.append(Token(TT_DIVIDE, "/", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == "(":
                self.advance()
                tokens.append(Token(TT_LPAREN, "(", self.prevPos.copy(), self.curPos.copy()))
            elif self.peek() == ")":
                self.advance()
                tokens.append(Token(TT_RPAREN, ")", self.prevPos.copy(), self.curPos.copy()))
            else:
                illegalChar = self.peek()
                self.advance()
                return None, IllegalCharError(f"character '{illegalChar}' is unexpected.", 
                                              self.prevPos.copy(), 
                                              self.curPos.copy())
            
        return tokens, None
    
############################
# pLang Functionality
############################

def run(srcText: str) -> None:
    """
    run a given srcText
    """
    lexer = Lexer("<stdin>", srcText)
    tokens, errors = lexer.getTokens()
    
    if errors: print(errors)
    else: print(tokens)

def repl() -> None:
    """
    Read-Evaluate-Print-Loop
    """
    while True:
        srcText = input("pLang> ")
        run(srcText)

def runFile(fpath: str) -> None:
    """
    run the file with the given fpath
    """
    srcText = ""
    with open(fpath) as f:
        srcText = f.read()
    
    lexer = Lexer(fpath, srcText)
    tokens, errors = lexer.getTokens()

    if errors: print(errors)
    else: print(tokens)