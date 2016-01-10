# SampleManagerWeb

This is SampleManagerWeb (for now... for the lack of a better name), a sample management tool that enables researchers
to keep track of their samples from any PC in a laboratory. The programme is a Flask-based web service that runs on a
central server on the local network of your research institute and that can be accessed from all other computers on the
same network using the normal web browser (should be a recent browser though).

# Installation

This programme should work an almost any platform (Linux, Windows, MacOS), but I only provide the installation instructions
for Linux. Seeing that you should install it on a server, I suppose Linux is the target OS in most cases anyways.

You should have python 2.x and pip installed on your system. From there on it's quite straightforward:

    $ sudo pip install virtualenv

installs virtualenv for python. This is not absolutely necessary, but I recommend it. You can now create a folder somewhere
and clone the git repository:

    $ git clone git@github.com:green-mercury/SampleManagerWeb.git

Now you enter this directory and you create a virtual environment for python - and activate it:

    $ cd SampleManagerWeb
    $ virtualenv venv
    $ . venv/bin/activate

Finally, all that remains to do is to install the required python packages:

    $ pip install -r requirements.txt

TODO: explain how to initialise the DB
