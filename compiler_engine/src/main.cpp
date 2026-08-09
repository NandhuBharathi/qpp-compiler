#include <iostream>
#include "../include/lexer.h"
#include "../include/parser.h"
#include "../include/codegen.h"

int main() {
    std::cout << "--- Q++ LLVM IR Generator Test ---" << std::endl;

    // LLVM Engine-ah start pandrom
    InitializeLLVM();

    // Manual-ah oru AST Tree create pandrom: "100 + 200"
    auto num1 = std::make_unique<NumberExprAST>(100);
    auto num2 = std::make_unique<NumberExprAST>(200);
    auto mathOp = std::make_unique<BinaryExprAST>('+', std::move(num1), std::move(num2));

    std::cout << "\n[Action] Converting AST (100 + 200) to LLVM IR..." << std::endl;

    // AST-ah LLVM IR ah convert pandrom!
    llvm::Value* irValue = mathOp->codegen();

    if (irValue) {
        std::cout << "\n[Success] Generated LLVM Machine IR:" << std::endl;
        // LLVM generate panna code-ah terminal-la print pandrom
        irValue->print(llvm::outs());
        std::cout << "\n";
    } else {
        std::cout << "Error generating IR." << std::endl;
    }

    return 0;
}
