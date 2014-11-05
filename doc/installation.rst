Installation
============

.. rubric:: Prerequisites

Skynet requires Python3 (>=3.4), install it from here: https://www.python.org/download/releases/3.4.2

**IMPORTANT: Make sure you select the pip package manager option during the installation,
as it is used to install the Skynet package.**

*TIP: On Windows, add both the top-level Python install folder (e.g. C:\Python34)
and the Scripts subfolder (e.g. C:\Python34\Scripts) to your PATH environment variable
if you want to run python scripts and install packages using pip from any folder.*

.. rubric:: Skynet Package Install

Download the latest release from Github at https://github.snei.sony.com/SNEI/skynet/releases.

Get the .zip archive for Windows, and the .tar.gz for Mac/Linux.

To install the package, run in a terminal:

.. code-block:: sh

    pip3 install ~/Downloads/skynet-X.Y.tar.gz

(substitute with skynet-X.Y.zip on Windows)

.. rubric:: Host/Target setup

Detailed host and target setup instructions can be found on the Confluence Skynet space:

* https://qmjira.snei.sony.com/confluence/display/SKYN/Host+setup
* https://qmjira.snei.sony.com/confluence/display/SKYN/Target+setup

Using the Mantis test runner
============================

.. code-block:: sh

    mantis-run --ip=<devkit_ip>[,<additional_devkit_ip>] path/to/tests
    mantis-run --ip=<devkit_ip>[,<additional_devkit_ip>] path/to/test_file.py
    mantis-run --ip=<devkit_ip>[,<additional_devkit_ip>] -k test_method
