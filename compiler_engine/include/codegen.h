#ifndef CODEGEN_H
#define CODEGEN_H

#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/IRBuilder.h>
#include <memory>
#include <map>
#include <string>

extern std::unique_ptr<llvm::LLVMContext> TheContext;
extern std::unique_ptr<llvm::Module> TheModule;
extern std::unique_ptr<llvm::IRBuilder<>> Builder;

// Variables-ah store panna pora Memory Map!
extern std::map<std::string, llvm::Value*> NamedValues;

void InitializeLLVM();

#endif
