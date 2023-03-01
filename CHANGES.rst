Version 0.0.4
-------------

Released 2023-03-01

- A modified version of the `Deep Q-Learning for Atari Breakout`_
  code example from Keras was introduced as ``learn.py``.  It's not
  yet able to learn well, I've been using the game score as a reward
  function and that's totally unsuitable in so many ways.
- The Apache-2.0 licence was added, matching the GitHub repository
  containing the above file.
- The project's dependencies have been updated to reflect the shift
  from NEAT-Python to TensorFlow.


Version 0.0.3
-------------

Released 2023-02-26

- Genome fitness is evaluated using a per-generation random seed,
  such that every member of a generation is evaluated using the same
  sequence of shapes.
- ``evolve --profile`` sets and propagates the random seed to
  reduce spurious difference between profile runs.
- Five missing shapes have been added.
- The ``info`` returned by ``Env.step`` and ``Env.reset`` now includes
  the game's current score.
- A new ``TinyScreen`` wrapper allows the game to be viewed as though
  on a tiny (19 x 19 pixel) 1-bit screen.
- The score calculation now more closely matches the original game.
- The game mechanics now run 80% faster than in the previous release
  (the unrendered framerate increased from 3,650 fps to 6,535 fps on
  my Chromebook).


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
.. _Deep Q-Learning for Atari Breakout: https://keras.io/examples/rl/deep_q_network_breakout/
