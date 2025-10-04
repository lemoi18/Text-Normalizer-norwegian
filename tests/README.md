# Norwegian Text Normalizer Tests

This directory contains comprehensive unit tests for the Norwegian text normalizer project.

## Test Coverage

The test suite covers all major functionality:

### Number Grammar (`number_grammar_reverse.py`)
- Number to Norwegian text conversion
- Single digits, teens, tens, compound numbers
- Hundreds, thousands, and millions
- Decimal and percentage parsing
- Range expressions and parenthesized numbers
- Grammar parsing and edge cases

### Year Grammar (`year_grammar_reverse.py`)
- Year to Norwegian text conversion
- Special handling for 1900s and 2000s
- Compressed format for years below 100
- Grammar parsing with punctuation
- Out-of-range year handling

### Date Grammar (`date_grammar_reverse.py`)
- Day to ordinal conversion
- Month number to name conversion
- Date pattern parsing (e.g., "3. juni", "03.06.2022")
- Time expression parsing (e.g., "klokka 17.30")
- Edge cases for different date formats

### Abbreviation Grammar (`abbrev_grammar_reverse.py`)
- Abbreviation dictionary reverse lookup
- Expansion function testing
- Grammar parsing for abbreviations
- Multiple expansion handling
- Integration with text processing

## Running Tests

### Method 1: Using the test runner (recommended)
```bash
python run_tests.py
```

### Method 2: Running tests directly
```bash
python tests/test_norwegian_normalizer.py
```

### Method 3: Using unittest module
```bash
python -m unittest tests.test_norwegian_normalizer -v
```

### Method 4: Using pytest (if installed)
```bash
pytest tests/ -v
```

## Test Structure

- `test_norwegian_normalizer.py`: Main test file containing all test cases
- Tests are organized into logical classes for each module
- Each test focuses on a specific functionality
- Integration tests verify modules work together
- Error handling tests ensure graceful failure

## Import Issues Resolved

The project had several import issues that have been fixed:
- Relative imports converted to absolute imports
- Circular dependency issues resolved
- Missing module references corrected

## Test Results

All 31 tests pass successfully, covering:
- ✅ Number conversion and parsing
- ✅ Year conversion and parsing
- ✅ Date parsing and normalization
- ✅ Abbreviation expansion
- ✅ Grammar parsing
- ✅ Edge cases and error handling
- ✅ Module integration

## Future Improvements

Potential areas for additional testing:
- Performance testing for large inputs
- Stress testing with complex text
- Additional Norwegian dialect support
- More edge cases for date formats
- Unicode and encoding tests