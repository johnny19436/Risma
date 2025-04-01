#include <pybind11/pybind11.h>

namespace py = pybind11;

// Declare those bind functions
void bind_var_calculator(py::module_ &);
void bind_portfolio(py::module_ &);

PYBIND11_MODULE(_package, m) {
    m.doc() = "Combined pybind11 module";
    bind_var_calculator(m);
    bind_portfolio(m);
}
