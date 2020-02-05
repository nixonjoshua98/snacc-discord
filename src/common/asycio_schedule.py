import asyncio


async def task_loop(delay: int, func, condition):
	while condition():
		await asyncio.sleep(delay)

		if asyncio.iscoroutinefunction(func):
			await func()
		else:
			func()


def add_task(delay: int, func, condition):
	return asyncio.create_task(task_loop(delay, func, condition))


async def cancel_task(task: asyncio.Task):
	task.cancel()

	try:
		await task
	except asyncio.CancelledError:
		pass
