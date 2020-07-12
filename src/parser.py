from typing import Optional, List
from dataclasses import dataclass, field


from pychord import Chord


@dataclass
class SongToken:
    content: str
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
    tokenized_chords: List = field(default_factory=list, init=False)
    html_rows: Optional[List] = None

    def __post_init__(self):
        # TODO: Implement this more efficiently.
        content_split = self.content.strip().split("\n")
        html_rows = []
        for content_row in content_split:
            _token_row = []
            _token_row_html = []
            for content in content_row.split(" "):
                token = SongToken(content)
                _token_row.append(token)
                _token_row_html.append(token.html)
                if token.chord and token not in self.tokenized_chords:
                    self.tokenized_chords.append(token)
            html_rows.append(f"<div class='row'>{' '.join(_token_row_html)}</div>")
            self.tokenized_content.append(_token_row)
        self.html_rows = html_rows

    def transform(self, method: str, *args, **kwargs) -> None:
        new_content_rows = []
        new_html_rows = []
        for row in self.tokenized_content:
            new_row = []
            new_row_html = []
            for token in row:
                if token.chord is not None:
                    getattr(token, method)(*args, **kwargs)
                new_row.append(token.content)
                new_row_html.append(token.html)
            new_content_rows.append(" ".join(new_row))
            new_html_rows.append(f"<div class='row'>{' '.join(new_row_html)}</div>")
        self.content = "\n".join(new_content_rows)
        self.html_rows = new_html_rows

    def transpose(self, n: int) -> None:
        self.transform("transpose", n)

    @property
    def html(self) -> str:
        content = "".join(self.html_rows)

        return content
