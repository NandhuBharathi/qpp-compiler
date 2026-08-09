#include "../include/codegen.h"

// Define the global objects
std::unique_ptr<llvm::LLVMContext> TheContext;
std::unique_ptr<llvm::Module> TheModule;
std::unique_ptr<llvm::IRBuilder<>> Builder;

void InitializeLLVM() {
    // Open a new LLVM context
    TheContext = std::make_unique<llvm::LLVMContext>();
    
    // Create a new module (container) named "Q++ JIT Compiler"
    TheModule = std::make_unique<llvm::Module>("Q++ JIT Compiler", *TheContext);
    
    // Initialize the IR Builder tool
    Builder = std::make_unique<llvm::IRBuilder<>>(*TheContext);
}
