#ifndef PARSER_H
#define PARSER_H

#include "lexer.h"
#include <string>
#include <vector>
#include <memory>

// Base AST Node Class
class ExprAST {
public:
    virtual ~ExprAST() = default;
};

// Numbers-kaga (e.g., 100, 200)
class NumberExprAST : public ExprAST {
    std::string Val;
public:
    NumberExprAST(std::string Val) : Val(Val) {}
};

// Variables-kaga (e.g., price, tax)
class VariableExprAST : public ExprAST {
    std::string Name;
public:
    VariableExprAST(std::string Name) : Name(Name) {}
};

// Math Operations-kaga (+, -, =, >)
class BinaryExprAST : public ExprAST {
    std::string Op;
    std::unique_ptr<ExprAST> LHS, RHS; // Left and Right hand sides
public:
    BinaryExprAST(std::string Op, std::unique_ptr<ExprAST> LHS, std::unique_ptr<ExprAST> RHS)
        : Op(Op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}
};

// Parser Class
class Parser {
    std::vector<Token> tokens;
    size_t pos;
    
    Token currentToken();
    Token getNextToken();

public:
    Parser(std::vector<Token> tokens);
    void parse(); // Ippo test pandrathukaga basic function
};

#endif
