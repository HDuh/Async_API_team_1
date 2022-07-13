def uuid_to_str(instance):
    """Конвертация uuid -> str"""
    try:
        instance.id = str(instance.id)
        instance.film_ids = [str(film_id) for film_id in instance.film_ids]
    except AttributeError:
        ...
    finally:
        return instance
