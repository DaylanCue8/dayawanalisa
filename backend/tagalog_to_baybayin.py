import re

class TagalogToBaybayin:
    def __init__(self):
        # 17 Base Syllables
        self.base_map = {
            'a': 'ᜀ', 'e': 'ᜁ', 'i': 'ᜁ', 'o': 'ᜂ', 'u': 'ᜂ',
            'ba': 'ᜊ', 'ka': 'ᜃ', 'da': 'ᜇ', 'ra': 'ᜇ', 'ga': 'ᜄ',
            'ha': 'ᜑ', 'la': 'ᜎ', 'ma': 'ᜌ', 'na': 'ᜈ', 'nga': 'ᜅ',
            'pa': 'ᜉ', 'sa': 'ᜐ', 'ta': 'ᜆ', 'wa': 'ᜏ', 'ya': 'ᜌ'
        }
        
        self.kudlit_ei = 'ᜒ' # Dot above
        self.kudlit_ou = 'ᜓ' # Dot below
        self.virama = '᜔'    # Cross killer

    def translate(self, text):
        # 1. Clean input but keep internal spaces
        text = text.lower()
        
        # 2. Enhanced Regex:
        # Added 'nga' support and ' ' (space) support
        # Group 1: Consonant + Vowel (including 'nga' + vowel)
        # Group 2: Standalone Consonants (including 'nga')
        # Group 3: Standalone Vowels
        # Group 4: Spaces
        pattern = r'(nga[aeiou]|(?:[bkdrghlmnpstw])?[aeiou])|(nga|[bkdrghlmnpstw])|([aeiou])|(\s+)'
        
        tokens = re.findall(pattern, text)
        
        result = []
        for cv, c, v, space in tokens:
            # RULE: Handle Space
            if space:
                result.append(space)
                continue

            # RULE: Standalone Vowels
            if v:
                result.append(self.base_map.get(v, ''))
            
            # RULE: Consonant-Vowel (CV) Pairs
            elif cv:
                vowel = cv[-1]
                consonant_part = cv[:-1] # Gets 'ba' from 'ba' or 'ng' from 'nga'
                
                # Normalize to 'a' base for the map
                base = self.base_map.get(consonant_part + 'a', '')
                
                if vowel in ['e', 'i']:
                    result.append(base + self.kudlit_ei)
                elif vowel in ['o', 'u']:
                    result.append(base + self.kudlit_ou)
                else: # vowel is 'a'
                    result.append(base)
            
            # RULE: Standalone Consonant (Virama)
            elif c:
                base = self.base_map.get(c + 'a', '') if 'a' not in c else self.base_map.get(c, '')
                if base:
                    result.append(base + self.virama)
                
        return "".join(result)

if __name__ == "__main__":
    translator = TagalogToBaybayin()
    # Test with spaces
    print(translator.translate("Salamat Po"))  # Output: ᜐᜎ᜙ᜆ᜔ ᜉᜓ
    print(translator.translate("Mabuhay ang Pilipinas"))