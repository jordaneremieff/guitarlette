import typing
from dataclasses import dataclass, field, InitVar

from pychord import Chord


@dataclass
class Song:
    source: InitVar[str]
    degree: typing.Optional[int] = None
    html: typing.Optional[str] = None
    txt: typing.Optional[str] = None
    txt_rows: typing.List[typing.List] = field(default_factory=list, init=False)
    html_rows: typing.List[typing.List] = field(default_factory=list, init=False)
    chords: typing.List = field(default_factory=list, init=False)
    row_count: typing.Optional[int] = None

    def __post_init__(self, source: str) -> None:
        self._parse(source, init=True)
        self.html = "".join(self.html_rows)
        self.txt = "\n".join(self.txt_rows)
        self.row_count = len(self.html_rows)

    def _parse(self, source, init: bool = False):
        if init:
            rows = source.strip().split("\n")
            for row in rows:
                self._parse(row)
        else:
            row = source.split(" ")
            html_values = []
            txt_values = []
            for value in row:
                try:
                    chord = Chord(value.strip())
                except ValueError:
                    chord = None

                if chord:
                    html_class = "chord"
                    if self.degree is not None:
                        chord.transpose(self.degree)
                        value = str(chord)
                    if value not in self.chords:
                        self.chords.append(value)
                elif value == "":
                    html_class = "delimiter"
                else:
                    html_class = "lyric"

                html_value = f"<span class='{html_class}'>{value}</span>"
                html_values.append(html_value)
                txt_values.append(value)

            html_row = f"<div class='row'>{' '.join(html_values)}</div>"
            txt_row = " ".join(txt_values)

            self.html_rows.append(html_row)
            self.txt_rows.append(txt_row)
