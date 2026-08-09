#include "../include/codegen.h"
#include "../include/parser.h"
#include <llvm/IR/Constants.h>
#include <iostream>

std::unique_ptr<llvm::LLVMContext> TheContext;
std::unique_ptr<llvm::Module> TheModule;
std::unique_ptr<llvm::IRBuilder<>> Builder;
std::map<std::string, llvm::Value*> NamedValues; // Define pandrom

void InitializeLLVM() {
    TheContext = std::make_unique<llvm::LLVMContext>();
    TheModule = std::make_unique<llvm::Module>("Q++ JIT Compiler", *TheContext);
    Builder = std::make_unique<llvm::IRBuilder<>>(*TheContext);
}

llvm::Value* NumberExprAST::codegen() {
    return llvm::ConstantInt::get(*TheContext, llvm::APInt(32, Val, true));
}

// Map-la irundhu Variable-ah edukkurom
llvm::Value* VariableExprAST::codegen() {
    llvm::Value* V = NamedValues[Name];
    if (!V) {
        std::cerr << "Unknown variable name: " << Name << std::endl;
        return nullptr;
    }
    return V;
}

// Map-kulla pudhu variable-ah assign pandrom
llvm::Value* AssignExprAST::codegen() {
    llvm::Value* ValIR = Val->codegen();
    if (!ValIR) return nullptr;
    
    NamedValues[Name] = ValIR; // Memory-la save aagiduchu!
    return ValIR;
}

llvm::Value* BinaryExprAST::codegen() {
    llvm::Value* L = LHS->codegen();
    llvm::Value* R = RHS->codegen();
    if (!L || !R) return nullptr;

    if (Op == '+') return Builder->CreateAdd(L, R, "addtmp");
    
    return nullptr;
}
