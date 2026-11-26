# Start a test run and come back for the result

Your checkout and its test environment are on a Mac. From a connected chat,
start the suite on that Mac and keep the task number. Use it in a second
request to see what happened.

> On my Mac, start the project's usual test command in the checkout I select.
> Return the CMDOP task number so I can check it later.

> On the same Mac, read the output of that task. Tell me whether it finished
> and what the test runner reported.

A developer used this workflow on November 26, 2026 to run the SDK example
catalog tests. The first task finished with a Python import error. After a
compatibility fix, a new task ran the same command with the same interpreter.
Reading the new task returned `running: false` and the following test summary:

```text
Ran 12 tests in 0.087s

OK
```

A finished task can contain either outcome. Read the test runner's summary
before reporting success. While the task is running, poll its existing number.
Keep the machine program running so its retained terminal output remains available.

The caller needs permission to start the task. For your own project, supply its
actual checkout path, interpreter and test command.
[Commands, tasks and output](../docs/commands-and-tasks.md)
