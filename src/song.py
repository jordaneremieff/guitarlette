import typing
from dataclasses import dataclass, InitVar

from pychord import Chord


@dataclass
class Song:
    source: InitVar[str]
    degree: InitVar[typing.Optional[int]] = None

    def __post_init__(self, source: str, degree: typing.Optional[int] = None) -> None:
        html_rows = []
        text_rows = []
        chords = []
        rows = source.strip().split("\n")
        row_count = len(rows)
        row_index = 0
        while row_index < row_count - 1:
            row = rows[row_index]
            row_parts = row.split(" ")
            html_values = []
            text_values = []
            for value in row_parts:
                try:
                    chord = Chord(value.strip())
                except ValueError:
                    chord = None

                if chord:
                    html_class = "chord"
                    if degree is not None:
                        chord.transpose(degree)
                        value = str(chord)
                    if value not in chords:
                        chords.append(value)
                elif value == "":
                    html_class = "delimiter"
                else:
                    html_class = "lyric"

                html_value = f"<span class='{html_class}'>{value}</span>"
                html_values.append(html_value)
                text_values.append(value)

                html_row = f"<div class='row'>{' '.join(html_values)}</div>"
                text_row = " ".join(text_values)

            html_rows.append(html_row)
            text_rows.append(text_row)
            row_index += 1

        self.html: str = "".join(html_rows)
        self.text: str = "\n".join(text_rows)
