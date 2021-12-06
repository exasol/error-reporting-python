
class Placeholder:
    def __init__(self, key: str, text: str):
        self.key = key
        self.text = text
        self._unquoted_suffix = "|uq"

    @property
    def name(self):
        if self.is_unquoted():
            return self._parse_unquoted_placeholder_name()
        return self.text

    def is_unquoted(self):
        return self.text.endswith(self._unquoted_suffix)

    def _parse_unquoted_placeholder_name(self):
        return self.text[:-len(self._unquoted_suffix)]
    
 
