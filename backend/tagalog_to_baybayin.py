import re

class TagalogToBaybayin:
    def __init__(self):
        self.base_map = {
            'a': 'ᜀ', 'e': 'ᜁ', 'i': 'ᜁ', 'o': 'ᜂ', 'u': 'ᜂ',
            'ba': 'ᜊ', 'ka': 'ᜃ', 'da': 'ᜇ', 'ra': 'ᜇ', 'ga': 'ᜄ',
            'ha': 'ᜑ', 'la': 'ᜎ', 'ma': 'ᜋ', 'na': 'ᜈ', 'nga': 'ᜅ',
            'pa': 'ᜉ', 'sa': 'ᜐ', 'ta': 'ᜆ', 'wa': 'ᜏ', 'ya': 'ᜌ'
        }
        self.kudlit_ei = 'ᜒ'
        self.kudlit_ou = 'ᜓ'
        self.virama = '᜔'
        # Traditional Baybayin punctuation
        self.danda = '᜵'  # Single bar (comma/pause)
        self.double_danda = '᜶'  # Double bar (period/full stop)

    def translate(self, text):
        if not text: return "", 0
        
        original_text = text.lower().strip()
        confidence = 100.0
        
        non_native = re.findall(r'[cfjqzvx]', original_text)
        if non_native:
            confidence -= (len(non_native) * 15)

        if 'r' in original_text:
            confidence -= 5

        text = original_text.replace('ng', 'NG')
        if text == "mga": 
            return "ᜋᜄ", 100.0
        
        # Updated pattern to include a group for periods and commas: (\.|\,)
        pattern = r'(NG[aeiou]|(?:[bkdrghlmnpstwry])?[aeiou])|(NG|[bkdrghlmnpstwry])|([aeiou])|(\s+)|(\.|\,)'
        tokens = re.findall(pattern, text)
        result = []
        
        # Added 'punct' to the loop unpacking
        for cv, c, v, space, punct in tokens:
            if space:
                result.append(space)
                continue
            
            # Handle Period or Comma
            if punct:
                if punct == '.':
                    result.append(self.double_danda)
                elif punct == ',':
                    result.append(self.danda)
                continue

            vowel_token = v if v else (cv if cv in 'aeiou' else None)
            if vowel_token:
                result.append(self.base_map.get(vowel_token, ''))
                continue

            elif cv:
                vowel_part = cv[-1]
                cons_part = cv[:-1]
                key = 'nga' if cons_part == 'NG' else cons_part + 'a'
                base = self.base_map.get(key, '')
                
                if vowel_part in ['e', 'i']:
                    result.append(base + self.kudlit_ei)
                elif vowel_part in ['o', 'u']:
                    result.append(base + self.kudlit_ou)
                else:
                    result.append(base)
            
            elif c:
                key = 'nga' if c == 'NG' else c + 'a'
                base = self.base_map.get(key, '')
                if base:
                    result.append(base + self.virama)

        return "".join(result), max(0, confidence)