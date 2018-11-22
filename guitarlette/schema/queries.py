CREATE_SONG_MUTATION = """
mutation createSong($name: String!, $content: String!) {
  createSong(name: $name, content: $content) {
    song {
      id
      name
      content
    }
  }
}
"""


UPDATE_SONG_MUTATION = """
mutation updateSong($id: Int!, $name: String!, $content: String!) {
  updateSong(id: $id, name: $name, content: $content) {
    song {
      id
      name
      content
    }
  }
}
"""
