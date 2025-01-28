import pyparsing as pp
from pyparsing import Word, nums, Regex
from .number_grammar_reverse import wstart, wend, number_to_spoken

pp.ParserElement.setDefaultWhitespaceChars("\t\n")

def year_to_spoken(year: int) -> str:
    """
    Convert an integer year into Norwegian spoken format:
    - 1980 -> "nitten åtti"
    - 1904 -> "nitten hundre og fire"
    - 2001 -> "to tusen og én"
    """
    if not (0 < year < 3000):
        return number_to_spoken(year)

    # 2000-2099: Special millennium format
    if 2000 <= year <= 2099:
        if year == 2000:
            return "to tusen"
        remainder = year - 2000
        if remainder == 1:
            return "to tusen og én"  # Special case for 2001
        return f"to tusen og {compress_below_100(remainder)}"

    # 1900-1999: 20th century format
    if 1900 <= year <= 1999:
        remainder = year - 1900
        if remainder == 0:
            return "nitten hundre"
            
        # Handle years like 1980 (1900 + 80)
        if remainder >= 10 and remainder % 10 == 0:
            return f"nitten {compress_below_100(remainder)}"
            
        # Regular 1900s format
        return f"nitten hundre og {compress_below_100(remainder)}"

    return number_to_spoken(year)

def compress_below_100(num: int) -> str:
    """Convert numbers < 100 to compressed Norwegian format"""
    from .number_grammar_reverse import ONES, TEENS, TENS
    
    if num < 10:
        return ONES[num]
    if num < 20:
        return TEENS[num]
    
    tens = (num // 10) * 10
    ones = num % 10
    return TENS[tens] + (ONES[ones] if ones != 0 else "")
year_pattern = Regex(r"\b(\d{4})([.,?!:;])?(?!\d)")

def parse_year_with_punctuation(t):
    raw = t[0]              # e.g. "2010."
    digits = t[1]           # "2010"
    punct = t[2] if len(t) > 2 else ""  # "."

    spelled_year = year_to_spoken(int(digits))  # "to tusen og ti"
    return (raw, spelled_year + punct)   

yeargrammar_reverse = (
    pp.Regex(r"(\d{4})([.,?!:;])?(?!\d)")
    .setParseAction(parse_year_with_punctuation)
)

#yeargrammar_reverse = wstart + year_pattern + wend.setParseAction(lambda s, l, t: l)

if __name__ == "__main__":
    tests = ["1980", "1904", "2001", "2000", "1999","2024,"]
    for test in tests:
        res = yeargrammar_reverse.parseString(test)
        print(f"{test} => {res[0][1]}")