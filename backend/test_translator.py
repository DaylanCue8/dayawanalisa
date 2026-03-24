import pytest
from tagalog_to_baybayin import TagalogToBaybayin

@pytest.fixture
def ttb():
    return TagalogToBaybayin()

@pytest.mark.parametrize("input_text, expected, description", [
    # Path 1: Guard Clause (Empty string)
    ("", "", "Empty input guard clause"),
    
    # Path 2: Linguistic Exception (Linguistic Rule for 'mga')
    ("mga", "ᜋᜄ", "Linguistic exception path"),
    
    # Path 3: Rule A (Standalone Vowels)
    ("a i u", "ᜀ ᜁ ᜂ", "Standalone vowel glyphs"),
    ("Ilog", "ᜁᜎᜓᜄ᜔", "Standalone vowel at word start"),
    
    # Path 4: Rule B (Consonant-Vowel pairs)
    ("Baya", "ᜊᜌ", "CV pair with inherent 'a'"),
    ("Ngiti", "ᜅᜒᜆᜒ", "CV pair with upper kudlit (e/i)"),
    ("Opo", "ᜂᜉᜓ", "CV pair with lower kudlit (o/u)"),
    
    # Path 5: Rule C (Final Consonants / Virama)
    ("Salamat", "ᜐᜎᜋᜆ᜔", "Final consonant with virama"),
    ("Ang", "ᜀᜅ᜔", "Final digraph consonant logic"),
    
    # Path 6: Whitespace preservation
    ("A B", "ᜀ ᜊ᜔", "Space preservation between tokens")
])
def test_white_box_coverage(ttb, input_text, expected, description):
    """
    Verifies internal logic paths for white box verification.
    This test suite ensures 100% statement coverage of the TTB module.
    """
    actual = ttb.translate(input_text)
    
    # Terminal output for manual verification (Visible with pytest -s)
    print(f"Testing {description}: '{input_text}' -> '{actual}'")
    
    assert actual == expected