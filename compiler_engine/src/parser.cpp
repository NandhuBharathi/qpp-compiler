#include "../include/parser.h"
#include <iostream>

Parser::Parser(std::vector<Token> tokens) : tokens(tokens), pos(0) {}

Token Parser::currentToken() {
    if (pos < tokens.size()) return tokens[pos];
    return {TOK_EOF, ""};
}

Token Parser::getNextToken() {
    if (pos < tokens.size()) pos++;
    return currentToken();
}

void Parser::parse() {
    std::cout << "\n--- Parser Started: Building AST ---" << std::endl;
    
    while (currentToken().type != TOK_EOF) {
        Token tok = currentToken();
        
        // Basic Syntax Logic Check (Sample)
        if (tok.type == TOK_FUNC) {
            std::cout << "[AST Node] -> Function Declaration Found" << std::endl;
        } 
        else if (tok.type == TOK_RETURN) {
            std::cout << "[AST Node] -> Return Statement Found" << std::endl;
        }
        else if (tok.type == TOK_NUMBER) {
            std::cout << "[AST Node] -> Number Expr: " << tok.value << std::endl;
        }
        else if (tok.type == TOK_IDENTIFIER) {
            std::cout << "[AST Node] -> Variable/Identifier Expr: " << tok.value << std::endl;
        }
        else if (tok.type == TOK_PLUS || tok.type == TOK_ASSIGN) {
            std::cout << "[AST Node] -> Binary Operation: " << tok.value << std::endl;
        }
        
        getNextToken();
    }
    
    std::cout << "--- Parsing Completed Successfully! ---" << std::endl;
}
