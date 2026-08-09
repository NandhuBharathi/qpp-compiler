#include <iostream>
#include <string>
#include <llvm/IR/Constants.h>
#include "../include/lexer.h"
#include "../include/parser.h"
#include "../include/codegen.h"

int main(int argc, char* argv[]) {
    // Variable assignment test pandrom
    std::string code = "";
    if (argc > 1) {
        code = argv[1];
    } else {
        code = "score = 500 + 300"; 
    }

    InitializeLLVM();
    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();
    Parser parser(tokens);
    auto astTree = parser.ParseExpression();

    if (astTree) {
        llvm::Value* irValue = astTree->codegen();
        if (irValue) {
            if (auto* constInt = llvm::dyn_cast<llvm::ConstantInt>(irValue)) {
                std::cout << constInt->getSExtValue() << "\n";
            } else {
                irValue->print(llvm::outs());
                std::cout << "\n";
            }
        }
    } else {
        std::cout << "Error: Could not parse the expression.\n";
    }

    return 0;
}
