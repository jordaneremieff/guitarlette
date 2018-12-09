import json
from dataclasses import dataclass, field
from typing import List, Union, Tuple


from pychord import Chord


@dataclass
class SongToken:

    content: str

    @property
    def html(self) -> str:
        if not self.content:
            return "<span class='chord-delimiter'></span>"
        return self.content


@dataclass
class SongChord(SongToken):

    chord: Chord

    @property
    def html(self) -> str:
        return f"<span class='chord {self.chord}'>{self.content}</span>"

    def transpose(self, n: int) -> None:
        self.chord.transpose(n)
        self.content = str(self.chord)


@dataclass
class SongParser:

    content: str
    rows: List[List[Union[SongToken, SongChord]]] = field(
        default_factory=list, init=False
    )
    chords: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.rows = [
            [self.parse_token(i) for i in row.split(" ")]
            for row in [i for i in self.content.strip().split("\n") if i]
        ]

    def parse_token(self, token: str) -> Union[SongToken, SongChord]:
        try:
            chord = Chord(token)
        except ValueError:
            return SongToken(content=token)
        else:
            if token not in self.chords:
                self.chords.append(token)
        return SongChord(content=token, chord=chord)

    def _apply(self, method: str, *args, **kwargs) -> None:
        new_content = []

        for row in self.rows:
            new_row = []
            for token in row:
                if hasattr(token, "chord"):
                    getattr(token, method)(*args, **kwargs)

                new_row.append(token.content)

            new_content.append(" ".join(new_row))

        self.content = "\n".join(new_content)

    def transpose(self, n: int) -> None:
        self._apply("transpose", n)

    @property
    def html(self) -> str:
        content = "".join(
            [
                f"<div class='row'>{' '.join([token.html for token in row])}</div>"
                for row in self.rows
            ]
        )
        return content

    @property
    def json(self):
        return json.dumps(
            {
                "type": "song.parser",
                "editor_content": self.content,
                "viewer_content": self.html,
                "chords": self.chords,
            }
        )


if __name__ == "__main__":
    test = """
    G                Em
    What a beautiful face
                         C
    I have found in this place,
                     D
    that is circling all around the sun
    G                Em
    What a beautiful dream
                            C
    that could flash on the screen
                     D                    G
    in a blink of an eye and be gone from me,
              Em
    soft and sweet,
             C               D                 G Em C D
    let me hold it close and keep it here with me
    """
    song = SongParser(content=test)
    song.transpose(3)
    print(song.html)
    song.transpose(5)
    print(song.html)
