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
        // Namma test case: Assign first, print next!
        code = "total = 800 + 900 print(total)"; 
    }

    InitializeLLVM();
    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();
    Parser parser(tokens);

    // Loop: Muthal token la irundhu kadasila EOF varaikum continuous-ah run aagum!
    while (parser.currentToken().type != TOK_EOF) {
        auto astTree = parser.ParseExpression();
        
        if (astTree) {
            llvm::Value* irValue = astTree->codegen();
            if (irValue) {
                // MUKKIYAM: isSilent() false aaga irundha mattum thaan output print aagum!
                if (!astTree->isSilent()) {
                    if (auto* constInt = llvm::dyn_cast<llvm::ConstantInt>(irValue)) {
                        std::cout << constInt->getSExtValue() << "\n";
                    } else {
                        irValue->print(llvm::outs());
                        std::cout << "\n";
                    }
                }
            }
        } else {
            std::cout << "Error: Invalid syntax.\n";
            break;
        }
    }

    return 0;
}
