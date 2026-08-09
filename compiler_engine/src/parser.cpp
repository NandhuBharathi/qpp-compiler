#include "../include/parser.h"
#include <iostream>

Parser::Parser(std::vector<Token> tokens) : tokens(tokens), pos(0) {}

Token Parser::currentToken() {
    if (pos < tokens.size()) return tokens[pos];
    return {TOK_EOF, ""};
}

Token Parser::getNextToken() {
    if (pos < tokens.size()) pos++;
    return currentToken();
}

std::unique_ptr<ExprAST> Parser::ParseNumberExpr() {
    auto result = std::make_unique<NumberExprAST>(std::stoi(currentToken().value));
    getNextToken();
    return std::move(result);
}

std::unique_ptr<ExprAST> Parser::ParseStringExpr() {
    bool isTemplate = false;
    if (currentToken().type == TOK_BANG) {
        isTemplate = true;
        getNextToken(); 
    }
    if (currentToken().type != TOK_STRING) return nullptr;
    std::string val = currentToken().value;
    getNextToken(); 
    return std::make_unique<StringExprAST>(val, isTemplate);
}

std::unique_ptr<ExprAST> Parser::ParseIdentifierExpr() {
    std::string idName = currentToken().value;
    
    bool isAssign = false;
    for (size_t i = pos; i < tokens.size(); i++) {
        if (tokens[i].type == TOK_ASSIGN) { isAssign = true; break; }
        if (tokens[i].type != TOK_IDENTIFIER && tokens[i].type != TOK_COMMA) break; 
    }

    getNextToken(); 

    if (!isAssign) {
        return std::make_unique<VariableExprAST>(idName);
    }

    std::vector<std::string> names;
    names.push_back(idName);

    while (currentToken().type == TOK_COMMA) {
        getNextToken(); names.push_back(currentToken().value); getNextToken();
    }

    getNextToken(); 

    std::vector<std::unique_ptr<ExprAST>> vals;
    vals.push_back(ParseExpression());

    while (currentToken().type == TOK_COMMA) {
        getNextToken(); vals.push_back(ParseExpression());
    }

    return std::make_unique<AssignExprAST>(names, std::move(vals));
}

std::unique_ptr<ExprAST> Parser::ParsePrintExpr() {
    getNextToken(); 
    if (currentToken().type != TOK_LPAREN) return nullptr;
    getNextToken(); 
    
    std::vector<std::unique_ptr<ExprAST>> args;
    
    if (currentToken().type != TOK_RPAREN) {
        while (true) {
            if (currentToken().type == TOK_STRING || currentToken().type == TOK_BANG) {
                args.push_back(ParseStringExpr());
            } else {
                args.push_back(ParseExpression());
            }
            
            if (currentToken().type == TOK_RPAREN) break;
            
            if (currentToken().type == TOK_COMMA) {
                getNextToken(); 
            } else {
                break;
            }
        }
    }
    
    if (currentToken().type != TOK_RPAREN) return nullptr;
    getNextToken(); 
    
    return std::make_unique<PrintExprAST>(std::move(args));
}

std::unique_ptr<ExprAST> Parser::ParseInputExpr() {
    getNextToken(); 
    if (currentToken().type != TOK_LPAREN) return nullptr;
    getNextToken(); 
    
    std::string promptMessage = "Enter value: ";

    if (currentToken().type == TOK_BANG) {
        getNextToken(); 
    }
    if (currentToken().type == TOK_STRING) {
        promptMessage = currentToken().value; 
        getNextToken(); 
    }
    
    if (currentToken().type != TOK_RPAREN) return nullptr;
    getNextToken(); 

    int userValue = 0;
    std::cout << promptMessage << "\n"; 
    std::cout.flush(); 
    std::cin >> userValue;

    return std::make_unique<NumberExprAST>(userValue);
}

// 💥 1. ParsePrimary: Numbers, Variables, Inputs, and Parentheses ( )
std::unique_ptr<ExprAST> Parser::ParsePrimary() {
    if (currentToken().type == TOK_NUMBER) {
        return ParseNumberExpr();
    }
    if (currentToken().type == TOK_IDENTIFIER) {
        return ParseIdentifierExpr();
    }
    if (currentToken().type == TOK_INPUT) {
        return ParseInputExpr();
    }
    if (currentToken().type == TOK_STRING || currentToken().type == TOK_BANG) {
        return ParseStringExpr();
    }
    
    // Parentheses (BODMAS Brackets Support!)
    if (currentToken().type == TOK_LPAREN) {
        getNextToken(); // Consume '('
        auto node = ParseExpression();
        if (!node) return nullptr;
        if (currentToken().type != TOK_RPAREN) {
            std::cerr << "Error: Expected ')'\n";
            return nullptr;
        }
        getNextToken(); // Consume ')'
        return node;
    }

    return nullptr;
}

// 💥 2. ParseTerm: Higher Precedence (* and /)
std::unique_ptr<ExprAST> Parser::ParseTerm() {
    auto LHS = ParsePrimary();
    if (!LHS) return nullptr;

    while (currentToken().type == TOK_MUL || currentToken().type == TOK_DIV) {
        char op = currentToken().value[0];
        getNextToken();
        auto RHS = ParsePrimary();
        if (!RHS) return nullptr;
        LHS = std::make_unique<BinaryExprAST>(op, std::move(LHS), std::move(RHS));
    }
    return LHS;
}

// 💥 3. ParseExpression: Lower Precedence (+ and -)
std::unique_ptr<ExprAST> Parser::ParseExpression() {
    // If it's a print statement or assignment starting with identifier
    if (currentToken().type == TOK_PRINT) {
        return ParsePrintExpr();
    }

    auto LHS = ParseTerm();
    if (!LHS) {
        if (currentToken().type == TOK_IDENTIFIER) {
            return ParseIdentifierExpr(); // Handles variable assignments like a = 10
        }
        return nullptr;
    }

    while (currentToken().type == TOK_PLUS || currentToken().type == TOK_MINUS) {
        char op = currentToken().value[0];
        getNextToken();
        auto RHS = ParseTerm();
        if (!RHS) return nullptr;
        LHS = std::make_unique<BinaryExprAST>(op, std::move(LHS), std::move(RHS));
    }
    return LHS;
}
