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
    // Indha function dhaan output print aaganuma vendama nu mudivu pannum
    virtual bool isSilent() const { return false; } 
};

class NumberExprAST : public ExprAST {
    int Val;
public:
    NumberExprAST(int Val) : Val(Val) {}
    llvm::Value* codegen() override;
};

class VariableExprAST : public ExprAST {
    std::string Name;
public:
    VariableExprAST(std::string Name) : Name(Name) {}
    llvm::Value* codegen() override;
};

class AssignExprAST : public ExprAST {
    std::string Name;
    std::unique_ptr<ExprAST> Val;
public:
    AssignExprAST(std::string Name, std::unique_ptr<ExprAST> Val)
        : Name(Name), Val(std::move(Val)) {}
    llvm::Value* codegen() override;
    
    // Assignment eppovum SILENT ah dhaan irukkanum!
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

// Pudhusa Print expression
class PrintExprAST : public ExprAST {
    std::unique_ptr<ExprAST> Arg;
public:
    PrintExprAST(std::unique_ptr<ExprAST> Arg) : Arg(std::move(Arg)) {}
    llvm::Value* codegen() override;
};

class Parser {
    std::vector<Token> tokens;
    size_t pos;

public:
    Token currentToken();
    Token getNextToken();

    Parser(std::vector<Token> tokens);
    
    std::unique_ptr<ExprAST> ParseNumberExpr();
    std::unique_ptr<ExprAST> ParseIdentifierExpr();
    std::unique_ptr<ExprAST> ParsePrintExpr(); // Print parser
    std::unique_ptr<ExprAST> ParseExpression();
};

#endif
