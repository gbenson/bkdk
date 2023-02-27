BKDK
====

BKDK is a machine learning experiment to see if I can create an AI
that can play a puzzle game I'm semi-addicted to.  Inspired by
`MarI/O`_, “a program made of neural networks and genetic algorithms
that kicks butt at Super Mario World”.

.. Links
.. _MarI/O: https://www.youtube.com/watch?v=qv6UVOQ0F44

How to run it?
--------------

Clone the repo::

 git clone https://github.com/gbenson/bkdk.git
 cd bkdk

Create a virtual environment::

 python3 -m venv venv
 . venv/bin/activate

Upgrade pip and setuptools::

 pip install --upgrade pip setuptools

Install in editable mode::

 pip install -e .

Train a network::

 python learn.py
