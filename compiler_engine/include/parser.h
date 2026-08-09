#ifndef PARSER_H
#define PARSER_H

#include "lexer.h"
#include <llvm/IR/Value.h>
#include <string>
#include <vector>
#include <memory>

// Base AST Node
class ExprAST {
public:
    virtual ~ExprAST() = default;
    virtual llvm::Value* codegen() = 0; // LLVM IR Create pandra function
};

// Numbers-kaga (e.g., 100)
class NumberExprAST : public ExprAST {
    int Val;
public:
    NumberExprAST(int Val) : Val(Val) {}
    llvm::Value* codegen() override;
};

// Math Operations-kaga (+, -, etc.)
class BinaryExprAST : public ExprAST {
    char Op;
    std::unique_ptr<ExprAST> LHS, RHS;
public:
    BinaryExprAST(char Op, std::unique_ptr<ExprAST> LHS, std::unique_ptr<ExprAST> RHS)
        : Op(Op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}
    llvm::Value* codegen() override;
};

// Parser Class
class Parser {
    std::vector<Token> tokens;
    size_t pos;
public:
    Parser(std::vector<Token> tokens);
    void parse(); 
};

#endif
