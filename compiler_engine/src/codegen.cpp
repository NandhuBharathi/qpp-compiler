#include "../include/codegen.h"
#include "../include/parser.h"
#include <llvm/IR/Constants.h>
#include <iostream>

std::unique_ptr<llvm::LLVMContext> TheContext;
std::unique_ptr<llvm::Module> TheModule;
std::unique_ptr<llvm::IRBuilder<>> Builder;

void InitializeLLVM() {
    TheContext = std::make_unique<llvm::LLVMContext>();
    TheModule = std::make_unique<llvm::Module>("Q++ JIT Compiler", *TheContext);
    Builder = std::make_unique<llvm::IRBuilder<>>(*TheContext);
}

// 1. Number-ah LLVM IR-ah maathurathu (e.g., 100 -> i32 100)
llvm::Value* NumberExprAST::codegen() {
    // 32-bit integer ah LLVM context-kulla create pandrom
    return llvm::ConstantInt::get(*TheContext, llvm::APInt(32, Val, true));
}

// 2. Math operation-ah LLVM IR-ah maathurathu (e.g., A + B)
llvm::Value* BinaryExprAST::codegen() {
    llvm::Value* L = LHS->codegen();
    llvm::Value* R = RHS->codegen();
    
    if (!L || !R) return nullptr;

    if (Op == '+') {
        // Builder use panni addition instruction create pandrom
        return Builder->CreateAdd(L, R, "addtmp");
    }
    
    return nullptr;
}
