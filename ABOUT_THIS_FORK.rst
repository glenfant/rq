Windows support
===============

RQ may work under windows. But the timeout support is bypassed

Multiprocessing in place of Unix fork
=====================================

Jobs are always executed in a distinct process. In original rq, jobs are
executed using Unix fork() that's not available under Windows. From this
version, when executed under Windows, rq workers use automatically
multiprocessing when executing jobs in a distinct process. When under Unix,
workers execute as before the jobs in a forked process. But the "--
multiprocessing" option of "rqworker" command enables workers to execute jobs
with multiprocessing.

In process queue
================

Added the WIP queue that records actually executed jobs.

rq enhancement. Support for deferred job executions
===================================================

rq has already a support for dependent jobs. At a given time, you have two
jobs J1 and J2 :

- they need to be executed in a particular order (J1, then J2)
- the parameters and execution contexts for running these jobs are known
  before execution.

So far, so good, we can use the "depends_on" parameter for this. In example ::

  >>> bread_slices = queue.enqueue(cut_bread, kwargs={parts: 4})
  >>> queue.enqueue(add_marmalade, args=(strawberry,), depends_on=bread_slices)

But we have sometimes situations where we need to enqueue a task with known
parameters which depends on future tasks that cannot be known (enumeration,
name, parameters, ...) before this. In other words, and expressed as API ::

  >>> furure_job = queue.enqueue(some_callable, ..., deferred=True)

This enqueues a new job with the DEFERRED status (and **not** the QUEUED
status as usual). The workers will ignore such jobs at the moment.

We shall now add new jobs which **must** be executed before this
``future_job`` ::

  >>> queue.enqueue(some_callable_1, ..., blocked_by=future_job)
  >>> queue.enqueue(some_callable_2, ..., blocked_by=future_job)

This enqueues new jobs which execution is conditioned by the execution of
``future_job``. The corresponding jobs are created with the DEFERRED status
too.

Technically speaking, each job enqueued with the ``blocked_by`` argument is
appended to a Redis list ::

  key : "rq:deferred:<id of future_job>"
  value : [id of job some_callable_1, id of job some_callable_2]

As these jobs are marked as DEFERRED, the workers bypass such jobs.

When all dependent jobs are pushed, we are ready to execute all this ::

  >>> future_job.release()

or... ::

  >>> rq.release_job(future_job)

The effect of this is ::

- Change the state of all dependent jobs to QUEUED.

  -> The workers may execute these jobs when possible, taking potential
     depedencies into account.

- Change the state of ``future_job`` to ``QUEUED`` when last of these jobs is
  executed. Executing "de facto" the job few time later.
