#include <iostream>
#include <string>
#include <llvm/IR/Constants.h>
#include "../include/lexer.h"
#include "../include/parser.h"
#include "../include/codegen.h"

int main(int argc, char* argv[]) {
    std::string code = "";
    if (argc > 1) {
        code = argv[1];
    } else {
        // Correct Order: Initialize first, copy next, add and print!
        code = "x,y,z = 10,20,30; a,b,c = x,y,z; total = a+b+c; print(total)"; 
    }

    InitializeLLVM();
    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();
    Parser parser(tokens);

    while (parser.currentToken().type != TOK_EOF) {
        if (parser.currentToken().type == TOK_EOL) {
            parser.getNextToken();
            continue;
        }

        auto astTree = parser.ParseExpression();
        
        if (astTree) {
            if (parser.currentToken().type != TOK_EOL && parser.currentToken().type != TOK_EOF) {
                std::cout << "Syntax Error: Expected newline or ';' between statements.\n";
                break;
            }

            llvm::Value* irValue = astTree->codegen();
            if (irValue && !astTree->isSilent()) {
                if (auto* constInt = llvm::dyn_cast<llvm::ConstantInt>(irValue)) {
                    std::cout << constInt->getSExtValue() << "\n";
                } else {
                    irValue->print(llvm::outs()); std::cout << "\n";
                }
            }
        } else {
            std::cout << "Error: Invalid syntax.\n";
            break;
        }
    }

    return 0;
}
