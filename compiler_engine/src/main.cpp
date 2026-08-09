#include <iostream>
#include <string>
#include "../include/lexer.h"
#include "../include/parser.h"
#include "../include/codegen.h"

int main(int argc, char* argv[]) {
    std::string code = "";
    if (argc > 1) {
        code = argv[1];
    } else {
        code = "func calculate_total(price) { return price + 100 }";
    }

    std::cout << "--- Q++ Compiler Engine ---" << std::endl;

    // 1. Initialize LLVM Backend
    InitializeLLVM();
    std::cout << "[LLVM] Backend Initialized Successfully." << std::endl;

    // 2. Lexical Analysis
    Lexer lexer(code);
    std::vector<Token> tokens = lexer.tokenize();
    std::cout << "[Lexer] Identified " << tokens.size() << " tokens." << std::endl;

    // 3. Parsing & AST Building
    Parser parser(tokens);
    parser.parse();

    // 4. Future Step: Code Generation (AST to IR)
    // Ingendhu dhaan namma AST nodes-ah TheModule-kulla IR ah push pannuvom.
    
    std::cout << "\n[Status] Engine Pipeline Ready for Code Generation!" << std::endl;

    return 0;
}
