#include <iostream>
#include <string>
#include "../include/lexer.h"
#include "../include/parser.h"
#include "../include/codegen.h"

int main(int argc, char* argv[]) {
    // User terminal-la type pandra code-ah edukkum
    std::string code = "";
    if (argc > 1) {
        code = argv[1];
    } else {
        code = "450 + 550"; // Default dynamic code
    }

    // 1. Initialize LLVM
    InitializeLLVM();

    // 2. Text to Tokens
    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();

    // 3. Tokens to AST
    Parser parser(tokens);
    auto astTree = parser.ParseExpression(); // Dynamically building the tree

    // 4. AST to LLVM IR
    if (astTree) {
        llvm::Value* irValue = astTree->codegen();
        if (irValue) {
            irValue->print(llvm::outs()); // Output the generated machine code
            std::cout << "\n";
        }
    } else {
        std::cout << "Error: Could not parse the expression." << std::endl;
    }

    return 0;
}
