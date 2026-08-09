#include <iostream>
#include <string>
#include "../include/lexer.h"
#include "../include/parser.h"

int main(int argc, char* argv[]) {
    std::string code = "";
    if (argc > 1) {
        code = argv[1];
    } else {
        code = "func calculate_total(price) { return price + 100 }";
    }

    std::cout << "Q++ Engine Output:\n" << std::endl;

    // 1. Lexical Analysis (Tokens)
    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();
    std::cout << "Lexer identified " << tokens.size() << " tokens." << std::endl;

    // 2. Syntax Analysis (AST Generation)
    Parser parser(tokens);
    parser.parse();

    return 0;
}
