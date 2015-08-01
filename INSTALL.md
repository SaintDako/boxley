# Installation
There are two ways to use Boxley. The first is to get the executable, which is far easier. If you don't trust executables though, and prefer to install (and possibly build) things from source, you can do that. It's a bit more of a process.

## Method 1 (Executable)
(The executable isn't online yet -- sorry!)

### Initialization

To start using Boxley, initialize it, follow the link it spits out, get the authorization code, and paste it back in the terminal. 

```
boxley init
1. Go to: https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id=le4w3kfr8fmlg0d
2. Click "Allow" (you might have to log in first)
3. Copy the authorization code.
Enter the authorization code here: 
```

Now you can start using Boxley! Great job.

## Method 2 (Installing From Source)
Installing from source requires you to make your own Dropbox app and install the Dropbox Python SDK. There are also instructions on building the source into an executable below.

1. Head to the [Dropbox app console](https://www.dropbox.com/developers/apps)
2. Click "create app"
3. Verify your email, if necessary
4. Select "**Dropbox API app**" as the type of app you'd like to create
5. Select "**No**" to the question "Can your app be limited to its own folder?"
6. Select "**All file types**" to the question "What type of files does your app need access to?"
7. Provide an app name -- it doesn't need to be called Boxley

Then, clone this repository and put it somewhere. Open up `main.py` and change the first few lines of the `Init` function, from

```
def Init():
    SECRETS = open("./secrets.txt")
    app_key = SECRETS.readline().strip()
    app_secret = SECRETS.readline().strip()
    SECRETS.close()
```

to

```
def Init():
    # SECRETS = open("./secrets.txt")
    # app_key = SECRETS.readline().strip()
    # app_secret = SECRETS.readline().strip()
    # SECRETS.close()
    app_key = 'YOUR_APP_KEY'
    app_secret = 'YOUR_APP_SECRET'
```

where `YOUR_APP_KEY` and `YOUR_APP_SECRET` must be your app's "app key" and "app secret" respectively, which can be found on the Dropbox app console. 

**NOTE**: if you are using Windows and are planning on making the source into an executable, skip to the instructions below.

Install the [Dropbox Python SDK](https://www.dropbox.com/developers/core/sdks/python). Then running `python main.py init` should work.

## Turning the source into an executable
If you want to turn the repository into an executable, you can try a python library that creates executables. Unfortunately, it's different on different operating systems. 

### Ubuntu
I've had success with Nuitka.

Before starting, you'll need to install the [Dropbox Python SDK](https://www.dropbox.com/developers/core/sdks/python).

#### Nuitka

Using Nuitka is simple enough. On Ubuntu 14.04, I downloaded the .deb file from the [Nuitka downloads page](http://nuitka.net/pages/download.html), and ran the following:

```
sudo dpkg -i nuitka.deb
sudo apt-get update
sudo apt-get install -f

nuitka --recurse-all main.py
```

The last command will create `main.exe`, which can be renamed to `boxley` and put in your path. Then run `boxley init`.

### Windows
I've only had success with PyInstaller thus far. Nuitka and Py2Exe didn't seem to work.

#### PyInstaller
**NOTE**: this is working for Dropbox SDK v2.2.0. If the SDK changes significantly, these instructions may not work.

First, install [PyWin32](http://sourceforge.net/projects/pywin32/files/) -- make sure to install the correct version depending on your version of Python.

Then install PyInstaller with `pip install pyinstaller`. This should probably be run in a command prompt with administrator privileges (right click > run as admin...).

Then get the [Dropbox Python SDK](https://www.dropbox.com/developers/core/sdks/python), but **DO NOT** install it via pip. Actually download the SDK and decompress it. Navigate to the `dropbox/` folder and edit `rest.py`.

In `rest.py`, add `import os` to the import statements. Then change line 27 from

```python
TRUSTED_CERT_FILE = pkg_resources.resource_filename(__name__, 'trusted-certs.crt')     # BAD!
```

to

```python
TRUSTED_CERT_FILE = os.path.join(os.path.dirname(sys.executable), 'trusted-certs.crt')    # GOOD!
```

Backup the `trusted-certs.crt` file to another directory. Then run `python -m compileall`. Then go back to the root of the directory (`dropbox-x.x.x`) and run `python setup.py install`.

Now, in Boxley's directory, run `pyinstaller -F main.py`. This will create `dist/`, `build/` and `main.spec`. Inside `dist/` is the executable. Copy the `trusted-certs.crt` file to `dist/`. Then, run `./dist/main.exe init` and it should work!

**NOTE**: If you decide to move `./dist/main.exe` to another folder, *be sure to move* `trusted-certs.crt` with it!