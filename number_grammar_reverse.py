import pyparsing as pp
from pyparsing import Word, nums, WordStart, WordEnd, Combine, Suppress, OneOrMore, Optional, Keyword, originalTextFor, oneOf, Group, Regex
import re
# We replicate some definitions so that everything is in one file:
pp.ParserElement.setDefaultWhitespaceChars("\t\n")
wstart = WordStart()
wend = WordEnd()
WS = pp.Suppress(" ")

"""
1) A helper function to spell out a non-negative integer in Norwegian
##############################################################################
"""
ONES = [
    "null",  # 0
    "en",    # 1
    "to",    # 2
    "tre",   # 3
    "fire",  # 4
    "fem",   # 5
    "seks",  # 6
    "sju",   # 7
    "åtte",  # 8
    "ni",    # 9
]
TEENS = {
    10: "ti",
    11: "elleve",
    12: "tolv",
    13: "tretten",
    14: "fjorten",
    15: "femten",
    16: "seksten",
    17: "sytten",
    18: "atten",
    19: "nitten",
}
TENS = {
    20: "tjue",
    30: "tretti",
    40: "førti",
    50: "femti",
    60: "seksti",
    70: "sytti",
    80: "åtti",
    90: "nitti",
}

def number_to_spoken(num: int) -> str:
    if num == 0:
        return "null"

    parts = []

    # Handle millions
    millions = num // 1_000_000
    remainder = num % 1_000_000
    if millions > 0:
        if millions == 1:
            parts.append("en million")
        else:
            parts.append(f"{number_to_spoken(millions)} millioner")
        #if remainder > 0:
        #    parts.append("og")

    # Handle thousands
    thousands = remainder // 1000
    remainder = remainder % 1000
    if thousands > 0:
        if thousands == 1:
            parts.append("tusen")
        else:
            parts.append(f"{number_to_spoken(thousands)} tusen")
        if remainder > 0:
            parts.append("og")

    # Handle hundreds
    hundreds = remainder // 100
    remainder2 = remainder % 100
    if hundreds > 0:
        if hundreds == 1:
            parts.append("ett hundre")
        else:
            parts.append(f"{number_to_spoken(hundreds)} hundre")
        if remainder2 > 0:
            parts.append("og")

    # Handle remainder under 100
    if remainder2 > 0:
        if remainder2 < 10:
            parts.append(ONES[remainder2])
        elif remainder2 < 20:
            parts.append(TEENS[remainder2])
        else:
            tens_part = (remainder2 // 10) * 10
            ones_part = remainder2 % 10
            parts.append(TENS[tens_part])
            if ones_part > 0:
                parts.append(ONES[ones_part])

    return " ".join(parts).replace("  ", " ").strip()


###############################################################################
# 2) Define a grammar that matches up to 6-digit numbers and returns spelled-out
# ##############################################################################
# e.g. "2500" -> "to tusen fem hundre" (or you might want "to tusen og fem hundre")

integer_token = Word(nums).setParseAction(lambda t: (t[0], number_to_spoken(int(t[0]))))

numbergrammar_reverse = (
    wstart + integer_token + wend.setParseAction(lambda s, l, t: l)
)

###############################################################################
# 3) If you want more advanced tokens for decimals (“3,14” => “tre komma fjorten”),
#    or half thousands (“2,5” => “to og en halv”), you can add them here:
# ##############################################################################

# Spaced numbers parser
spaced_number = Combine(Word(nums) + OneOrMore(WS + Word(nums)))
spaced_number.setParseAction(lambda t: (t[0], number_to_spoken(int(t[0].replace(' ', '')))))

# Percentages parser
percent_decimal_expr = pp.Regex(r'\d+,\d+%')
percent_integer_expr = pp.Regex(r'\d+%')

def parse_percent_decimal(t):
    num_str = t[0].replace('%', '')
    whole, frac = num_str.split(',')
    return (t[0], f"{number_to_spoken(int(whole))} komma {number_to_spoken(int(frac))} prosent")

def parse_percent_integer(t):
    num_str = t[0].replace('%', '')
    return (t[0], f"{number_to_spoken(int(num_str))} prosent")

percent_decimal_expr.setParseAction(parse_percent_decimal)
percent_integer_expr.setParseAction(parse_percent_integer)

# Combined percentage expression
percent_expr = percent_integer_expr | percent_decimal_expr

# Decimals parser
decimal_expr = pp.Regex(r'\d+,\d+')
def decimal_to_spoken(t):
    text = t[0]
    whole, frac = text.split(',')
    if frac == '5':
        return (text, f"{number_to_spoken(int(whole))} og en halv")
    return (text, f"{number_to_spoken(int(whole))} komma {number_to_spoken(int(frac))}")
decimal_expr.setParseAction(decimal_to_spoken)



###############################################################################
# New Patterns: Ranges and -tiden
###############################################################################
# 12-14 → "tolv til fjorten"
range_expr = Combine(Word(nums) + Suppress("-") + Word(nums))
range_expr.setParseAction(
    lambda t: f"{number_to_spoken(int(t[0][0]))} til {number_to_spoken(int(t[0][1]))}"
)

time_expr = Combine(
    Word(nums, exact=2) 
    + Suppress(".") 
    + Word(nums, exact=2)
).setParseAction(
    lambda t: f"{number_to_spoken(int(t[0][:2]))} {number_to_spoken(int(t[0][3:5]))}"
)

tiden_expr = (
    time_expr
    + Suppress("-") 
    + oneOf("tiden tida")
).setParseAction(lambda t: f"{t[0]}-{t[1]}")


def parse_parenthesized_number(t):
    raw_digits = t.digits  # e.g. "20"
    spelled = number_to_spoken(int(raw_digits))  # "tjue"
    # Return a 2-tuple: (original, replaced)
    return (f"({raw_digits})", f"({spelled})")

parenthesized_number = (
    pp.Literal("(").suppress()
    + pp.Word(pp.nums)("digits")
    + pp.Literal(")").suppress()
)

def parse_parenthesized_number(t):
    raw_digits = t.digits  # e.g. "20"
    spelled = number_to_spoken(int(raw_digits))  # "tjue"
    # Return a 2-tuple: (original, replaced)
    return (f"({raw_digits})", f"({spelled})")

parenthesized_number.setParseAction(parse_parenthesized_number)

digit_tiden_expr = pp.Regex(r"(\d+)-(tiden|tida)").setParseAction(
    lambda t: (t[0], f"{number_to_spoken(int(t[0].split('-')[0]))}-{t[0].split('-')[1]}")
)

two_part_version_expr = pp.Regex(r"\b(\d+)\.(\d+)\b")

def parse_two_part_version(t):
    # e.g. "2.10" => "2" and "10"
    import re
    raw = t[0]
    m = re.match(r"(\d+)\.(\d+)", raw)
    if not m:
        return (raw, raw)
    left = int(m.group(1))   # 2
    right = int(m.group(2))  # 10
    from number_grammar_reverse import number_to_spoken
    # If your desired style is literally “to ti”:
    spelled = f"{number_to_spoken(left)} {number_to_spoken(right)}"
    return (raw, spelled)

two_part_version_expr.setParseAction(parse_two_part_version)

#######################
# Updated grammar with priority order
###############################################################################
# Grammar with priority
numbergrammar_reverse = (
    wstart + (
        parenthesized_number |
        two_part_version_expr |
        range_expr |
        digit_tiden_expr |
        percent_expr |
        spaced_number |
        decimal_expr |
        Word(nums).setParseAction(lambda t: (t[0], number_to_spoken(int(t[0]))))
    ) + wend
)

###############################################################################

__all__ = ["numbergrammar_reverse", "number_to_spoken"]




