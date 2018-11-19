from pychord import Chord
from dataclasses import dataclass
from typing import List
from functools import partial

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

    def format_html(self):
        if self.is_chord:
            self.content = f"<span style='font-weight:bold;'>{self.content}</span>"

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

    # @property
    # def get_fingerings(self):
    #     return self._get_fingerings


def parse_chord(element):
    try:
        chord = Chord(element)
    except ValueError:
        chord = None
    return SongRowItem(content=element, chord=chord)


def parse_row(row):
    row = [parse_chord(i) for i in row.split(" ")]
    return row


def song_parser(raw_data):
    raw_data = [i for i in raw_data.strip().split("\n") if i]
    rows = [parse_row(row) for row in raw_data]
    content = SongContent(rows=rows)
    return content


song = song_parser(CONTENT)

song.transpose(3)
print(song)
song.transpose(5)
print(song)
song.format_html()
print(song)
