
class ErrorMessageBuilder:
    def __init__(self, error_code: str):
        self._error_code = error_code
        self._message_builder = []
        self._mitigations = []

    def message(self, message: str):
        self._message_builder.append(message)
        return self

    def mitigation(self, mitigation: str):
        self._mitigations.append(mitigation)
        return self

    def ticket_mitigation(self):
        self.mitigation("This is an internal error that should not happen. "
                        "Please report it by opening a GitHub issue.")
        return self

    def __str__(self):
        result = []

        if self._message_builder:
            result.append("".join((self._error_code, ":")))
            result += self._message_builder
        else:
            result.append(self._error_code)

        if len(self._mitigations) == 1:
            result.append(self._mitigations[0])
        elif len(self._mitigations) > 1:
            mitigations = ["Known mitigations:"]
            for mitigation in self._mitigations:
                mitigations.append("".join(("* ", mitigation)))
            result.append("\n".join(mitigations))

        return " ".join(result)


