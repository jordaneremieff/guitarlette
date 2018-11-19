from pychord import Chord
from dataclasses import dataclass
from typing import List


CONTENT = """
Am D C Fm

Testing testing test ttest etst

G Em C D

sdfsdfsdfsdf
"""


@dataclass
class SongRowItem:

    content: str
    chord: Chord = None

    def format_html(self) -> None:
        if self.is_chord:
            self.content = "".join(
                [
                    f"<span style='font-weight:bold;' class='{self.chord}'>",
                    f"{self.content}</span>",
                ]
            )

    def transpose(self, n: int) -> None:
        if self.is_chord:
            self.chord.transpose(n)

    @property
    def is_chord(self) -> bool:
        return self.chord is not None


@dataclass
class SongContent:

    rows: List[List]

    def _apply_method(self, method: str, *args, **kwargs) -> None:
        for row in self.rows:
            for item in row:
                getattr(item, method)(*args, **kwargs)

    def format_html(self) -> None:
        self._apply_method("format_html")

    def transpose(self, n: int) -> None:
        self._apply_method("transpose", n)

    @property
    def html(self) -> str:
        self.format_html()
        content = []

        for row in self.rows:
            row_content = "".join([item.content for item in row])
            content.append(row_content)

        content = "<br>".join(content)
        return content

    # @property
    # def get_fingerings(self):
    #     return self._get_fingerings


def parse_chord(item_content: str) -> SongRowItem:
    try:
        chord = Chord(item_content)
    except ValueError:
        chord = None
    return SongRowItem(content=item_content, chord=chord)


def parse_row(row: str) -> list:
    row = [parse_chord(i) for i in row.split(" ")]
    return row


def song_parser(raw_data: str) -> SongContent:
    raw_data = [i for i in raw_data.strip().split("\n") if i]
    rows = [parse_row(row) for row in raw_data]
    song_content = SongContent(rows=rows)
    return song_content


# song = song_parser(CONTENT)

# song.transpose(3)
# print(song)
# song.transpose(5)
# print(song)
# song.format_html()
# print(song.html)
