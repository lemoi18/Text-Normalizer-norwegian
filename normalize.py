#!/usr/bin/env python3
"""
Norwegian Text Normalizer - Main Interface

This module provides the main interface for Norwegian text normalization.
It includes both the simple normalize function (compatible with existing code)
and the enhanced normalize function with all pattern improvements.

The normalize function now includes all enhanced patterns by default,
making it the recommended choice for all use cases.
"""

import pyparsing as pp
from pyparsing import Word, printables, alphas8bit

# Import the integrated grammar system
from grammar import comprehensive_grammar, normalize_text as enhanced_normalize_text

# Legacy imports for backward compatibility
from number_grammar_reverse import numbergrammar_reverse, wstart, wend
from year_grammar_reverse import yeargrammar_reverse
from date_grammar_reverse import dategrammar_reverse
from abbrev_grammar_reverse import abbrevgrammar_reverse

# Backward compatibility grammar (original patterns)
wordgrammar = Word(printables + alphas8bit)
legacy_grammar = (
    abbrevgrammar_reverse
    ^ dategrammar_reverse
    ^ yeargrammar_reverse
    ^ numbergrammar_reverse
    ^ wordgrammar
)

def normalize(mystring, grammar=None, use_enhanced=True):
    """
    Normalize Norwegian text using comprehensive grammar patterns.

    This function normalizes Norwegian text by converting various patterns
    into their spoken Norwegian equivalents. By default, it uses the enhanced
    grammar with all pattern improvements.

    Args:
        mystring (str): The input string to normalize
        grammar: Optional custom grammar (defaults to comprehensive grammar)
        use_enhanced (bool): Whether to use enhanced patterns (default: True)

    Returns:
        str: Normalized string with patterns converted to spoken Norwegian

    Examples:
        >>> normalize("Møte kl. 15:30 den 3. juni 2023")
        'Møte klokka femten tretti den tredje juni to tusen og tjue tre'

        >>> normalize("Rapporten 2010-2020 viser 50% økning")
        'Rapporten tjue ti til tjue tjue viser femti prosent økning'

        >>> normalize("ca. 10-15 deltakere")
        'cirka ti til femten deltakere'
    """
    if not mystring or not isinstance(mystring, str):
        return mystring

    # Use enhanced normalization by default
    if use_enhanced and grammar is None:
        return enhanced_normalize_text(mystring)

    # Use custom grammar if provided
    if grammar is not None:
        returnstring = ""
        parsed = grammar.searchString(mystring)

        if not parsed:
            return mystring

        for i, x in enumerate(parsed):
            if len(x) == 2:
                returnstring += str(x[0][1]) + " "
            else:
                returnstring += str(x[0]) + " "

        return returnstring[:-1] if returnstring else mystring

    # Use legacy grammar for backward compatibility
    returnstring = ""
    parsed = legacy_grammar.searchString(mystring)

    if not parsed:
        return mystring

    for i, x in enumerate(parsed):
        if len(x) == 2:
            returnstring += str(x[0][1]) + " "
        else:
            returnstring += str(x[0]) + " "

    return returnstring[:-1] if returnstring else mystring

def normalize_legacy(mystring, grammar=None):
    """
    Legacy normalize function for backward compatibility.

    This function uses the original grammar patterns without enhanced features.
    It's maintained for backward compatibility with existing code.

    Args:
        mystring (str): The input string to normalize
        grammar: Optional custom grammar (defaults to legacy grammar)

    Returns:
        str: Normalized string using legacy patterns

    Note:
        This function is deprecated. Use normalize() instead, which now
        includes all enhanced patterns by default.
    """
    return normalize(mystring, grammar=grammar, use_enhanced=False)

def normalize_enhanced(mystring, grammar=None):
    """
    Enhanced normalize function with all pattern improvements.

    This function uses the comprehensive grammar with all enhanced patterns.
    It's equivalent to calling normalize() with default parameters.

    Args:
        mystring (str): The input string to normalize
        grammar: Optional custom grammar (defaults to comprehensive grammar)

    Returns:
        str: Normalized string with all enhanced patterns

    Note:
        This function is maintained for compatibility but normalize() now
        provides the same functionality by default.
    """
    return enhanced_normalize_text(mystring)

# Convenience aliases
normalize_text = normalize  # Main function alias
normalize_comprehensive = normalize_enhanced  # Enhanced function alias

# Export the main functions
__all__ = [
    'normalize',           # Main function (now enhanced by default)
    'normalize_legacy',    # Legacy function for backward compatibility
    'normalize_enhanced',  # Enhanced function alias
    'normalize_text',      # Convenience alias
    'normalize_comprehensive',  # Enhanced function alias
    'comprehensive_grammar',  # Access to the full grammar
    'legacy_grammar',      # Access to legacy grammar
]

# Module metadata
__version__ = '2.0.0'
__author__ = 'Norwegian Text Normalizer Team'
__description__ = 'Comprehensive Norwegian text normalization for TTS applications'