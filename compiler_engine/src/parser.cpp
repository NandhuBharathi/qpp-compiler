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

std::unique_ptr<ExprAST> Parser::ParseNumberExpr() {
    auto result = std::make_unique<NumberExprAST>(std::stoi(currentToken().value));
    getNextToken();
    return std::move(result);
}

// MULTI-ASSIGNMENT PARSING LOGIC
std::unique_ptr<ExprAST> Parser::ParseIdentifierExpr() {
    std::vector<std::string> names;
    
    // 1. Variable names-ah padikkirom
    names.push_back(currentToken().value);
    getNextToken();

    // Comma irundha adutha adutha variables-ah list-la podurom (a, b, c)
    while (currentToken().type == TOK_COMMA) {
        getNextToken(); // Consume ','
        names.push_back(currentToken().value);
        getNextToken(); // Consume variable name
    }

    // '=' illana idhu verum read operation (e.g., a)
    if (currentToken().type != TOK_ASSIGN) {
        return std::make_unique<VariableExprAST>(names[0]);
    }

    getNextToken(); // Consume '='

    // 2. Values-ah padikkirom
    std::vector<std::unique_ptr<ExprAST>> vals;
    vals.push_back(ParseExpression());

    // Comma irundha adutha adutha values-ah list-la podurom (10, 20, 30)
    while (currentToken().type == TOK_COMMA) {
        getNextToken(); // Consume ','
        vals.push_back(ParseExpression());
    }

    return std::make_unique<AssignExprAST>(names, std::move(vals));
}

std::unique_ptr<ExprAST> Parser::ParsePrintExpr() {
    getNextToken(); 
    if (currentToken().type != TOK_LPAREN) return nullptr;
    getNextToken(); 
    
    auto Arg = ParseExpression();
    if (!Arg) return nullptr;
    
    if (currentToken().type != TOK_RPAREN) return nullptr;
    getNextToken(); 
    
    return std::make_unique<PrintExprAST>(std::move(Arg));
}

std::unique_ptr<ExprAST> Parser::ParseExpression() {
    std::unique_ptr<ExprAST> LHS;

    if (currentToken().type == TOK_PRINT) { LHS = ParsePrintExpr(); } 
    else if (currentToken().type == TOK_IDENTIFIER) { LHS = ParseIdentifierExpr(); } 
    else if (currentToken().type == TOK_NUMBER) { LHS = ParseNumberExpr(); } 
    else { return nullptr; }

    if (!LHS) return nullptr;

    if (currentToken().type == TOK_PLUS) {
        getNextToken();
        auto RHS = ParseExpression();
        if (!RHS) return nullptr;
        return std::make_unique<BinaryExprAST>('+', std::move(LHS), std::move(RHS));
    }

    return LHS;
}
