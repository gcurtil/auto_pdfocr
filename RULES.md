# Project Rules and Coding Standards

You are an expert Python developer working on this project. 
Always adhere to the following guidelines when generating or modifying code.

## 1. Python Version & Environment
- Use **Python 3.11+** syntax (e.g., use `match/case` where appropriate).
- Assume the environment is managed by `uv`.
- Type hinting is **mandatory** for all function arguments and return values.

## 2. Code Style & Formatting
- Follow **PEP 8** standards strictly.
- **Line Length:** 88 characters (matching Black configuration).
- **Naming Conventions:**
  - Variables/Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
  - Private members: `_leading_underscore`

## 3. Imports
- Sort imports automatically (simulating `isort`).
- Structure imports in this order:
  1. Standard Library
  2. Third-party Libraries
  3. Local Application Imports
- Use absolute imports (e.g., `from myapp.utils import helper`) rather than relative imports.

## 4. Docstrings & Documentation
- Use **NumPy Style** docstrings.
- Every public function, class, and module must have a docstring.
- **Format:**
  - Sections should be underlined with dashes (`-----`).
  - Common sections: `Parameters`, `Returns`, `Raises`, `See Also`, `Examples`.
- **Example:**
  ```python
  def calculate_velocity(distance: float, time: float) -> float:
      """
      Calculates velocity based on distance and time.

      Parameters
      ----------
      distance : float
          The distance traveled in meters.
      time : float
          The time taken in seconds.

      Returns
      -------
      float
          The calculated velocity in m/s.

      Raises
      ------
      ValueError
          If time is zero or negative.
      
      Examples
      --------
      >>> calculate_velocity(100.0, 10.0)
      10.0
      """
      ...
