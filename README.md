# Risma
  A command-line tool for real-time risk management and analysis in hedge funds 
  using modern C++ (with OpenCL) and Python.

Problem to Solve
================

Hedge funds need efficient and reliable risk assessment tools. This project
addresses the challenge of computing real-time Value-at-Risk (VaR) and Expected
Shortfall (ES) metrics. Key points include:

1. Financial industry risk management.
2. Advanced numerical methods for Monte Carlo VaR.
3. Use of parallel computing (via OpenCL) to accelerate large-scale matrix
   operations and stress testing simulations.

Prospective Users
=================

The primary users of this software are:

- Hedge Fund Managers: to monitor and evaluate portfolio risks in real time.
- Risk Analysts: to perform detailed risk assessments and simulate stress
  scenarios.
- Financial Institutions: to integrate a robust risk management engine into their
  existing systems.

System Architecture
===================

The system is a hybrid application with two main modules:

- C++ Module:
   Implements fast matrix computations using OpenCL.
   Performs risk calculations (VaR, ES) using Monte Carlo method.

- Python Module:
    Acts as a high-level interface and provides data analysis, visualization,
    and scripting capabilities using NumPy, Pandas, and Matplotlib.

Workflow:
  1. The user inputs portfolio data and risk parameters via the command-line.
  2. The Python module processes the input and calls the C++ module for
     computation-intensive tasks.
  3. Results are returned, analyzed, and displayed with visual reports.

API Description
===============

The system offers APIs for both C++ and Python.

C++ API:
  - Provides functions such as `computeVaR(portfolio, params)` and
    `simulateStressTest(portfolio, conditions)`.
  - Designed for high performance and parallel computation.

Python API:
  - Offers wrapper functions for C++ APIs, allowing seamless integration in
    Python scripts.

Engineering Infrastructure
==========================

The project is supported by a robust engineering setup:

1. Automatic Build System:
     Single-command build process using CMake for the C++ module and a
     setup.py script for the Python module.
2. Version Control:
     Code is hosted on GitHub with frequent commits, pull requests, and branch
     management.

3. Testing Framework:

   - C++ Testing: Using Google test for Core Risk Computation Functions. 

     - Accuracy: Ensure computed VaR,ES matches expected results for known inputs.
     - Edge Cases: Test with extreme values (e.g., highly volatile assets, zero returns).
     - Robustness: Handle cases with limited data or highly skewed return distributions.

   - Python Testing: Uses pytest to validate API wrappers.

     - Integration Testing: Verify that Python functions correctly wrap C++ computations.
     - Exception Handling: Gracefully handle erroneous inputs or C++ failures.


Schedule
========

The project is planned for 11-week development:

**Planning phase** (11 weeks from 3/10 to 5/26):
  * Week 1 (3/10): Set up repository, initial project skeleton, and prototype
    for basic functionalities.
  * Week 3 (3/24): Develop core risk computation functions in C++.
  * Week 4 (3/31): Create Python wrappers and a basic CLI interface.
  * Week 5 (4/7): Integrate C++ and Python modules; begin unit testing on C++.
  * Week 6 (4/14): Optimize parallel computations and enhance performance.
  * Week 7 (4/21): Full system testing and comprehensive documentation.
**Integration** and Presentation Phase (2 weeks):
  * Week 9 (5/5): Final feature integration, address feedback, polish CLI.
  * Week 10 (5/12): Prepare final presentation and finalize repository details.

References
==========

- `Value at Risk (VaR) - Investopedia <https://www.investopedia.com/terms/v/var.asp>`__
- `Expected Shortfall (ES or CVaR) - Investopedia <https://www.investopedia.com/terms/c/conditional_value_at_risk.asp>`__
-  Use Yahoo Finance, Google Finance, and Alpha Vantage as reference for 
   historical stock prices, indices, or currency data.