BUCKET_NAME = "guitarlette"
USER_KEY = "jordan"

from pprint import pprint

"""
Bucket


guitarlette/
    <user>/
        <notebook>/
            <songs: title-artist>

"""


from ..s3 import S3


# def test_s3_create_user():
#     client = S3(BUCKET_NAME, USER_KEY)
#     client.create_user()


# def test_s3_list_notebooks():
#     client = S3(BUCKET_NAME, USER_KEY)
#     print(client)
#     notebooks = client.list_notebooks()
#     pprint(notebooks)
#     print("OK")


def test_s3_create_song():
    client = S3(BUCKET_NAME, USER_KEY)
    print(client)
    title = "In the aeroplane Over the sea"
    artist = "neutral milk hotel"
    notebook = "my notebook"
    client.create_song(notebook, title=title, artist=artist)


# def test_s3_create_notebook():
#     client = S3(BUCKET_NAME, USER_KEY)
#     print(client)
#     client.create_notebook("my notebook")
#     print("OK")
