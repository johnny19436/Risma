PYTHON := python3
CXX := g++
UNAME_S := $(shell uname -s)

PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print('python{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
PYTHON_INCLUDE = $(shell $(PYTHON)-config --includes)
PYTHON_LDFLAGS := $(shell $(PYTHON)-config --ldflags)

HOMEBREW_INCLUDE := /opt/homebrew/include
HOMEBREW_LIB := -L/opt/homebrew/lib -lboost_math_c99

# Pybind11 include path
PYBIND11_INCLUDE := $(shell $(PYTHON) -m pybind11 --includes 2>/dev/null | sed 's/-I//')
ifeq ($(PYBIND11_INCLUDE),)
	PYBIND11_INCLUDE := /usr/include/pybind11
endif

# OS-specific BLAS/MKL flags
ifeq ($(UNAME_S),Darwin)
    # For macOS, assume OpenBLAS from Homebrew and add dynamic lookup flag for Python extensions
    BLAS_INCLUDE := /opt/homebrew/opt/openblas/include
    BLAS_LIB := -L/opt/homebrew/opt/openblas/lib -lopenblas
    DYNAMIC_LOOKUP := -undefined dynamic_lookup
else ifeq ($(UNAME_S),Linux)
    BLAS_INCLUDE := /usr/include/mkl
    BLAS_LIB := -lmkl_rt -lpthread -lm -ldl
    DYNAMIC_LOOKUP :=
else
    $(error "Unsupported OS: $(UNAME_S)")
endif

CXXFLAGS := -O3 -march=native -std=c++17 -fPIC
INCLUDES := -I$(PYBIND11_INCLUDE) -I$(BLAS_INCLUDE) -I$(HOMEBREW_INCLUDE) $(PYTHON_INCLUDE) 
LDFLAGS := $(PYTHON_LDFLAGS) $(BLAS_LIB) $(HOMEBREW_LIB)

# SRC := _portfolio.cpp _varCalculator.cpp
# TARGET :=  _portfolio$(shell $(PYTHON)-config --extension-suffix) _varCalculator$(shell $(PYTHON)-config --extension-suffix)

SRC := _varCalculator.cpp _portfolio.cpp
TARGET :=  _varCalculator$(shell $(PYTHON)-config --extension-suffix)

.PHONY: all test clean

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -DBUILD_PYBIND -shared $(DYNAMIC_LOOKUP) -o $@ $^ $(INCLUDES) $(LDFLAGS)


test: all
	$(PYTHON) -m pytest --maxfail=1 --disable-warnings -q
	
clean:
	rm -f $(TARGET)
	find . -type f -name '*.so' -delete
	rm -rf __pycache__ .pytest_cache

