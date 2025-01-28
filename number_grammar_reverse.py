import pyparsing as pp
from pyparsing import Word, nums, oneOf, Suppress,originalTextFor,Combine,Keyword,OneOrMore, Regex
from .year_grammar_reverse import yeargrammar_reverse, year_to_spoken
from .number_grammar_reverse import wstart, wend, number_to_spoken
import re
pp.ParserElement.setDefaultWhitespaceChars("\t\n")

# We'll define a small dictionary from integer day -> "første" / "andre" / etc.
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

months = {
    1: "januar",
    2: "februar",
    3: "mars",
    4: "april",
    5: "mai",
    6: "juni",
    7: "juli",
    8: "august",
    9: "september",
    10: "oktober",
    11: "november",
    12: "desember",
}

def day_to_ordinal(day: int) -> str:
    """Always returns the first ordinal form from ordinals_dict."""
    if day in ordinals_dict:
        return ordinals_dict[day][0]
    
    # For days not in dictionary (though our dict covers 1-31)
    tens = (day // 10) * 10
    ones = day % 10
    if tens >= 20:
        return f"{number_to_spoken(tens).rstrip('e')}{day_to_ordinal(ones)}"
    return f"{number_to_spoken(day)}ende"  # Fallback pattern

def numeric_month_to_name(m: int) -> str:
    """Convert 1 => 'januar', 12 => 'desember'"""
    return months.get(m, str(m))

###############################################################################
# 1) Grammar to match typical "3. juni" or "03.06.2022", etc.
###############################################################################
# We'll keep it simple: dd. monthname [yyyy], or dd.mm.yyyy
digit = Word(nums)

# Match pattern1: "3. juni"
pattern1 = pp.Regex(r"(\d{1,2})\.\s*(januar|februar|mars|april|mai|juni|juli|august|september|oktober|november|desember)\b\.?")# e.g. group(1) = day, group(2) = monthName, group(3) = optional year

def parse_pattern1(t):
    # t[0] is the entire match
    import re
    m = re.match(r"(\d{1,2})\.\s*([^\s]+)(?:\s+(\d{4}))?", t[0])
    if not m:
        return (t[0], t[0])  # fallback
    day_str = m.group(1)
    month_str = m.group(2)
    year_str = m.group(3) if m.group(3) else None

    day_val = int(day_str)
    # Convert day to ordinal
    day_spoken = day_to_ordinal(day_val)
    # The month is already spelled out, just keep it
    spoken = f"{day_spoken} {month_str}"
    # If there's a year
    if year_str:
        from .year_grammar_reverse import year_to_spoken
        yval = int(year_str)
        spoken_year = year_to_spoken(yval)
        spoken += f" {spoken_year}"
    return (t[0], spoken)

pattern1_expr = pattern1.setParseAction(parse_pattern1)

# Match pattern2: "dd.mm.yyyy" or "dd.mm"
pattern2 = pp.Regex(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?")
def parse_pattern2(t):
    import re
    m = re.match(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?", t[0])
    if not m:
        return (t[0], t[0])
    day_val = int(m.group(1))
    month_val = int(m.group(2))
    year_val = m.group(3)
    day_spoken = day_to_ordinal(day_val)
    month_spoken = numeric_month_to_name(month_val)
    out = f"{day_spoken} i {month_spoken}"
    if year_val:
        from .year_grammar_reverse import year_to_spoken
        out += " " + year_to_spoken(int(year_val))
    return (t[0], out)

pattern2_expr = pattern2.setParseAction(parse_pattern2)

ordinal_expr = (
    Word(nums) 
    + Suppress(".-")
).setParseAction(
    lambda t: f"{ordinals_dict[int(t[0])][0]}"
)





klokka_time_expr = pp.Regex(r"(?i)\b(klokka|klokken)\s+(\d{1,2})\.(\d{1,2})([.,?!:;])?(?!\d)")
def parse_klokka_time(t):
    """
    Examples:
      - "Klokka 17.12" => "Klokka sytten tolv"
      - "klokken 8.30" => "klokken åtte tretti"
    Preserves the exact casing of “klokka” or “klokken” from the input.
    """
    raw = t[0]               
    match = re.search(r"(?i)\b(klokka|klokken)\s+(\d{1,2})\.(\d{1,2})([.,?!:;])?(?!\d)", raw)
    if not match:
        return (raw, raw)

    # This is the exact substring the user typed: "Klokka", "klokka", "Klokken", "klokken", etc.
    klokkeword = match.group(1)

    hour = int(match.group(2))
    minute = int(match.group(3))
    hour_spelled = number_to_spoken(hour)
    minute_spelled = number_to_spoken(minute)

    return (raw, f"{klokkeword} {hour_spelled} {minute_spelled}")

klokka_time_expr.setParseAction(parse_klokka_time)





klokka_time_expr2 = pp.Regex(r"(?i)\b(klokka|klokken)\s+(\d{1,2})\:(\d{1,2})([.,?!:;])?(?!\d)")
def parse_klokka_time(t):
    """
    Examples:
      - "Klokka 17:12" => "Klokka sytten tolv"
      - "klokken 8:30" => "klokken åtte tretti"
    Preserves the exact casing of “klokka” or “klokken” from the input.
    """
    raw = t[0]               
    match = re.search(r"(?i)\b(klokka|klokken)\s+(\d{1,2})\:(\d{1,2})([.,?!:;])?(?!\d)", raw)
    if not match:
        return (raw, raw)

    # This is the exact substring the user typed: "Klokka", "klokka", "Klokken", "klokken", etc.
    klokkeword = match.group(1)

    hour = int(match.group(2))
    minute = int(match.group(3))
    hour_spelled = number_to_spoken(hour)
    minute_spelled = number_to_spoken(minute)

    return (raw, f"{klokkeword} {hour_spelled} {minute_spelled}")

klokka_time_expr2.setParseAction(parse_klokka_time)






dategrammar_reverse = (
    wstart
    + (klokka_time_expr2 ^klokka_time_expr ^pattern1_expr ^ pattern2_expr)
    + wend.setParseAction(lambda s, l, t: l)
)
