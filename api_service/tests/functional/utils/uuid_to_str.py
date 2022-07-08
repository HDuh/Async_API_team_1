def uuid_to_str(instance):
    """Конвертация uuid -> str"""
    try:
        instance.id = str(instance.id)
    except AttributeError:
        ...
    finally:
        return instance
