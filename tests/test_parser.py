from guitarlette.parser import SongChord, SongParser
from pychord import Chord


CONTENT = """
    C                   D         G Em C D G
how strange it is to be anything at all
"""


def test_transpose_chord() -> None:
    content = "G"
    chord = Chord(content)
    song_chord = SongChord(content=content, chord=chord)
    song_chord.transpose(1)
    assert str(song_chord.chord) == "Ab"


def test_transpose_song() -> None:
    song = SongParser(content=CONTENT)
    song.transpose(1)
    transposed = """Db                   Eb         Ab Fm Db Eb Ab
how strange it is to be anything at all"""
    assert song.content == transposed
