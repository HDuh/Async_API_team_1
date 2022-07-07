import asyncio


def unpack_factory(factory, size):
    """"""
    loop = asyncio.new_event_loop()
    size_int = size.fuzz()
    return [
        model_factory.__dict__
        for model_factory in loop.run_until_complete(factory.get_factory().async_create_batch(size_int))
    ]
