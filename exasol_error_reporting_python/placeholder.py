
class Placeholder:
    """
    A data class holds information about Placeholder.
    """

    def __init__(self, key: str, text: str):
        self.key = key
        self.text = text
        self._unquoted_suffix = "|uq"

    @property
    def name(self) -> str:
        """
        Return the placeholder name. If there is an unquotation suffix ("|uq")
        in the placeholder, the suffix is removed.

        :return: placeholder name
        """
        if self.is_unquoted():
            return self._parse_unquoted_placeholder_name()
        return self.text

    def is_unquoted(self) -> bool:
        """
        Checks whether the text ends with the unquotation suffix ("|uq").

        :return: True If the text ends with the unquotation suffix.
        """
        return self.text.endswith(self._unquoted_suffix)

    def _parse_unquoted_placeholder_name(self) -> str:
        """
        Remove the unquotation suffix ("|uq") from the text.

        :return: the text in which the unquotation suffix is removed
        """
        return self.text[:-len(self._unquoted_suffix)]
    
 
