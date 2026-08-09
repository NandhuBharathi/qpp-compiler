#include "../include/codegen.h"
#include "../include/parser.h"
#include <llvm/IR/Constants.h>
#include <iostream>

std::unique_ptr<llvm::LLVMContext> TheContext;
std::unique_ptr<llvm::Module> TheModule;
std::unique_ptr<llvm::IRBuilder<>> Builder;
std::map<std::string, llvm::Value*> NamedValues;

void InitializeLLVM() {
    TheContext = std::make_unique<llvm::LLVMContext>();
    TheModule = std::make_unique<llvm::Module>("Q++ JIT Compiler", *TheContext);
    Builder = std::make_unique<llvm::IRBuilder<>>(*TheContext);
}

llvm::Value* NumberExprAST::codegen() {
    return llvm::ConstantInt::get(*TheContext, llvm::APInt(32, Val, true));
}

llvm::Value* VariableExprAST::codegen() {
    llvm::Value* V = NamedValues[Name];
    if (!V) { std::cerr << "Unknown variable name: " << Name << "\n"; return nullptr; }
    return V;
}

// MULTI-ASSIGNMENT LLVM LOGIC
llvm::Value* AssignExprAST::codegen() {
    std::vector<llvm::Value*> evaluatedVals;
    
    // 1. First ella values-aiyum run panni memory-la edukkiriom
    for (auto& v : Vals) {
        llvm::Value* valIR = v->codegen();
        if (!valIR) return nullptr;
        evaluatedVals.push_back(valIR);
    }

    // Rule 1: a, b, c = 10 (Single value to all)
    if (evaluatedVals.size() == 1) {
        for (const auto& name : Names) {
            NamedValues[name] = evaluatedVals[0];
        }
        return evaluatedVals[0]; 
    } 
    // Rule 2: a, b, c = 10, 20, 30 (Value matches Variable Count)
    else if (evaluatedVals.size() == Names.size()) {
        for (size_t i = 0; i < Names.size(); ++i) {
            NamedValues[Names[i]] = evaluatedVals[i];
        }
        return evaluatedVals.back();
    } 
    // Error Scenario!
    else {
        std::cerr << "Syntax Error: Unmatched assignment count!\n";
        return nullptr;
    }
}

llvm::Value* PrintExprAST::codegen() {
    return Arg->codegen();
}

llvm::Value* BinaryExprAST::codegen() {
    llvm::Value* L = LHS->codegen();
    llvm::Value* R = RHS->codegen();
    if (!L || !R) return nullptr;
    if (Op == '+') return Builder->CreateAdd(L, R, "addtmp");
    return nullptr;
}
