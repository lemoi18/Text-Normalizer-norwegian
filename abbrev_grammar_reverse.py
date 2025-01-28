import pyparsing as pp
from pyparsing import oneOf, Literal
from .number_grammar_reverse import wstart, wend, WS  # We reuse helper tokens
# ^ Make sure to point to whichever file you place your shared definitions in.
#   Or, if you want a self-contained file, define wstart, wend there as well.

# change Pyparsing's default whitespace handling
pp.ParserElement.setDefaultWhitespaceChars("\t\n")

###############################################################################
# 1) Reverse dictionary: from abbreviation -> full spelled-out form(s)
#
#    Since your original "abbrevdict" mapped spelled-out to abbreviations,
#    we now want to map the abbreviations back to spelled-out.
###############################################################################
abbrevdict_forward = {
    "blant annet": "bl.a.",
    "blant anna": "bl.a.",
    "cirka": "ca.",
    "sirka": "ca.",
    "centimeter": "cm",
    "det vil si": "dvs.",
    "et cetera": "etc.",
    "for eksempel": "f.eks.",
    "fylkesvei": "fv.",
    "kilobyte": "kB",
    "kilometer i timen": "km/t",
    "kilowattimer": "kWh",
    "klokka": "kl.",
    "klokken": "kl.",
    "mellom anna": "m.a.",
    "megabyte": "MB",
    "millimeter": "mm",
    "og liknende": "o.l.",
    "parts per million": "p.p.m",
    "riksvei": "rv.",
    "til dømes": "t.d.",
    "terrawattimer": "TWh",
    "jamfør": "jf.",
    "det vil seie": "dvs.",
    "fylkesveg": "fv.",
    "jevnfør": "jf.",
    "kilowattimar": "kWh",
    "og lignende": "o.l.",
    "og liknande": "o.l.",
    "riksveg": "rv.",
    "terawattimar": "TWh",
    "terawattimer": "TWh",
    "dekar": "daa",
    "desibel": "dB",
    "desiliter": "dl",
    "desimeter": "dm",
    "eller liknende": "e.l.",
    "eller lignende": "e.l.",
    "eller liknande": "e.l.",
    "fra og med": "f.o.m.",
    "gigabyte": "GB",
    "gigawatt": "GW",
    "kilobit": "kb",
    "kilo": "kg",
    "kilogram": "kg",
    "kilometer": "km",
    "kilovolt": "kV",
    "kvadratmeter": "kvm",
    "kilowatt": "kW",
    "megabit": "Mb",
    "milliliter": "ml",
    "millivolt": "mV",
    "megavolt": "MV",
    "milliwatt": "mW",
    "megawatt": "MW",
    "og så bortetter": "osb.",
    "og så vidare": "osv.",
    "og så videre": "osv.",
    "på grunn av": "pga.",
    "petabyte": "PB",
    "petawatt": "PW",
    "terabyte": "TB",
    "terrabyte": "TB",
    "til og med": "t.o.m.",
    "terawatt": "TW",
    "terrawatt": "TW",
    "til eksempel": "t.eks.",
}

# Inverse dictionary: abbreviation -> (preferred) spelled-out
# Because multiple keys map to the same abbreviation, we must pick one
# or store them as a list. Here we pick the "first" spelled-out we find:
abbrevdict_reverse = {}
for spelled_out, abbr in abbrevdict_forward.items():
    if abbr not in abbrevdict_reverse:
        # if there's a collision "bl.a." from multiple entries,
        # we store them all in a list or pick one:
        abbrevdict_reverse[abbr] = [spelled_out]
    else:
        abbrevdict_reverse[abbr].append(spelled_out)

###############################################################################
# 2) Define grammar that recognizes these abbreviations and returns spelled-out
###############################################################################
abbrev_keys = list(abbrevdict_reverse.keys())  # e.g. ["bl.a.", "ca.", ...]
abbrev_match = oneOf(abbrev_keys)

def expand_abbrev(t):
    """Given a token (like 'bl.a.'), return one or all possible expansions."""
    token = t[0]
    expansions = abbrevdict_reverse[token]  # possibly multiple
    # For "production-ready," decide how to pick expansions. We'll pick the first:
    return expansions[0]

simpleabbrev_reverse = abbrev_match.setParseAction(lambda t: (t[0], expand_abbrev(t)))

###############################################################################
# 3) Put it all together in a final grammar. 
###############################################################################
# We keep the same wstart + wend boundaries for symmetrical usage.
abbrevgrammar_reverse = (
    wstart
    + simpleabbrev_reverse
    + wend.setParseAction(lambda s, l, t: l)
)

if __name__ == "__main__":
    test_sent = "Hun jobbet ca. tre år i bedriften osv. før hun sluttet."
    # searchString will find all matches
    found = abbrevgrammar_reverse.searchString(test_sent)
    print("Original:", test_sent)
    print("Matches and expansions:", found)
    # If you want to do replacements line-by-line or token-by-token,
    # you can do so by scanning from left to right.
