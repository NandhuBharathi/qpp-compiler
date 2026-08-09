#ifndef LEXER_H
#define LEXER_H

#include <string>
#include <vector>

// Q++ kaga namma define pandra Token types
enum TokenType {
    TOK_FUNC,       // 'func'
    TOK_RETURN,     // 'return'
    TOK_IF,         // 'if'
    TOK_ELSE,       // 'else'
    TOK_IDENTIFIER, // Variable/Function names
    TOK_NUMBER,     // 100, 200, etc.
    TOK_LBRACE,     // '{'
    TOK_RBRACE,     // '}'
    TOK_LPAREN,     // '('
    TOK_RPAREN,     // ')'
    TOK_ASSIGN,     // '='
    TOK_PLUS,       // '+'
    TOK_GREATER,    // '>'
    TOK_EOF,        // End of File
    TOK_UNKNOWN     // Unrecognized characters
};

// Oru Token-oda structure
struct Token {
    TokenType type;
    std::string value;
};

// Lexer Class definition
class Lexer {
    std::string src;
    size_t pos;
public:
    Lexer(const std::string& input);
    Token getNextToken();
    std::vector<Token> tokenize();
};

#endif
