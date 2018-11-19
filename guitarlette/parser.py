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

    def transpose(self, n):
        if self.chord is not None:
            self.chord.transpose(n)


@dataclass
class SongContent:

    rows: List[List]

    @property
    def get_fingerings(self):
        return self._get_fingerings

    def transpose(self, n):
        for row in self.rows:
            for item in row:
                item.transpose(n)


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
    print(content)
    content.transpose(3)
    print(content)


song_parser(CONTENT)
