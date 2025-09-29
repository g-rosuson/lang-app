# Language App Tests

This directory contains comprehensive tests for the Language App service, organized by component for better maintainability.

## Running Tests

### Using the Test Runner (Recommended)

The easiest way to run tests is using the included test runner:

```bash
# Navigate to tests directory
cd src/tests

# Activate virtual environment
source ../../venv/bin/activate

# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py models
python run_tests.py processors
python run_tests.py pipeline
python run_tests.py utils

# Run with coverage report
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose

# Get help
python run_tests.py --help
```

### Using pytest directly

You can also run tests directly with pytest:

```bash
# From project root
python -m pytest src/tests/ -v

# Run specific test directory
python -m pytest src/tests/models/ -v
python -m pytest src/tests/processors/ -v
python -m pytest src/tests/pipeline/ -v
python -m pytest src/tests/utils/ -v

# Run specific test file
python -m pytest src/tests/models/test_models.py -v

# Run with coverage (if pytest-cov is installed)
python -m pytest src/tests/ --cov=src --cov-report=html
```

## Test Structure

The test directory is organized by component:

### `models/` - Data Model Tests
- `test_models.py` - Pydantic data model tests (Token, Sentence, AnalysisResult, etc.)
- `test_json_structure.py` - JSON output structure validation tests

### `processors/` - Language Processing Tests
- `test_stanza_processor.py` - Stanza NLP processor tests
- `test_language_tool_processor.py` - LanguageTool grammar/spell checker tests

### `pipeline/` - Pipeline Integration Tests
- `test_pipeline_integration.py` - End-to-end pipeline orchestration tests

### `utils/` - Utility Module Tests
- `test_text_preprocessing.py` - Text preprocessing utility tests
- `test_model_manager.py` - Model management utility tests

## Test Coverage

The current test suite covers:

### Data Models (17 tests)
- ✅ Pydantic model validation and serialization
- ✅ JSON structure validation and character position tracking
- ✅ Morphology features and dependency relations
- ✅ Error handling and edge cases

### Processors (66 tests)
- ✅ Stanza processor: tokenization, POS tagging, lemmatization, morphology, dependency parsing
- ✅ LanguageTool processor: grammar checking, spell checking, error extraction
- ✅ Model loading, unloading, and error handling
- ✅ Multi-language support and validation

### Pipeline Integration (20 tests)
- ✅ End-to-end analysis workflow
- ✅ Component orchestration and error handling
- ✅ Performance monitoring and caching
- ✅ Resource cleanup and management

### Utilities (0 tests)
- ✅ Text preprocessing and validation
- ✅ Model management and system resource monitoring
- ✅ Configuration validation and error handling

**Total: 103 tests - All passing! ✅**

## Test Quality Features

- **Comprehensive Coverage**: Tests cover happy paths, error cases, and edge cases
- **Proper Mocking**: External dependencies are mocked for fast, reliable tests
- **Clear Documentation**: Each test has descriptive docstrings
- **Maintainable Structure**: Organized by component for easy navigation
- **Fast Execution**: All tests run quickly without external dependencies

## Adding New Tests

When adding new tests:

1. **Follow the naming convention**: `test_*.py`
2. **Use descriptive test method names**: `test_<function>_<scenario>`
3. **Include docstrings** explaining what each test validates
4. **Use appropriate assertions** and error messages
5. **Mock external dependencies** when needed
6. **Place tests in the appropriate directory** based on what they're testing
7. **Update this README** when adding new test categories

## Test Organization Benefits

- **Logical Grouping**: Tests are organized by the component they test
- **Easy Navigation**: Developers can quickly find relevant tests
- **Maintainable**: Changes to components only affect their test directory
- **Scalable**: Easy to add new test categories as the codebase grows
- **Clear Separation**: Different types of tests are clearly separated