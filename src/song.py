import typing
from dataclasses import dataclass
from collections import deque
from pychord import Chord


class Token:
    __slots__ = ("content", "is_new_row", "degree")

    def __init__(self, content: str, degree: typing.Optional[int] = None) -> None:
        self.content = content
        self.is_new_row = True
        self.degree = degree

    def render(self) -> str:
        s = self.content.strip().decode()
        if s == "":
            return f"<span class='delimiter'></span>"
        if s == "{$s}":
            return " "
        if s == "{$n}" and self.is_new_row:
            self.is_new_row = False
            return "<div class='row'>"
        if s == "{$n}" and not self.is_new_row:
            self.is_new_row = True
            return "</div>"

        try:
            chord = Chord(s)
        except ValueError:
            return f"<span class='lyric'>{s}</span>"

        if self.degree:
            chord.transpose(self.degree)
            s = str(chord)

        return f"<span class='chord'>{s}</span>"


@dataclass
class Song:
    text: str
    degree: typing.Optional[int] = None

    def __post_init__(self) -> None:
        parsed = (
            self.text.encode("utf-8")
            .strip()
            .replace(b"\n", b" {$n} ")
            .replace(b" ", b" {$s} ")
        ).split(b" ")
        total = len(parsed)
        result = deque()
        tokens = {}

        for index in range(total):
            token_key = parsed[index].strip()
            if token_key not in tokens.keys():
                token = Token(content=token_key, degree=self.degree)
                tokens[token_key] = token
            else:
                token = tokens.get(token_key)
            rendered = token.render()
            result.append(rendered)

        self.html: str = "".join(result)
