import asyncio

class AsyncWrapper:
    def __init__(self, gen):
        self.gen = gen

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.gen)
        except StopIteration:
            raise StopAsyncIteration