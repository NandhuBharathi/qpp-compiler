#ifndef LEXER_H
#define LEXER_H

#include <string>
#include <vector>

enum TokenType {
    TOK_FUNC, TOK_RETURN, TOK_IF, TOK_ELSE, 
    TOK_PRINT,      // Pudhusa 'print' keyword add pandrom
    TOK_IDENTIFIER, TOK_NUMBER,
    TOK_LBRACE, TOK_RBRACE, TOK_LPAREN, TOK_RPAREN,
    TOK_ASSIGN, TOK_PLUS, TOK_GREATER, TOK_EOF, TOK_UNKNOWN
};

struct Token {
    TokenType type;
    std::string value;
};

class Lexer {
    std::string src;
    size_t pos;
public:
    Lexer(const std::string& input);
    Token getNextToken();
    std::vector<Token> tokenize();
};

#endif
