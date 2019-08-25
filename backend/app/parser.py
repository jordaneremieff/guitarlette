from dataclasses import dataclass, field
from typing import List


from pychord import Chord


@dataclass
class Token:
    """
    A token contained within a composition.

    This may represent the following:

        * a chord value, such as 'C'
        * an empty space to be used as a delimiter
        * any string value, such as the lyrics in a song
    """

    content: str
    chord: Chord = None

    @property
    def html(self) -> str:
        if self.chord is not None:
            return f"<span class='chord'>{self.content}</span>"
        elif not self.content:
            return "<span class='chord-delimiter'></span>"
        return self.content

    def transpose(self, n: int) -> None:
        assert self.chord is not None
        self.chord.transpose(n)
        self.content = str(self.chord)


@dataclass
class Parser:

    content: str
    rows: List[List[Token]] = field(default_factory=list, init=False)
    chords: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.rows = [
            [self.parse_token(i) for i in row.split(" ")]
            for row in [i for i in self.content.strip().split("\n") if i]
        ]

    def parse_token(self, token: str) -> Token:
        try:
            chord = Chord(token)
        except ValueError:
            return Token(content=token)
        else:
            if token not in self.chords:
                self.chords.append(token)
        return Token(content=token, chord=chord)

    def transform(self, method: str, *args, **kwargs) -> None:
        """
        Apply a transformation method to the song content.
        """
        new_content_rows = []

        for row in self.rows:

            new_row = []

            for token in row:

                # Iterate the `Token`s, checking if there is a chord value. If found,
                # the transform method on the `Token` instance will be called with the
                # supplied arguments.
                if token.chord is not None:
                    getattr(token, method)(*args, **kwargs)

                # Append the token content to the row to build a new composition.
                new_row.append(token.content)

            # Join the new token row together to form a complete content row, then
            # append to the new content rows to finally be joined to form the new
            # content.
            new_content_rows.append(" ".join(new_row))

        self.content = "\n".join(new_content_rows)

    def transpose(self, n: int) -> None:
        self.transform("transpose", n)

    @property
    def html(self) -> str:
        content = "".join(
            [
                f"<div class='row'>{' '.join([token.html for token in row])}</div>"
                for row in self.rows
            ]
        )
        return content
