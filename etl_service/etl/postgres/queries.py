def movies_query(index_state: str) -> str:
    query = f"""
    SELECT
        fw.id,
        fw.title,
        fw.description,
        fw.rating as imdb_rating,
        ARRAY_AGG(DISTINCT jsonb_build_object('id', genre.id, 'name', genre.name)) as genre,
        ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'full_name', person.full_name)) FILTER 
                                                                    (WHERE pfw.role = 'actor') AS actors,
        ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'full_name', person.full_name)) FILTER 
                                                                    (WHERE pfw.role = 'writer') AS writers,
        ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'full_name', person.full_name)) FILTER 
                                                                    (WHERE pfw.role = 'director') AS directors,
        GREATEST(fw.modified, MAX(person.modified), MAX(genre.modified)) AS updated_at
    FROM content.film_work fw
        LEFT JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
        LEFT JOIN content.genre genre ON gfw.genre_id = genre.id
        LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
        LEFT JOIN content.person person ON pfw.person_id = person.id
    WHERE
        GREATEST(fw.modified, person.modified, genre.modified) > '{index_state}'
    GROUP BY fw.id
    ORDER BY GREATEST(fw.modified, MAX(person.modified), MAX(genre.modified)) ASC
    """
    return query


def genres_query(index_state: str) -> str:
    """
    SQL запрос с подставленной временной меткой для индекса genres
    """

    return f"""
    SELECT genre.id,
           genre.name,
           genre.modified as updated_at
    FROM content.genre genre
    WHERE
        genre.modified > '{index_state}'
    GROUP BY genre.id
    ORDER BY genre.modified ASC
    """


def persons_query(index_state: str) -> str:
    """
    SQL запрос с подставленной временной меткой для индекса persons
    """

    return f"""
    SELECT person.id,
        person.full_name,
        ARRAY_AGG(DISTINCT person_film.role::text) AS role,
        ARRAY_AGG(DISTINCT person_film.film_work_id::text) AS film_ids,
        person.modified as updated_at
    FROM content.person person
        LEFT JOIN content.person_film_work AS person_film ON person.id = person_film.person_id
    WHERE
        person.modified > '{index_state}'
    GROUP BY person.id
    ORDER BY person.modified ASC
    """


def get_query_by_index(index: str, index_state: str) -> str:
    """Формирует нужный sql запрос в зависимости от индекса"""

    indexes = {
        "movies": movies_query(index_state),
        "genres": genres_query(index_state),
        "persons": persons_query(index_state),
    }

    return indexes[index]


def index_mapper(index: str, index_state: str) -> str:
    """Функция возвращает SQL запрос выгрузки данных для индекса."""
    mapping = {
        'movies': movies_query(index_state),
        'genres': genres_query(index_state),
        'persons': persons_query(index_state),
    }
    try:
        return mapping[index]
    except KeyError:
        raise ValueError(f'Not query for index {index}')
