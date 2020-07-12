from typing import Optional, List
from dataclasses import dataclass, field


from pychord import Chord


@dataclass
class SongToken:
    content: str
    line_break: bool = False
    html_class: Optional[str] = None
    chord: Optional[Chord] = None

    def __post_init__(self) -> None:
        if self.content == "":
            self.html_class = "delimiter"
        else:
            try:
                self.chord = Chord(self.content.strip())
            except ValueError:
                pass
            else:
                self.html_class = "chord"

    def transpose(self, degree: int) -> None:
        if self.chord is None:
            raise ValueError("Transpose may only be called on chord tokens")
        assert self.chord is not None
        self.chord.transpose(degree)
        self.content = str(self.chord)

    @property
    def html(self) -> str:
        if self.html_class:
            return f"<span class='{self.html_class}'>{self.content}</span>"
        return self.content


@dataclass
class SongParser:

    content: str
    tokenized_content: List[List[SongToken]] = field(default_factory=list, init=False)
    tokenized_chords: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        content_split = self.content.strip().split("\n")
        for content_row in content_split:
            _token_row = []
            for content in content_row.split(" "):
                token = SongToken(content)
                _token_row.append(token)
                if token.chord and token not in self.tokenized_chords:
                    self.tokenized_chords.append(token)
            self.tokenized_content.append(_token_row)

    def transform(self, method: str, *args, **kwargs) -> None:
        new_content_rows = []
        for row in self.tokenized_content:
            new_row = []
            for token in row:
                if token.chord is not None:
                    getattr(token, method)(*args, **kwargs)
                new_row.append(token.content)
            new_content_rows.append(" ".join(new_row))
        self.content = "\n".join(new_content_rows)

    def transpose(self, n: int) -> None:
        self.transform("transpose", n)

    @property
    def html(self) -> str:
        content = "".join(
            [
                f"<div class='row'>{' '.join([token.html for token in row])}</div>"
                for row in self.tokenized_content
            ]
        )
        return content
