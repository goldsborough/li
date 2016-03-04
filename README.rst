**
li
**

.. image:: https://badge.fury.io/py/li.svg
    :target: http://badge.fury.io/py/li

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg
	:target: http://goldsborough.mit-license.org

.. image:: http://img.shields.io/gratipay/goldsborough.svg
	:target: https://gratipay.com/~goldsborough/

.. image:: https://travis-ci.org/goldsborough/li.svg?branch=master
    :target: https://travis-ci.org/goldsborough/li

\

\

*li* is a tool to quickly fetch a license.

When finishing up a project, you had two choices to fetch your license:

1. Go to some previous projects of yours and get the license you used there. Then check if the year of the license is still valid, else change it. Estimated time: ~30 seconds.

2. Go online and use a search engine to find the license of your choice, in plain-text. Naturally, you click on the wrong link about 13 times before you find a simple plain-text version of the license, for you to copy. Then replace the <year> and <author> fields with your data. Estimated time: ~1-2 minutes.

I propose the following solution:

.. code-block:: bash

    $ li -k mit -a "Your Name" > LICENSE

Estimated time: ~5 seconds.

You can also pass a year with ``-y``, but I reckon you'll be happy with the
default value being the current year. The best thing is: your input is cached under
``$HOME/.license``, so next time, all you need to type is:

.. code-block:: bash

    $ li > LICENSE

Estimated time: ~1 second. Estimated happiness: over 9000. You're welcome.

Installing
==========

You can grab *li* off PyPI:

.. code-block:: bash

    $ pip install li

`License <goldsborough.mit-license.org>`_
=========================================

This project is licensed under the MIT-License.

Authors
=======

Peter Goldsborough & `cat <https://goo.gl/IpUmJn>`_ :heart:
