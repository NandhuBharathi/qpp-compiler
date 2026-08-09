#include <iostream>
#include <string>
#include <llvm/IR/Constants.h> // LLVM Constant extraction-kaga idhai add pannirukkom
#include "../include/lexer.h"
#include "../include/parser.h"
#include "../include/codegen.h"

int main(int argc, char* argv[]) {
    // Top-level code execution (No mandatory functions needed!)
    std::string code = "";
    if (argc > 1) {
        code = argv[1];
    } else {
        code = "1000 + 1500"; 
    }

    // 1. Initialize LLVM
    InitializeLLVM();

    // 2. Lexer
    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();

    // 3. Parser (Direct-ah expressions-ah handle pannum)
    Parser parser(tokens);
    auto astTree = parser.ParseExpression();

    // 4. Code Generation & Clean Output
    if (astTree) {
        llvm::Value* irValue = astTree->codegen();
        if (irValue) {
            // Check if the result is a constant integer
            if (auto* constInt = llvm::dyn_cast<llvm::ConstantInt>(irValue)) {
                // i32 ellam thookittu, direct-ah value-ah mattum print pandrom
                std::cout << constInt->getSExtValue() << "\n";
            } else {
                // Oruvela future-la complex IR vandha fallback-kaga idhu irukkum
                irValue->print(llvm::outs());
                std::cout << "\n";
            }
        }
    } else {
        std::cout << "Error: Could not parse the expression.\n";
    }

    return 0;
}
