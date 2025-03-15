cmake_minimum_required(VERSION 3.10)
project(Risma VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add OpenCL package
find_package(OpenCL REQUIRED)

# Add source files
add_executable(risma_cpp
    cpp_module/main.cpp
    cpp_module/var_calculator.cpp
    cpp_module/portfolio.cpp
)

# Include directories
target_include_directories(risma_cpp PRIVATE 
    ${OpenCL_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}/cpp_module/include
)

# Link libraries
target_link_libraries(risma_cpp PRIVATE OpenCL::OpenCL) 