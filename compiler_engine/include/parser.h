#ifndef PARSER_H
#define PARSER_H

#include "lexer.h"
#include <llvm/IR/Value.h>
#include <string>
#include <vector>
#include <memory>

class ExprAST {
public:
    virtual ~ExprAST() = default;
    virtual llvm::Value* codegen() = 0; 
};

class NumberExprAST : public ExprAST {
    int Val;
public:
    NumberExprAST(int Val) : Val(Val) {}
    llvm::Value* codegen() override;
};

class BinaryExprAST : public ExprAST {
    char Op;
    std::unique_ptr<ExprAST> LHS, RHS;
public:
    BinaryExprAST(char Op, std::unique_ptr<ExprAST> LHS, std::unique_ptr<ExprAST> RHS)
        : Op(Op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}
    llvm::Value* codegen() override;
};

class Parser {
    std::vector<Token> tokens;
    size_t pos;

    Token currentToken();
    Token getNextToken();

public:
    Parser(std::vector<Token> tokens);
    
    // Pudhusa add pandra functions (Dynamic AST building)
    std::unique_ptr<ExprAST> ParseNumberExpr();
    std::unique_ptr<ExprAST> ParseExpression();
};

#endif
