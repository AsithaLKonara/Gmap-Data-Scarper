"""Advanced obfuscation parsing for phone numbers."""
import re
from typing import List, Optional


class ObfuscationParser:
    """Parses obfuscated phone numbers (word-to-number, [dot], etc.)."""
    
    # Word to number mapping
    WORD_TO_NUMBER = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "oh": "0", "o": "0",
        "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
        "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
        "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
        "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
        "eighty": "80", "ninety": "90"
    }
    
    def __init__(self):
        """Initialize obfuscation parser."""
        pass
    
    def parse(self, text: str) -> List[str]:
        """
        Parse obfuscated phone numbers from text.
        
        Args:
            text: Text containing obfuscated phone numbers
            
        Returns:
            List of parsed phone number strings
        """
        results = []
        
        # 1. Handle [dot], [at], [dash] replacements
        text = self._replace_brackets(text)
        
        # 2. Handle word-to-number conversion
        text_with_numbers = self._convert_words_to_numbers(text)
        
        # 3. Extract phone numbers from converted text
        phone_pattern = re.compile(
            r'(\+?\d{1,3}[\s\-\.\(\)]?)?(\(?\d{1,4}\)?[\s\-\.\)]{0,2})?(\d{1,4}[\s\-\.\)]{0,2}){2,4}',
            re.IGNORECASE
        )
        
        matches = phone_pattern.findall(text_with_numbers)
        for match in matches:
            if isinstance(match, tuple):
                phone = ''.join(str(m) for m in match if m).strip()
            else:
                phone = str(match).strip()
            
            if len(phone) >= 10:
                results.append(phone)
        
        # 4. Handle mixed formats (e.g., "five five five - one two three four")
        mixed_pattern = re.compile(
            r'(?:' + '|'.join(self.WORD_TO_NUMBER.keys()) + r')(?:\s*[-\.\s]?\s*(?:' + '|'.join(self.WORD_TO_NUMBER.keys()) + r')){6,12}',
            re.IGNORECASE
        )
        
        mixed_matches = mixed_pattern.findall(text)
        for match in mixed_matches:
            converted = self._convert_words_to_numbers(match)
            phone_pattern_match = phone_pattern.search(converted)
            if phone_pattern_match:
                phone = phone_pattern_match.group(0)
                if len(phone) >= 10:
                    results.append(phone)
        
        # Deduplicate
        return list(set(results))
    
    def _replace_brackets(self, text: str) -> str:
        """Replace [dot], [at], [dash] with actual characters."""
        replacements = {
            r'\[dot\]': '.',
            r'\[at\]': '@',
            r'\[dash\]': '-',
            r'\[dash\]': '-',
            r'\(dot\)': '.',
            r'\(at\)': '@',
            r'\(dash\)': '-',
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _convert_words_to_numbers(self, text: str) -> str:
        """Convert word representations to numbers."""
        words = text.lower().split()
        result = []
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word in self.WORD_TO_NUMBER:
                result.append(self.WORD_TO_NUMBER[clean_word])
            else:
                # Check if it's a partial match (e.g., "five-five")
                parts = re.split(r'[-\.\s]', clean_word)
                converted_parts = []
                for part in parts:
                    if part in self.WORD_TO_NUMBER:
                        converted_parts.append(self.WORD_TO_NUMBER[part])
                    else:
                        converted_parts.append(part)
                
                if converted_parts != [clean_word]:
                    result.append(''.join(converted_parts))
                else:
                    result.append(word)
        
        return ' '.join(result)
    
    def parse_phone_from_text(self, text: str) -> Optional[str]:
        """
        Parse a single phone number from obfuscated text.
        
        Args:
            text: Text containing obfuscated phone
            
        Returns:
            Parsed phone number or None
        """
        results = self.parse(text)
        return results[0] if results else None

