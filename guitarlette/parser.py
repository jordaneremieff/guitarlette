from pychord import Chord
from dataclasses import dataclass, field
from typing import List, Union


CONTENT = """
Am D C Fm

Testing testing test ttest etst

G Em C D

sdfsdfsdfsdf
"""


@dataclass
class SongToken:

    content: str

    @property
    def html(self) -> str:
        return self.content


@dataclass
class SongChord(SongToken):

    chord: Chord

    @property
    def html(self) -> str:
        return f"<span class='chord {self.chord}'>{self.content}</span>"

    def transpose(self, n: int) -> None:
        self.chord.transpose(n)


@dataclass
class SongContent:

    raw_data: str
    rows: List[List[Union[SongToken, SongChord]]] = field(
        default_factory=list, init=False
    )

    def __post_init__(self):
        self.rows = [
            [self.parse_token(i) for i in row.split(" ")]
            for row in [i for i in self.raw_data.strip().split("\n") if i]
        ]

    def parse_token(self, token: str) -> Union[SongToken, SongChord]:
        try:
            chord = Chord(token)
        except ValueError:
            return SongToken(content=token)
        return SongChord(content=token, chord=chord)

    def _apply(self, method: str, *args, **kwargs) -> None:
        (getattr(item, method)(*args, **kwargs) for item in (row for row in self.rows))

    def transpose(self, n: int) -> None:
        self._apply("transpose", n)

    @property
    def html(self) -> str:
        content = "".join(
            [
                f"<div class='row'>{''.join([token.html for token in row])}</div>"
                for row in self.rows
            ]
        )
        return content


song = SongContent(raw_data=CONTENT)
song.transpose(3)
print(song)
song.transpose(5)
print(song.html)
