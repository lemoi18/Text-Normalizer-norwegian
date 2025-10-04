import pyparsing as pp
from pyparsing import Word, nums, Regex, Suppress, Combine, Literal, Optional, oneOf
from number_grammar_reverse import number_to_spoken, wstart, wend
from year_grammar_reverse import year_to_spoken
import re

# Change Pyparsing's default whitespace handling
pp.ParserElement.setDefaultWhitespaceChars("\t\n")

###############################################################################
# 1. Enhanced Range Patterns (fix for "10-15" -> "ti til femten")
###############################################################################

def parse_enhanced_range(tokens):
    """Parse range patterns like '10-15', '2010-2020', '(10-15)', etc."""
    raw = tokens[0]

    # Remove brackets and extract the core range with any trailing symbols
    # Keep track of trailing symbols like % to handle them appropriately
    core_match = re.match(r'([\(\[]?)(\d+(?:[.,]\d+)?\s*-\s*\d+(?:[.,]\d+)?)([\)\]]?)(\s*%?)', raw)
    if core_match:
        prefix_bracket = core_match.group(1)
        range_part = core_match.group(2)
        suffix_bracket = core_match.group(3)
        trailing_symbols = core_match.group(4)
    else:
        # Fallback: just remove brackets
        range_part = re.sub(r'^[\(\[]+|[\)\]]+$', '', raw)
        trailing_symbols = ''
        prefix_bracket = ''
        suffix_bracket = ''

    # Try to extract the numbers from the range part
    match = re.match(r'(\d+(?:[.,]\d+)?)\s*-\s*(\d+(?:[.,]\d+)?)', range_part)
    if match:
        num1_str = match.group(1)
        num2_str = match.group(2)

        # Remove decimal separators for processing
        num1_clean = num1_str.replace(',', '.')
        num2_clean = num2_str.replace(',', '.')

        try:
            # Try to parse as integers first
            if '.' not in num1_clean and '.' not in num2_clean:
                num1 = int(num1_clean)
                num2 = int(num2_clean)

                # Special handling for year ranges
                if num1 >= 1000 and num2 >= 1000 and num1 <= 9999 and num2 <= 9999:
                    year1 = year_to_spoken(num1)
                    year2 = year_to_spoken(num2)
                    return (raw, f"{prefix_bracket}{year1} til {year2}{trailing_symbols}{suffix_bracket}")

                # Regular number ranges
                num1_spoken = number_to_spoken(num1)
                num2_spoken = number_to_spoken(num2)
                return (raw, f"{prefix_bracket}{num1_spoken} til {num2_spoken}{trailing_symbols}{suffix_bracket}")

            # Handle decimal ranges
            num1 = float(num1_clean)
            num2 = float(num2_clean)

            if num1 == int(num1) and num2 == int(num2):
                # Actually whole numbers
                num1_spoken = number_to_spoken(int(num1))
                num2_spoken = number_to_spoken(int(num2))
                return (raw, f"{prefix_bracket}{num1_spoken} til {num2_spoken}{trailing_symbols}{suffix_bracket}")

            # True decimals - simplified approach
            return (raw, raw)  # Keep original for complex decimals

        except (ValueError, OverflowError):
            return (raw, raw)

    return (raw, raw)

# Enhanced range pattern
enhanced_range_expr = pp.Regex(r'[\(\[]?\d+(?:[.,]\d+)?\s*-\s*\d+(?:[.,]\d+)?[\)\]]?\s*%?')
enhanced_range_expr.setParseAction(parse_enhanced_range)

###############################################################################
# 2. Unicode Fractions Support
###############################################################################

unicode_fractions = {
    '¼': 'en fjerdedel',
    '½': 'en halv',
    '¾': 'tre fjerdedeler',
    '⅐': 'en sjuendedel',
    '⅑': 'en niendedel',
    '⅒': 'en tiendedel',
    '⅓': 'en tredjedel',
    '⅔': 'to tredjedeler',
    '⅕': 'en femtedel',
    '⅖': 'to femtedeler',
    '⅗': 'tre femtedeler',
    '⅘': 'fire femtedeler',
    '⅙': 'en sjettedel',
    '⅚': 'fem sjettedeler',
    '⅛': 'en åttendedel',
    '⅜': 'tre åttendedeler',
    '⅝': 'fem åttendedeler',
    '⅞': 'syv åttendedeler'
}

def parse_unicode_fraction(tokens):
    """Parse Unicode fraction characters."""
    raw = tokens[0]
    result_parts = []

    for char in raw:
        if char in unicode_fractions:
            result_parts.append(unicode_fractions[char])
        else:
            result_parts.append(char)

    result = ''.join(result_parts)
    return (raw, result)

unicode_fraction_expr = pp.Regex(r'[¼½¾⅐⅑⅒⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]')
unicode_fraction_expr.setParseAction(parse_unicode_fraction)

###############################################################################
# 3. Enhanced Date Patterns with Different Separators
###############################################################################

def parse_slash_date(tokens):
    """Parse date with slash separator like '3/6/2023'."""
    raw = tokens[0]
    match = re.match(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', raw)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = match.group(3)

        from date_grammar_reverse import day_to_ordinal, numeric_month_to_name

        day_spoken = day_to_ordinal(day)
        month_spoken = numeric_month_to_name(month)

        result = f"{day_spoken} {month_spoken}"

        if year:
            year_int = int(year)
            if len(year) == 2:  # Convert 2-digit year to 4-digit
                year_int = 2000 + year_int if year_int <= 30 else 1900 + year_int
            result += f" {year_to_spoken(year_int)}"

        return (raw, result)

    return (raw, raw)

def parse_dash_date(tokens):
    """Parse date with dash separator like '06-03-2023'."""
    raw = tokens[0]
    match = re.match(r'(\d{1,2})-(\d{1,2})(?:-(\d{2,4}))?', raw)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = match.group(3)

        from date_grammar_reverse import day_to_ordinal, numeric_month_to_name

        day_spoken = day_to_ordinal(day)
        month_spoken = numeric_month_to_name(month)

        result = f"{day_spoken} {month_spoken}"

        if year:
            year_int = int(year)
            if len(year) == 2:  # Convert 2-digit year to 4-digit
                year_int = 2000 + year_int if year_int <= 30 else 1900 + year_int
            result += f" {year_to_spoken(year_int)}"

        return (raw, result)

    return (raw, raw)

def parse_yearfirst_date(tokens):
    """Parse year-first date like '2023.06.03'."""
    raw = tokens[0]
    match = re.match(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', raw)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        from date_grammar_reverse import day_to_ordinal, numeric_month_to_name

        day_spoken = day_to_ordinal(day)
        month_spoken = numeric_month_to_name(month)
        year_spoken = year_to_spoken(year)

        result = f"{day_spoken} {month_spoken} {year_spoken}"
        return (raw, result)

    return (raw, raw)

# Date patterns with different separators
slash_date_expr = pp.Regex(r'\d{1,2}/\d{1,2}(?:/\d{2,4})?')
slash_date_expr.setParseAction(parse_slash_date)

dash_date_expr = pp.Regex(r'\d{1,2}-\d{1,2}(?:-\d{2,4})?')
dash_date_expr.setParseAction(parse_dash_date)

yearfirst_date_expr = pp.Regex(r'\d{4}\.\d{1,2}\.\d{1,2}')
yearfirst_date_expr.setParseAction(parse_yearfirst_date)

###############################################################################
# 4. Enhanced Scientific Notation
###############################################################################

def parse_scientific_notation(tokens):
    """Parse scientific notation like '1,5×10³' or '2.5e10'."""
    raw = tokens[0]

    # Match patterns like "1,5×10³", "2.5e10", "3,14·10²", "1E-6"
    # Try the e-notation format first
    e_match = re.match(r'([0-9]+(?:[.,][0-9]+)?)\s*([eE])\s*([-]?[0-9]+)', raw)
    if e_match:
        base = e_match.group(1).replace(',', '.')
        exp_str = e_match.group(3)
        try:
            base_num = float(base)
            exp_num = int(exp_str)
            # Convert to spoken format
            if base_num == int(base_num):
                base_spoken = number_to_spoken(int(base_num))
            else:
                base_spoken = f"{number_to_spoken(int(base_num))} komma {number_to_spoken(int((base_num % 1) * 10))}"

            exp_spoken = number_to_spoken(abs(exp_num))
            if exp_num < 0:
                return (raw, f"{base_spoken} ganger ti opphøyd i minus {exp_spoken}")
            else:
                return (raw, f"{base_spoken} ganger ti opphøyd i {exp_spoken}")
        except (ValueError, OverflowError):
            return (raw, raw)

    # Fall back to the traditional format
    match = re.match(r'([0-9]+[.,]?[0-9]*)\s*[×x·*]\s*10*([⁰¹²³⁴⁵⁶⁷⁸⁹]+|[0-9]+)', raw)
    if match:
        base = match.group(1).replace(',', '.')
        exp_str = match.group(2)

        # Convert Unicode superscript to regular digits
        superscript_map = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
                          '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
        for super_char, digit in superscript_map.items():
            exp_str = exp_str.replace(super_char, digit)

        try:
            base_num = float(base)
            exp_num = int(exp_str)

            if base_num == int(base_num):
                base_spoken = number_to_spoken(int(base_num))
            else:
                base_spoken = f"{number_to_spoken(int(base_num))} komma {number_to_spoken(int((base_num % 1) * 10))}"

            exp_spoken = number_to_spoken(exp_num)
            return (raw, f"{base_spoken} ganger ti opphøyd i {exp_spoken}")

        except (ValueError, OverflowError):
            return (raw, raw)

    # Handle simple exponent notation like "2.5e10"
    match = re.match(r'([0-9]+[.,]?[0-9]*)[eE]([0-9]+)', raw)
    if match:
        base = match.group(1).replace(',', '.')
        exp = match.group(2)

        try:
            base_num = float(base)
            exp_num = int(exp)

            if base_num == int(base_num):
                base_spoken = number_to_spoken(int(base_num))
            else:
                base_spoken = f"{number_to_spoken(int(base_num))} komma {number_to_spoken(int((base_num % 1) * 10))}"

            exp_spoken = number_to_spoken(exp_num)
            return (raw, f"{base_spoken} ganger ti opphøyd i {exp_spoken}")

        except (ValueError, OverflowError):
            return (raw, raw)

    return (raw, raw)

scientific_notation_expr = pp.Regex(r'[0-9]+(?:[.,][0-9]+)?\s*[×x·*eE]\s*(?:10*)?[⁰¹²³⁴⁵⁶⁷⁸⁹]+|[0-9]+(?:[.,][0-9]+)?[eE][-]?[0-9]+')
scientific_notation_expr.setParseAction(parse_scientific_notation)

###############################################################################
# 5. Enhanced Mixed Number Patterns
###############################################################################

def parse_mixed_number(tokens):
    """Parse mixed numbers like '1 1/2'."""
    raw = tokens[0]
    match = re.match(r'(\d+)\s+(\d+)/(\d+)', raw)
    if match:
        whole = int(match.group(1))
        numerator = int(match.group(2))
        denominator = int(match.group(3))

        whole_spoken = number_to_spoken(whole)

        # Simple fraction mapping
        if denominator == 2:
            fraction_spoken = "en halv" if numerator == 1 else f"{number_to_spoken(numerator)} halvdeler"
        elif denominator == 4:
            fraction_spoken = "en fjerdedel" if numerator == 1 else f"{number_to_spoken(numerator)} fjerdedeler"
        elif denominator == 3:
            fraction_spoken = "en tredjedel" if numerator == 1 else f"{number_to_spoken(numerator)} tredjedeler"
        else:
            fraction_spoken = f"{number_to_spoken(numerator)}/{number_to_spoken(denominator)}"

        return (raw, f"{whole_spoken} og {fraction_spoken}")

    return (raw, raw)

mixed_number_expr = pp.Regex(r'\d+\s+\d+/\d+')
mixed_number_expr.setParseAction(parse_mixed_number)

###############################################################################
# 6. Enhanced Large Numbers
###############################################################################

def parse_large_number(tokens):
    """Parse and properly name very large numbers."""
    raw = tokens[0]
    num_str = raw.replace(' ', '').replace('.', '')

    try:
        num = int(num_str)

        if num >= 10**12:  # Trillion and above
            if num == 10**12:
                return (raw, "en billion")
            else:
                # Simplified approach for very large numbers
                return (raw, number_to_spoken(num))
        elif num >= 10**9:  # Billion
            if num == 10**9:
                return (raw, "en milliard")
            billions = num // 10**9
            remainder = num % 10**9
            if remainder == 0:
                return (raw, f"{number_to_spoken(billions)} milliarder" if billions > 1 else "en milliard")
            else:
                return (raw, f"{number_to_spoken(billions)} milliarder {number_to_spoken(remainder)}")
        else:
            return (raw, number_to_spoken(num))

    except (ValueError, OverflowError):
        return (raw, raw)

large_number_expr = pp.Regex(r'\d{9,}')
large_number_expr.setParseAction(parse_large_number)

###############################################################################
# 7. Combined Enhanced Grammar
###############################################################################

enhanced_grammar_reverse = (
    wstart
    + (
        enhanced_range_expr
        ^ unicode_fraction_expr
        ^ slash_date_expr
        ^ dash_date_expr
        ^ yearfirst_date_expr
        ^ scientific_notation_expr
        ^ mixed_number_expr
        ^ large_number_expr
    )
    + wend.setParseAction(lambda s, l, t: l)
)

# Export for use in other modules
__all__ = [
    'enhanced_grammar_reverse',
    'enhanced_range_expr',
    'unicode_fraction_expr',
    'slash_date_expr',
    'dash_date_expr',
    'yearfirst_date_expr',
    'scientific_notation_expr',
    'mixed_number_expr',
    'large_number_expr'
]