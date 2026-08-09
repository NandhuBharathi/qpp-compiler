CXX = g++
# LLVM Flags-ah auto-va edukka
LLVM_CXXFLAGS = `llvm-config --cxxflags`
LLVM_LDFLAGS = `llvm-config --ldflags --system-libs --libs core`

CXXFLAGS = -Wall -std=c++17 -I./include $(LLVM_CXXFLAGS)

SRC_DIR = src
SOURCES = $(SRC_DIR)/main.cpp $(SRC_DIR)/lexer.cpp $(SRC_DIR)/parser.cpp $(SRC_DIR)/codegen.cpp
TARGET = qpp_engine

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LLVM_LDFLAGS)

clean:
	rm -f $(TARGET)
