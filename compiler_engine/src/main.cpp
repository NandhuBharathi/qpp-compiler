#include <iostream>
#include <string>
#include "../include/lexer.h"

// Token enum-ah string-ah matha oru helper function (Output paaka easy-ah irukka)
std::string getTokenName(TokenType type) {
    switch(type) {
        case TOK_FUNC: return "FUNC";
        case TOK_RETURN: return "RETURN";
        case TOK_IF: return "IF";
        case TOK_ELSE: return "ELSE";
        case TOK_IDENTIFIER: return "IDENTIFIER";
        case TOK_NUMBER: return "NUMBER";
        case TOK_LBRACE: return "LBRACE";
        case TOK_RBRACE: return "RBRACE";
        case TOK_LPAREN: return "LPAREN";
        case TOK_RPAREN: return "RPAREN";
        case TOK_ASSIGN: return "ASSIGN";
        case TOK_PLUS: return "PLUS";
        case TOK_GREATER: return "GREATER";
        case TOK_EOF: return "EOF";
        default: return "UNKNOWN";
    }
}

int main(int argc, char* argv[]) {
    // Command line-la code pass panna adhai edukkum, illana default Q++ code-ah edukkum
    std::string code = "";
    if (argc > 1) {
        code = argv[1];
    } else {
        code = "func calculate_total(price) { return price + 100 }";
    }

    std::cout << "--- Q++ Compiler Engine ---" << std::endl;
    std::cout << "Input Code: " << code << std::endl;
    std::cout << "Generated Tokens:" << std::endl;

    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();

    for (const auto& token : tokens) {
        std::cout << "[" << getTokenName(token.type) << " : " << token.value << "]" << std::endl;
    }

    return 0;
}
