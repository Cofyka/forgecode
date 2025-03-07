# Contributing to ForgeCode

Thank you for your interest in contributing to ForgeCode! This project is open-source, and we welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code enhancements.

## How to Contribute

### 1. Reporting Issues

- If you encounter a bug, unexpected behavior, or have a feature request, please [open an issue](https://github.com/Cofyka/forgecode/issues) with a clear and detailed description.
- Provide steps to reproduce the issue and include relevant logs or screenshots if possible.
- If you're suggesting an enhancement, explain why it would be beneficial and how it aligns with ForgeCode’s goals.

### 2. Forking and Setting Up

- Fork the repository on GitHub to create your own copy where you can freely make changes.
- Clone your fork locally (replace `YOUR_USERNAME` with your GitHub username):
  ```sh
  git clone https://github.com/YOUR_USERNAME/forgecode.git
  cd forgecode
  ```
- Set up a virtual environment and install dependencies using Poetry:
  ```sh
  poetry config virtualenvs.in-project true
  poetry install
  ```
- Run the example script to verify that everything is set up correctly:
  ```sh
  poetry run python examples/basic.py
  ```

### 3. Making Changes

- Create a new branch for your feature or fix:
  ```sh
  git checkout -b feature-name
  ```
- Follow the project's coding style and best practices.
- Write tests for your changes if applicable.
- Run tests before submitting your changes:
  ```sh
  poetry run pytest
  ```
- Ensure code quality and formatting:
  ```sh
  poetry run black . && poetry run flake8 .
  ```

### 4. Setting Up Pre-commit Hooks (Optional)

- To ensure consistent code formatting and quality, you can set up pre-commit hooks:
  ```sh
  poetry run pre-commit install
  ```
  This will automatically run formatting and lint checks when you commit your changes.

### 5. Submitting a Pull Request

- Push your changes to your fork:
  ```sh
  git push origin feature-name
  ```
- Open a pull request (PR) against the `main` branch in the original ForgeCode repository.
- Provide a descriptive title and summary of your changes.
- Be responsive and address any feedback provided during the review process.

### 6. Code Review Process

- PRs will be reviewed for correctness, style, maintainability, and alignment with project goals.
- Reviewers may request changes; please respond promptly.
- Once approved, your PR will be merged.

## Code Style Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use [Black](https://black.readthedocs.io/en/stable/) for formatting and `isort` for import sorting.
- Keep functions and classes concise, clear, and well-documented.

## Community Guidelines

- Be respectful and collaborative.
- Follow GitHub's [Code of Conduct](https://docs.github.com/en/site-policy/github-terms/github-community-guidelines).
- Constructive feedback is encouraged and appreciated.

## Contact

If you have any questions, feel free to reach out by opening an issue or joining discussions in the repository.

We appreciate your contributions to ForgeCode!

