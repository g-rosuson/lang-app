# Language App Tests

This directory contains tests for the Language App service.

## Running Tests

To run all tests:

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest src/tests/ -v

# Run specific test file
python -m pytest src/tests/services/test_text_preprocessing.py -v

# Run with coverage (if pytest-cov is installed)
python -m pytest src/tests/ --cov=src --cov-report=html
```

## Test Structure

- `services/` - Tests for language analysis services
  - `test_text_preprocessing.py` - Text preprocessing utility tests
  - `test_model_manager.py` - Model management utility tests  
  - `test_models.py` - Pydantic data model tests

## Test Coverage

The current test suite covers:

- ✅ Text preprocessing and validation
- ✅ Model management utilities
- ✅ Data model validation
- ✅ Error handling and edge cases
- ✅ Configuration validation

## Adding New Tests

When adding new tests:

1. Follow the naming convention: `test_*.py`
2. Use descriptive test method names: `test_<function>_<scenario>`
3. Include docstrings explaining what each test validates
4. Use appropriate assertions and error messages
5. Mock external dependencies when needed
