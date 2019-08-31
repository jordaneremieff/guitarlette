import typesystem


class SongSchema(typesystem.Schema):
    title = typesystem.String(max_length=255)
    content = typesystem.Text()

    def __str__(self) -> str:
        return self.title
