import pyparsing as pp
from pyparsing import Word, nums, Regex 
from .number_grammar_reverse import wstart, wend, number_to_spoken
import re





ordinals_dict = {
    1: ["første", "fyrste"],  # you may pick one: "første"
    2: ["andre"],
    3: ["tredje"],
    4: ["fjerde"],
    5: ["femte"],
    6: ["sjette"],
    7: ["sjuende", "syvende"],
    8: ["åttende", "åttande"],
    9: ["niende", "niande"],
    10: ["tiende", "tiande"],
    11: ["ellevte"],
    12: ["tolvte"],
    13: ["trettende", "trettande"],
    14: ["fjortende", "fjortande"],
    15: ["femtende", "femtande"],
    16: ["sekstende", "sekstande"],
    17: ["syttende", "syttande"],
    18: ["attende", "attande"],
    19: ["nittende", "nittande"],
    20: ["tjuende", "tyvende", "tjuande"],
    21: ["tjueførste", "tjuefyrste", "énogtyvende", "énogtjuende"],
    22: ["tjueandre", "toogtyvende", "toogtjuende"],
    23: ["tjuetredje", "treogtyvende", "treogtjuende"],
    24: ["tjuefjerde", "fireogtyvende", "fireogtjuende"],
    25: ["tjuefemte", "femogtyvende", "femogtjuende"],
    26: ["tjuesjette", "seksogtyvende", "seksogtjuende"],
    27: ["tjuesjuende", "tjuesyvende", "syvogtyvende", "syvogtjuende"],
    28: ["tjueåttende", "tjueåttande", "åtteogtyvende", "åtteogtjuende"],
    29: ["tjueniende", "tjueniande", "niogtyvende", "niogtjuende"],
    30: ["trettiende", "trettiande"],
    31: ["trettiførste", "trettifyrste", "énogtrettiende"],
}


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



year_pattern = pp.Regex(r"(\d{4})([.,?!:;])?(?!\d)")

def parse_year_with_punctuation(tokens):
    """
    tokens[0] is the entire matched text, e.g. "2004,".
    We'll do re.match inside this function to split out digits vs. punctuation.
    """
    raw = tokens[0]  # "2004,"

    match = re.match(r"(\d{4})([.,?!:;])?(?!\d)", raw)
    if not match:
        # fallback if something unexpected
        return raw


    digits = match.group(1)            # "2004"
    punct  = match.group(2) or ""      # "," or ""
    
    spelled_year = year_to_spoken(int(digits))


    return (raw, spelled_year + punct) 

ordinal_expr_general = pp.Regex(r"\b(\d+)\.(?!\d)(.*)?")


def parse_ordinal_expr_general(t):
    # t[0] is the entire match: e.g. "15. plass"
    import re
    raw = t[0]
    match = re.match(r"(\d+)\.(?!\d)(.*)?", raw)
    if not match:
        return (raw, raw)  # fallback
    
    digit_str = match.group(1)    # "15"
    trailing   = match.group(2) or ""  # " plass"
    
    # Spell out ordinal
    val = int(digit_str)
    from Normalizer.number_grammar_reverse import number_to_spoken
    
    # If you have a dictionary up to 31, do that; else fallback:
    if val in ordinals_dict:
        spelled_ordinal = ordinals_dict[val][0]
    else:
        spelled_ordinal = f"{number_to_spoken(val)}ende"
    
    # Suppose you want to keep the original period as well
    # by inserting it back before trailing text:
    # e.g. "femtende" + "." + " plass"
    new_text = f"{spelled_ordinal}{trailing}"
    return (raw, new_text)

ordinal_expr_general.setParseAction(parse_ordinal_expr_general)

thousand_separated_expr = pp.Regex(r"\d{1,3}(\.\d{3})+")
def parse_thousand_separated(t):
    # Remove all dots:
    numeric_str = t[0].replace(".", "")
    # Convert to int and then to spoken form
    spelled = number_to_spoken(int(numeric_str))
    return (t[0], spelled)

thousand_separated_expr.setParseAction(parse_thousand_separated)


#yeargrammar_reverse = wstart + year_pattern + wend.setParseAction(lambda s, l, t: l)


def wend_parse_action(string, location, tokens):
    return tokens + [location]


year_pattern.setParseAction(parse_year_with_punctuation)

yeargrammar_reverse = (
    wstart
    + (year_pattern ^ thousand_separated_expr ^ ordinal_expr_general )
    + wend.setParseAction(wend_parse_action)
)

