# copilot-instructions.md

## GitHub Copilot Usage Instructions for This Repository

Welcome to the `floatingpoint` project! This document provides guidelines and best practices for using GitHub Copilot in this repository.

---

### 1. **General Guidelines**

- **Follow Python best practices**: Use type hints, docstrings, and clear variable names.
- **Use linter**: Ensure your code adheres to the project's coding standards defined in the file `.pylintrc`.
- **Avoid unnecessary complexity**: Keep functions and methods simple and focused on a single task.
- **Respect existing code style**: Match indentation, naming conventions, and formatting.
- **Write descriptive commit messages**: Summarize what your change does and why.
- **Add or update docstrings** for all new functions, classes, and methods.
- **Write or update tests** for any new features or bug fixes.

---

### 2. **Project Structure**

- Main floating-point logic is in `fp.py`.
- Utility functions are imported from `fputil.py`.
- Web interface and API logic should be placed in a dedicated backend file (e.g., `app.py`).
- Frontend templates (if any) should be placed in a `templates/` directory.

---

### 3. **When Using Copilot**

- **Review all Copilot suggestions** for correctness and security.
- **Do not accept code that exposes sensitive data** or introduces vulnerabilities.
- **Avoid generating or committing code that violates copyright** or license terms.
- **If Copilot generates code that is unclear or untested,** add comments or request clarification.

---

### 4. **Pull Requests**

- **Describe your changes clearly** in the PR description.
- **Reference related issues** if applicable.
- **Ensure all tests pass** before requesting a review.
- **Expose only the necessary attributes** in API responses (e.g., `fp`, `bits`, `exact_decimal`, `unbiased_exp` for FP objects).

---

### 5. **Floating Point Representation**

- Use the `FP` class for all floating-point manipulations.
- To convert a float to its exact decimal representation, use:
  ```python
  fp_obj = FP.from_float(your_float)
  print(fp_obj.exact_decimal)
  ```
- When exposing FP objects via API, include:
  - `fp`: the Python float representation
  - `bits`: the binary representation
  - `exact_decimal`: the exact decimal value
  - `unbiased_exp`: the unbiased exponent

---

### 6. **Web/API Integration**

- When adding new routes, ensure they:
  - Accept input as JSON or form data.
  - Validate and sanitize all user input.
  - Return all relevant FP attributes in the response.

---

### 7. **Testing**

- Place tests in a `tests/` directory.
- Use `pytest` or Python’s built-in `unittest` framework.
- Add tests for new features and edge cases.

---

### 8. **Documentation**

- Update this file if project conventions change.
- Add usage examples to the main README as needed.

---

Thank you for contributing to `floatingpoint