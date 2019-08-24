import typesystem


class Song(typesystem.Schema):
    title = typesystem.String(max_length=100)
    artist = typesystem.String(max_length=100)
    content = typesystem.Text()

    def __str__(self) -> str:
        return f"{self.title} - {self.artist}"
