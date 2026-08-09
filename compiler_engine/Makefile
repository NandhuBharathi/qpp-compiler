CXX = g++
CXXFLAGS = -Wall -std=c++17 -I./include

SRC_DIR = src
SOURCES = $(SRC_DIR)/main.cpp $(SRC_DIR)/lexer.cpp
TARGET = qpp_engine

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET)
