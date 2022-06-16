import uuid


def get_genre_id_filter(genre_id: uuid.UUID):
    genre_id_filter = {
        "nested": {
            "path": "genre",
            "query": {
                "bool": {
                    "must": [
                        {"match": {"genre.id": genre_id}}
                    ]
                }
            }
        }
    }

    return genre_id_filter
