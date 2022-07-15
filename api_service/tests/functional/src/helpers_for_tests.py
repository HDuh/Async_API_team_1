import uuid
from http import HTTPStatus

__all__ = (
    'BAD_ID_CASES',
    'get_page_from_structure',
    'sorted_lists_for_tests_all',
)

BAD_ID_CASES = [
    (uuid.uuid4(), HTTPStatus.NOT_FOUND),
    ("incorrect_test_id", HTTPStatus.UNPROCESSABLE_ENTITY)
]


def get_page_from_structure(page, size, structure):
    expected_sorted_list = sorted(structure, key=lambda d: -d['imdb_rating'])
    start = 0 if page == 1 else (page - 1) * size
    end = start + size
    page_structure = expected_sorted_list[start:end]

    return page_structure


def sorted_lists_for_tests_all(expected_data, response_data):
    expected_sorted_list = sorted(expected_data, key=lambda d: d['id'])
    response_sorted_list = sorted(response_data, key=lambda d: d['id'])

    return expected_sorted_list, response_sorted_list
