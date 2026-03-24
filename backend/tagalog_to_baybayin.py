import re

class TagalogToBaybayin:
    def __init__(self):
        # 17 Base Syllables + Unique Vowel Glyphs
        self.base_map = {
            'a': 'ᜀ', 'e': 'ᜁ', 'i': 'ᜁ', 'o': 'ᜂ', 'u': 'ᜂ',
            'ba': 'ᜊ', 'ka': 'ᜃ', 'da': 'ᜇ', 'ra': 'ᜇ', 'ga': 'ᜄ',
            'ha': 'ᜑ', 'la': 'ᜎ', 'ma': 'ᜋ', 'na': 'ᜈ', 'nga': 'ᜅ',
            'pa': 'ᜉ', 'sa': 'ᜐ', 'ta': 'ᜆ', 'wa': 'ᜏ', 'ya': 'ᜌ'
        }
        self.kudlit_ei = 'ᜒ' # Dot/Line above
        self.kudlit_ou = 'ᜓ' # Dot/Line below
        self.virama = '᜔'    # Cross killer (+)

    def translate(self, text):
        if not text: return ""
        text = text.lower().strip()
        
        # 1. Linguistic Exceptions
        if text == "mga": return "ᜋᜄ"
        
        # 2. Pre-process Digraphs: Ensure 'ng' is one unit
        text = text.replace('ng', 'NG') 

        # 3. Pattern Strategy:
        # Group 1: Consonant (inc. NG) + Vowel
        # Group 2: Standalone Consonant (Virama)
        # Group 3: Standalone Vowel
        # Group 4: Spaces
        pattern = r'(NG[aeiou]|(?:[bkdrghlmnpstwry])?[aeiou])|(NG|[bkdrghlmnpstwry])|([aeiou])|(\s+)'
        
        tokens = re.findall(pattern, text)
        result = []
        
        for cv, c, v, space in tokens:
            if space:
                result.append(space)
                continue
            
            # --- RULE A: Standalone Vowels (A, E/I, O/U) ---
            # We check 'v' group and check if 'cv' is actually just a vowel
            vowel_token = v if v else (cv if cv in 'aeiou' else None)
            if vowel_token:
                result.append(self.base_map.get(vowel_token, ''))
                continue

            # --- RULE B: Consonant-Vowel (CV) Pairs ---
            elif cv:
                vowel_part = cv[-1]
                cons_part = cv[:-1]
                
                # Map to 'nga' for our placeholder, otherwise append 'a'
                key = 'nga' if cons_part == 'NG' else cons_part + 'a'
                base = self.base_map.get(key, '')
                
                if vowel_part in ['e', 'i']:
                    result.append(base + self.kudlit_ei)
                elif vowel_part in ['o', 'u']:
                    result.append(base + self.kudlit_ou)
                else: # inherent 'a'
                    result.append(base)
            
            # --- RULE C: Standalone Consonants (Final Consonants) ---
            elif c:
                key = 'nga' if c == 'NG' else c + 'a'
                base = self.base_map.get(key, '')
                if base:
                    result.append(base + self.virama)
                    
        return "".join(result)

# Quick Test
if __name__ == "__main__":  # pragma: no cover
    ttb = TagalogToBaybayin()
    print(f"Opo -> {ttb.translate('Opo')}")       # Expected: ᜂᜉᜓ
    print(f"Ngiti -> {ttb.translate('Ngiti')}")   # Expected: ᜅᜒᜆᜒ
    print(f"Salamat -> {ttb.translate('Salamat')}") # Expected: ᜐᜎᜋᜆ᜔