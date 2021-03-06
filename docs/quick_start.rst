.. Copyright 2017 Covata Limited or its affiliates

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Quick Start
===========

Requirements
------------

-  Python 2.7 + or 3.3 +
-  pip 9.0.1 +

Setting up Virtualenv
---------------------

.. code:: bash

   sudo pip install virtualenv
   virtualenv venv
   source venv/bin/activate

The project can then be installed directly using pip
or built from source.

Installation
------------

-  Using ``pip`` directly from Github (Note: This will install the current master branch):

   .. code:: bash

      pip install git+git://github.com/Covata/delta-sdk-python.git@master

Building from Source
--------------------

Building the project
~~~~~~~~~~~~~~~~~~~~

-  Install PyBuilder:

   .. code:: bash

      pip install pybuilder

-  Check out the project:

   .. code:: bash

      git clone https://github.com/Covata/delta-sdk-python.git
      cd delta-sdk-python

-  Build the project:

   .. code:: bash

      pyb

Installing the binary distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Using PyBuilder:

   .. code:: bash

      pyb install

-  Using Distutils, where `x.y.z` is the version number:

   .. code:: bash

      cd target/dist/delta-sdk-python-x.y.z
      python setup.py install
