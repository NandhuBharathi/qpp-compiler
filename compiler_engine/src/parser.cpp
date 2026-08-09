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

// Variables & Assignment Parser
std::unique_ptr<ExprAST> Parser::ParseIdentifierExpr() {
    std::string idName = currentToken().value;
    getNextToken(); // Peru padichadhum adutha token-ku povom

    // '=' illana idhu verum variable read pandrathu
    if (currentToken().type != TOK_ASSIGN) {
        return std::make_unique<VariableExprAST>(idName);
    }

    // '=' irundha, adhu Assignment expression
    getNextToken(); // '=' ah consume pandrom
    auto val = ParseExpression();
    return std::make_unique<AssignExprAST>(idName, std::move(val));
}

std::unique_ptr<ExprAST> Parser::ParseExpression() {
    std::unique_ptr<ExprAST> LHS;

    if (currentToken().type == TOK_IDENTIFIER) {
        LHS = ParseIdentifierExpr();
    } else if (currentToken().type == TOK_NUMBER) {
        LHS = ParseNumberExpr();
    } else {
        return nullptr;
    }

    if (!LHS) return nullptr;

    if (currentToken().type == TOK_PLUS) {
        getNextToken();
        auto RHS = ParseExpression();
        if (!RHS) return nullptr;
        return std::make_unique<BinaryExprAST>('+', std::move(LHS), std::move(RHS));
    }

    return LHS;
}
