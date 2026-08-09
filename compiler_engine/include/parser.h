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
    virtual bool isSilent() const { return false; } 
};

class NumberExprAST : public ExprAST {
    int Val;
public:
    NumberExprAST(int Val) : Val(Val) {}
    llvm::Value* codegen() override;
};

// Pudhusa String-ah handle panna AST Node!
class StringExprAST : public ExprAST {
    std::string Val;
public:
    StringExprAST(std::string Val) : Val(Val) {}
    llvm::Value* codegen() override;
    std::string getStringVal() const { return Val; }
};

class VariableExprAST : public ExprAST {
    std::string Name;
public:
    VariableExprAST(std::string Name) : Name(Name) {}
    llvm::Value* codegen() override;
};

class AssignExprAST : public ExprAST {
    std::vector<std::string> Names;
    std::vector<std::unique_ptr<ExprAST>> Vals;
public:
    AssignExprAST(std::vector<std::string> Names, std::vector<std::unique_ptr<ExprAST>> Vals)
        : Names(Names), Vals(std::move(Vals)) {}
    llvm::Value* codegen() override;
    bool isSilent() const override { return true; } 
};

class BinaryExprAST : public ExprAST {
    char Op;
    std::unique_ptr<ExprAST> LHS, RHS;
public:
    BinaryExprAST(char Op, std::unique_ptr<ExprAST> LHS, std::unique_ptr<ExprAST> RHS)
        : Op(Op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}
    llvm::Value* codegen() override;
};

// Print can now accept multiple arguments separated by commas!
class PrintExprAST : public ExprAST {
    std::vector<std::unique_ptr<ExprAST>> Args;
public:
    PrintExprAST(std::vector<std::unique_ptr<ExprAST>> Args) : Args(std::move(Args)) {}
    llvm::Value* codegen() override;
};

class Parser {
    std::vector<Token> tokens;
    size_t pos;

public: 
    Parser(std::vector<Token> tokens);
    
    Token currentToken();
    Token getNextToken();

    std::unique_ptr<ExprAST> ParseNumberExpr();
    std::unique_ptr<ExprAST> ParseStringExpr(); // String parser
    std::unique_ptr<ExprAST> ParseIdentifierExpr();
    std::unique_ptr<ExprAST> ParsePrintExpr();
    std::unique_ptr<ExprAST> ParseInputExpr();
    std::unique_ptr<ExprAST> ParseExpression();
};

#endif
