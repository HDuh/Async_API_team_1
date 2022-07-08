async def clean_index(instances):
    if isinstance(instances, list):
        for instance in instances:
            await instance.delete()
    else:
        await instances.delete()
