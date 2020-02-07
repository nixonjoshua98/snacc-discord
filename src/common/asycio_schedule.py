import asyncio

# https://phoolish-philomath.com/asynchronous-task-scheduling-in-python.html


async def task_loop(delay: int, func):
	while True:
		await asyncio.sleep(delay)

		if asyncio.iscoroutinefunction(func):
			await func()
		else:
			func()


def add_task(delay: int, func):
	print(f"Added task: {func.__name__}")

	return asyncio.create_task(task_loop(delay, func))


async def cancel_task(task: asyncio.Task):
	task.cancel()

	try:
		await task
	except asyncio.CancelledError:
		pass
