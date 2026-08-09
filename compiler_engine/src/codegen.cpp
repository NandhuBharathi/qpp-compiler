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

// String codegen (Dummy value return pannum, aana print aagum)
llvm::Value* StringExprAST::codegen() {
    return nullptr; 
}

llvm::Value* VariableExprAST::codegen() {
    llvm::Value* V = NamedValues[Name];
    if (!V) { std::cerr << "Unknown variable name: " << Name << "\n"; return nullptr; }
    return V;
}

llvm::Value* AssignExprAST::codegen() {
    std::vector<llvm::Value*> evaluatedVals;
    for (auto& v : Vals) {
        llvm::Value* valIR = v->codegen();
        if (!valIR) return nullptr;
        evaluatedVals.push_back(valIR);
    }

    if (evaluatedVals.size() == 1) {
        for (const auto& name : Names) {
            NamedValues[name] = evaluatedVals[0];
        }
        return evaluatedVals[0]; 
    } else if (evaluatedVals.size() == Names.size()) {
        for (size_t i = 0; i < Names.size(); ++i) {
            NamedValues[Names[i]] = evaluatedVals[i];
        }
        return evaluatedVals.back();
    } else {
        std::cerr << "Syntax Error: Unmatched assignment count!\n";
        return nullptr;
    }
}

// 💥 PRINT EXPR CODEGEN: Loop through all arguments (Strings & Variables) and print them!
llvm::Value* PrintExprAST::codegen() {
    for (size_t i = 0; i < Args.size(); ++i) {
        // Oruvela adhu String-ah irundha direct-ah print pannuvom
        if (auto* strArg = dynamic_cast<StringExprAST*>(Args[i].get())) {
            std::cout << strArg->getStringVal();
        } 
        // Illana adhu Number/Variable expression-ah irukkum, athoda value-ah print pannuvom
        else {
            llvm::Value* valIR = Args[i]->codegen();
            if (valIR) {
                if (auto* constInt = llvm::dyn_cast<llvm::ConstantInt>(valIR)) {
                    std::cout << constInt->getSExtValue();
                } else {
                    valIR->print(llvm::outs());
                }
            }
        }
        // Python mari values-ku idaiyila oru space kuduppom
        if (i + 1 < Args.size()) {
            std::cout << " ";
        }
    }
    std::cout << "\n"; // End of print newline
    return nullptr;
}

llvm::Value* BinaryExprAST::codegen() {
    llvm::Value* L = LHS->codegen();
    llvm::Value* R = RHS->codegen();
    if (!L || !R) return nullptr;
    if (Op == '+') return Builder->CreateAdd(L, R, "addtmp");
    return nullptr;
}
