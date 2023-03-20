import plang
import sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        plang.runFile(sys.argv[1])
    else:
        plang.repl()