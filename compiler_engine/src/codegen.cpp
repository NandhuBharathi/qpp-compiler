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

// 💥 STRING INTERPOLATION ENGINE: Replaces {var} with actual variable values!
void printInterpolatedString(const std::string& str) {
    size_t i = 0;
    while (i < str.length()) {
        if (str[i] == '{') {
            size_t endIdx = str.find('}', i);
            if (endIdx != std::string::npos) {
                std::string varName = str.substr(i + 1, endIdx - i - 1);
                // Look up in NamedValues memory map
                llvm::Value* V = NamedValues[varName];
                if (V) {
                    if (auto* constInt = llvm::dyn_cast<llvm::ConstantInt>(V)) {
                        std::cout << constInt->getSExtValue();
                    } else {
                        std::cout << "0";
                    }
                } else {
                    std::cout << "{Undefined:" << varName << "}";
                }
                i = endIdx + 1;
                continue;
            }
        }
        std::cout << str[i];
        i++;
    }
}

llvm::Value* PrintExprAST::codegen() {
    for (size_t i = 0; i < Args.size(); ++i) {
        if (auto* strArg = dynamic_cast<StringExprAST*>(Args[i].get())) {
            if (strArg->isTemplate()) {
                // If prefixed with '!', parse and inject variables!
                printInterpolatedString(strArg->getStringVal());
            } else {
                std::cout << strArg->getStringVal();
            }
        } else {
            llvm::Value* valIR = Args[i]->codegen();
            if (valIR) {
                if (auto* constInt = llvm::dyn_cast<llvm::ConstantInt>(valIR)) {
                    std::cout << constInt->getSExtValue();
                } else {
                    valIR->print(llvm::outs());
                }
            }
        }
        if (i + 1 < Args.size()) {
            std::cout << " ";
        }
    }
    std::cout << "\n";
    return nullptr;
}

llvm::Value* BinaryExprAST::codegen() {
    llvm::Value* L = LHS->codegen();
    llvm::Value* R = RHS->codegen();
    if (!L || !R) return nullptr;
    if (Op == '+') return Builder->CreateAdd(L, R, "addtmp");
    return nullptr;
}
