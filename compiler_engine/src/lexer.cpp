#include "../include/lexer.h"
#include <cctype>

// Constructor
Lexer::Lexer(const std::string& input) : src(input), pos(0) {}

Token Lexer::getNextToken() {
    while (pos < src.length()) {
        char current = src[pos];

        // 1. Whitespaces-ah ignore pannuvom
        if (isspace(current)) {
            pos++;
            continue;
        }

        // 2. Identifiers & Keywords (func, return, if, else)
        if (isalpha(current)) {
            std::string val = "";
            while (pos < src.length() && (isalnum(src[pos]) || src[pos] == '_')) {
                val += src[pos];
                pos++;
            }
            if (val == "func") return {TOK_FUNC, val};
            if (val == "return") return {TOK_RETURN, val};
            if (val == "if") return {TOK_IF, val};
            if (val == "else") return {TOK_ELSE, val};
            return {TOK_IDENTIFIER, val};
        }

        // 3. Numbers
        if (isdigit(current)) {
            std::string val = "";
            while (pos < src.length() && isdigit(src[pos])) {
                val += src[pos];
                pos++;
            }
            return {TOK_NUMBER, val};
        }

        // 4. Symbols
        if (current == '{') { pos++; return {TOK_LBRACE, "{"}; }
        if (current == '}') { pos++; return {TOK_RBRACE, "}"}; }
        if (current == '(') { pos++; return {TOK_LPAREN, "("}; }
        if (current == ')') { pos++; return {TOK_RPAREN, ")"}; }
        if (current == '=') { pos++; return {TOK_ASSIGN, "="}; }
        if (current == '+') { pos++; return {TOK_PLUS, "+"}; }
        if (current == '>') { pos++; return {TOK_GREATER, ">"}; }

        // Unknown characters
        pos++;
        return {TOK_UNKNOWN, std::string(1, current)};
    }
    return {TOK_EOF, ""};
}

// Motha code-aiyum array(vector)-ah matha
std::vector<Token> Lexer::tokenize() {
    std::vector<Token> tokens;
    Token tok = getNextToken();
    while (tok.type != TOK_EOF) {
        tokens.push_back(tok);
        tok = getNextToken();
    }
    tokens.push_back({TOK_EOF, ""});
    return tokens;
}
