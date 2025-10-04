#!/usr/bin/env python3
"""
Integrated Grammar System for Norwegian Text Normalizer

This module combines all grammar patterns (basic and enhanced) into a single,
comprehensive grammar system with proper priority ordering.
"""

import pyparsing as pp
from pyparsing import Word, printables, alphas8bit

# Import all grammar modules
from number_grammar_reverse import numbergrammar_reverse, wstart, wend, WS
from year_grammar_reverse import yeargrammar_reverse
from date_grammar_reverse import dategrammar_reverse
from abbrev_grammar_reverse import abbrevgrammar_reverse
from enhanced_patterns_grammar_reverse import (
    enhanced_range_expr,
    unicode_fraction_expr,
    slash_date_expr,
    dash_date_expr,
    yearfirst_date_expr,
    scientific_notation_expr,
    mixed_number_expr,
    large_number_expr
)

# Base word grammar for fallback
wordgrammar = Word(printables + alphas8bit)

# Import enhanced patterns
from enhanced_patterns_grammar_reverse import (
    enhanced_range_expr,
    unicode_fraction_expr,
    slash_date_expr,
    dash_date_expr,
    yearfirst_date_expr,
    scientific_notation_expr,
    mixed_number_expr,
    large_number_expr
)

# Comprehensive grammar with proper priority ordering
# Enhanced patterns come first to ensure they match before basic patterns
comprehensive_grammar = (
    enhanced_range_expr           # Range patterns (10-15, 2010-2020) - HIGHEST PRIORITY
    ^ unicode_fraction_expr       # Unicode fractions (½, ¾, ⅓)
    ^ slash_date_expr            # Slash dates (1/6/2023)
    ^ dash_date_expr             # Dash dates (06-03-2023)
    ^ yearfirst_date_expr        # Year-first dates (2023.06.03)
    ^ scientific_notation_expr   # Scientific notation (1,5×10³)
    ^ mixed_number_expr          # Mixed numbers (1 1/2)
    ^ large_number_expr          # Large numbers with proper naming (9+ digits)
    ^ abbrevgrammar_reverse       # Abbreviations (ca., f.eks., osv.)
    ^ dategrammar_reverse        # Standard date patterns (3. juni, 03.06.2023)
    ^ yeargrammar_reverse        # Year patterns (1980, 2010, 2023)
    ^ numbergrammar_reverse      # Number patterns (15, 2,5, 1000)
    ^ wordgrammar               # Fallback to plain words
)

def get_grammar():
    """
    Returns the comprehensive grammar with all patterns.

    Returns:
        PyParsing grammar object with all Norwegian text normalization patterns
    """
    return comprehensive_grammar

def normalize_text(text):
    """
    Normalize Norwegian text using the comprehensive grammar.

    This is the core normalization function that handles all Norwegian text patterns:
    - Years: 2010 → "tjue ti"
    - Dates: 3. juni → "tredje juni"
    - Numbers: 15 → "femten"
    - Abbreviations: ca. → "cirka"
    - Enhanced patterns: 10-15 → "ti til femten"

    Args:
        text (str): Input Norwegian text to normalize

    Returns:
        str: Normalized text with patterns converted to spoken Norwegian
    """
    if not text or not isinstance(text, str):
        return text

    # Get all matches from the grammar
    matches = comprehensive_grammar.searchString(text)

    if not matches:
        return text

    # Collect all normalized replacements with their positions
    replacements = []
    for match in matches:
        if len(match) > 0:
            first_element = match[0]

            # Check if this is a normalized pattern
            if isinstance(first_element, tuple) and len(first_element) == 2:
                original_text = str(first_element[0])
                normalized_text = str(first_element[1])
                # Find position of original text in the remaining text
                pos = text.find(original_text)
                if pos != -1:
                    replacements.append((pos, len(original_text), normalized_text))
            elif hasattr(first_element, '__len__') and len(first_element) > 0:
                # Enhanced patterns might have nested structure
                nested_item = first_element[0]
                if isinstance(nested_item, tuple) and len(nested_item) == 2:
                    original_text = str(nested_item[0])
                    normalized_text = str(nested_item[1])
                    pos = text.find(original_text)
                    if pos != -1:
                        replacements.append((pos, len(original_text), normalized_text))

    # Sort replacements by position (reverse order to avoid index shifts)
    replacements.sort(key=lambda x: x[0], reverse=True)

    # Apply replacements from right to left
    result = text
    for pos, length, replacement in replacements:
        result = result[:pos] + replacement + result[pos + length:]

    return result

# Export the main functions and grammar
__all__ = [
    'comprehensive_grammar',
    'get_grammar',
    'normalize_text'
]