import re

class TagalogToBaybayin:
    def __init__(self):
        # 17 Base Syllables (Corrected 'ma' and 'ya')
        self.base_map = {
            'a': 'ᜀ', 'e': 'ᜁ', 'i': 'ᜁ', 'o': 'ᜂ', 'u': 'ᜂ',
            'ba': 'ᜊ', 'ka': 'ᜃ', 'da': 'ᜇ', 'ra': 'ᜇ', 'ga': 'ᜄ',
            'ha': 'ᜑ', 'la': 'ᜎ', 'ma': 'ᜋ', 'na': 'ᜈ', 'nga': 'ᜅ',
            'pa': 'ᜉ', 'sa': 'ᜐ', 'ta': 'ᜆ', 'wa': 'ᜏ', 'ya': 'ᜌ'
        }
        
        self.kudlit_ei = 'ᜒ' # Dot/Line above
        self.kudlit_ou = 'ᜓ' # Dot/Line below
        self.virama = '᜔'    # Cross killer (Spanish biyas-krus)

    def translate(self, text):
        if not text: return ""
        text = text.lower()
        
        # Updated Pattern: Includes 'y' and 'r', and handles 'nga' priority
        pattern = r'(nga[aeiou]|(?:[bkdrghlmnpstwry])?[aeiou])|(nga|[bkdrghlmnpstwry])|([aeiou])|(\s+)'
        
        # findall returns a list of tuples based on groups
        tokens = re.findall(pattern, text)
        
        result = []
        for cv, c, v, space in tokens:
            if space:
                result.append(space)
                continue

            # Standalone Vowels (A, E/I, O/U)
            if v:
                result.append(self.base_map.get(v, ''))
            
            # Consonant-Vowel (CV) Pairs (e.g., 'ba', 'pi', 'mu')
            elif cv:
                vowel = cv[-1]
                # If CV is just a vowel (regex quirk), handle it
                if cv in ['a', 'e', 'i', 'o', 'u']:
                    result.append(self.base_map.get(cv, ''))
                    continue
                
                consonant_part = cv[:-1]
                base = self.base_map.get(consonant_part + 'a', '')
                
                if vowel in ['e', 'i']:
                    result.append(base + self.kudlit_ei)
                elif vowel in ['o', 'u']:
                    result.append(base + self.kudlit_ou)
                else: # vowel is 'a', no kudlit needed
                    result.append(base)
            
            # Standalone Consonants (e.g., 's' in 'salamat')
            elif c:
                # Always append the 'a' version of the character plus the virama
                search_key = c if c.endswith('a') else c + 'a'
                base = self.base_map.get(search_key, '')
                if base:
                    result.append(base + self.virama)
                
        return "".join(result)

# Quick Test
if __name__ == "__main__":
    ttb = TagalogToBaybayin()
    print(f"Salamat Po -> {ttb.translate('Salamat Po')}")
    print(f"Mabuhay -> {ttb.translate('Mabuhay')}")