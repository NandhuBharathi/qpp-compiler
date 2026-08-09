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

// 1. Oru number token-ah AST Node-ah maathurathu
std::unique_ptr<ExprAST> Parser::ParseNumberExpr() {
    // String value-ah Integer-ah convert panni Node create pandrom
    auto result = std::make_unique<NumberExprAST>(std::stoi(currentToken().value));
    getNextToken(); // Andha number-ah consume pannidrom
    return std::move(result);
}

// 2. Math expression (e.g., 500 + 400) ah AST Tree-ah maathurathu
std::unique_ptr<ExprAST> Parser::ParseExpression() {
    // First left side-la irukka number-ah edukkum
    auto LHS = ParseNumberExpr();
    if (!LHS) return nullptr;

    // Adutha token '+' ah irundha
    if (currentToken().type == TOK_PLUS) {
        getNextToken(); // '+' ah consume pannidrom
        
        // Right side-la irukka number-ah edukkum
        auto RHS = ParseNumberExpr();
        if (!RHS) return nullptr;
        
        // Rendaiyum serthu oru Binary Math Node-ah return pannum
        return std::make_unique<BinaryExprAST>('+', std::move(LHS), std::move(RHS));
    }
    
    // '+' illana verum andha number-ah mattum thiruppi tharum
    return LHS;
}
