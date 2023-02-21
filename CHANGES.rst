Version 0.0.2
-------------

Released 2023-02-21

- The game mechanics are now wrapped in an OpenAI Gym environment.
- The ``evolve`` command now has a ``--profile`` option, which
  causes it to run via the `Python profiler`_ and write statistics
  to a file in the current directory.


Version 0.0.1
-------------

Released 2023-02-19

- Basic game implementation, with basic NEAT-Python 0.92 integration.
  It doesn't optimize, and there are no visuals, but stuff does run.


.. Links
.. _Python profiler: https://docs.python.org/3/library/profile.html
