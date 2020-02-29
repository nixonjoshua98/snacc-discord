import asyncio


async def task_loop(delay: int, func, args):
	while True:
		await asyncio.sleep(delay)

		if asyncio.iscoroutinefunction(func):
			try:
				await func(*args)
			except TypeError:
				await func()
		else:
			try:
				func(*args)
			except TypeError:
				func()


def add_task(delay: int, func, *args):
	print(f"Added task: {func.__name__}")

	return asyncio.create_task(task_loop(delay, func, args))


async def cancel_task(task: asyncio.Task):
	task.cancel()

	try:
		await task
	except asyncio.CancelledError:
		pass
