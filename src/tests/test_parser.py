from pychord import Chord
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Token:
    content: str
    html_class: Optional[str] = None
    chord: Optional[Chord] = None

    def __post_init__(self) -> None:
        try:
            self.chord = Chord(self.content)
        except ValueError:
            if not self.content:
                self.html_class = "delimiter"
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
    tokenized_content: List[List[Token]] = field(default_factory=list, init=False)
    tokenized_chords: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        for content_row in self.content.strip().split("\n"):
            if content_row:
                _token_row = []
                for content in content_row.split(" "):
                    token = Token(content)
                    _token_row.append(token)
                    if token.chord and token not in self.tokenized_chords:
                        self.tokenized_chords.append(token)
                self.tokenized_content.append(_token_row)

    def transform(self, method: str, *args, **kwargs) -> None:
        """
        Apply a transformation method to the song content.
        """
        new_content_rows = []

        for row in self.tokenized_content:
            new_row = []
            for token in row:
                # Iterate the `Token`s, checking if there is a chord value. If found,
                # the transform method on the `Token` instance will be called with the
                # supplied arguments.
                if token.chord is not None:
                    getattr(token, method)(*args, **kwargs)

                # Append the token content to the row to build a new composition.
                new_row.append(token.content)

            # Join the new token row together to form a complete content row, then
            # append to the new content rows to finally be joined to form the new
            # content.
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


# def parse_tokens(row):
#     row = rows.pop().split(' ')
#     for i in row:
#         if i:
#             try:
#                 chord = Chord(token)
#             except ValueError:
#                 Token(content=token)
#             else:
#                 Token(chord=chord)


# def mk_esc(esc_chars):
#     rows = CONTENT.strip().split("\n")
#     return lambda s: ''.join(['\\' + c if c in esc_chars else c for c in s])


# def test_parser():
#     rows = CONTENT.strip().split("\n")
#     tokens = []
#     while rows:
#         row = rows.pop().split(' ')

#         if row:


#     for row in rows:
#         for i in row.split(" "):
#             if i:
#                 try:
#                     chord = Chord(token)
#                 except ValueError:
#                     Token(content=token)
#                 else:
#                     Token(chord=chord)


#                   if token not in self.chords:
#             self.chords.append(token)

#         return Token(content=token, chord=chord)
#                 print(i)

# self.content.strip().split("\n")

# print(content)

if __name__ == "__main__":

    CONTENT = """
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

    song = SongParser(content=CONTENT)
    song.transpose(3)
    print(song.html)
    song.transpose(5)
    print(song.html)
