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

std::unique_ptr<ExprAST> Parser::ParseIdentifierExpr() {
    std::string idName = currentToken().value;
    
    bool isAssign = false;
    for (size_t i = pos; i < tokens.size(); i++) {
        if (tokens[i].type == TOK_ASSIGN) { isAssign = true; break; }
        if (tokens[i].type != TOK_IDENTIFIER && tokens[i].type != TOK_COMMA) break; 
    }

    getNextToken(); 

    if (!isAssign) {
        return std::make_unique<VariableExprAST>(idName);
    }

    std::vector<std::string> names;
    names.push_back(idName);

    while (currentToken().type == TOK_COMMA) {
        getNextToken(); names.push_back(currentToken().value); getNextToken();
    }

    getNextToken(); 

    std::vector<std::unique_ptr<ExprAST>> vals;
    vals.push_back(ParseExpression());

    while (currentToken().type == TOK_COMMA) {
        getNextToken(); vals.push_back(ParseExpression());
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

// 💥 OVERWRITTEN INPUT FUNCTION
std::unique_ptr<ExprAST> Parser::ParseInputExpr() {
    getNextToken(); // Consume 'input'
    
    if (currentToken().type != TOK_LPAREN) return nullptr;
    getNextToken(); // Consume '('
    
    // DEFAULT PROMPT
    std::string promptMessage = ">>> Enter value: ";

    // Ulla String irundha, adhai namma promptMessage-ah mathikirom!
    if (currentToken().type == TOK_STRING) {
        promptMessage = currentToken().value; // User kudutha string-ah edukkirom
        getNextToken(); // String token-ah consume pandrom
    }
    
    if (currentToken().type != TOK_RPAREN) return nullptr;
    getNextToken(); // Consume ')'

    int userValue = 0;
    std::cout << promptMessage; // Dynamically print custom or default prompt
    std::cout.flush(); 
    std::cin >> userValue;

    return std::make_unique<NumberExprAST>(userValue);
}

std::unique_ptr<ExprAST> Parser::ParseExpression() {
    std::unique_ptr<ExprAST> LHS;

    if (currentToken().type == TOK_PRINT) { LHS = ParsePrintExpr(); }
    else if (currentToken().type == TOK_INPUT) { LHS = ParseInputExpr(); } 
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
