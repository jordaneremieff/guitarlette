import typing
from dataclasses import dataclass
from collections import deque
from pychord import Chord


class Token:
    __slots__ = ("content", "indexes", "is_new_row", "degree")

    def __init__(self, content: str, degree: typing.Optional[int] = None) -> None:
        self.content = content
        self.indexes = deque()
        self.is_new_row = True
        self.degree = degree

    def append(self, index: int) -> None:
        self.indexes.append(index)

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
        is_tokenized = False
        index = 0
        tokens = {}

        while True:
            if not is_tokenized:
                token_key = parsed[index].strip()

                if token_key not in tokens.keys():
                    token = Token(content=token_key, degree=self.degree)
                    token.append(index)
                    tokens[token_key] = token
                else:
                    tokens[token_key].append(index)

                if index + 1 == total and not is_tokenized:
                    is_tokenized = True
                else:
                    index += 1
            else:
                token_key = parsed[index]
                token = tokens[token_key]
                rendered = token.render()

                result.appendleft(rendered)

                if index == 0:
                    break

                index -= 1

        self.html: str = "".join(result)
