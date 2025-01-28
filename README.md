# Text Normalization Using PyParsing

This script normalizes text inputs by applying specific grammatical rules using the [PyParsing](https://pypi.org/project/pyparsing/) library. It is designed to handle and standardize various formats, such as years, dates, and numbers, converting them into a spoken Norwegian format.

## Still under development
- **Edge Cases** some of the edge cases do **not** work

## Overview

The script defines several grammars for parsing and normalizing text:
- **Year Grammar:** Converts years into a spoken format.
- **Date Grammar:** Converts dates into a more descriptive format.
- **Number Grammar:** Converts numbers into their word equivalents.
- **Abbriviation Grammar:** Matches abbriviations and extends them.

## Features

- **Grammatical Parsing:** Modular grammar definitions for extensibility.
- **Normalization:** A `normalize` function processes input strings and applies the relevant grammar.


## Installation

1. Install Python (3.8 or later recommended).
2. Install the required library:
   ```bash
   pip install pyparsing
   ```

## How to use


```python
import pyparsing as pp
from pyparsing import Word, printables, alphas8bit

wordgrammar = Word(printables + alphas8bit)

norm_grammar = (
    abbrevgrammar_reverse 
    ^ dategrammar_reverse
    ^ yeargrammar_reverse
    ^ numbergrammar_reverse 
    ^ wordgrammar
)
def normalize(mystring, grammar):
    returnstring = ""

    parsed = grammar.searchString(mystring)
    
    for i, x in enumerate(parsed):
        if DEBUG:
            print(f"[TOKEN {i}] Raw: {x!r}")
            
        if len(x) == 2:

            returnstring += str(x[0][1]) + " "
        else:

            returnstring += str(x[0]) + " "


        
    return returnstring[:-1]
````
```python
text = "YOUR TEXT"
normalize(text,norm_grammar)
```
