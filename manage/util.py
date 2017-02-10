import os
import subprocess


def get_current_venv():
    """
    Returns the path to the current virtualenv taken from zappa

    The MIT License (MIT)

    Copyright (c) 2017 Rich Jones

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """
    if 'VIRTUAL_ENV' in os.environ:
        venv = os.environ['VIRTUAL_ENV']
    elif os.path.exists('.python-version'):  # pragma: no cover
        try:
            subprocess.check_output('pyenv', stderr=subprocess.STDOUT)
        except OSError:
            print("This directory seems to have pyenv's local venv"
                  "but pyenv executable was not found.")
        with open('.python-version', 'r') as f:
            env_name = f.read()[:-1]
        bin_path = subprocess.check_output(['pyenv', 'which', 'python']).decode('utf-8')
        venv = bin_path[:bin_path.rfind(env_name)] + env_name
    else:  # pragma: no cover
        venv = subprocess.check_output(['which', 'python']).decode('utf-8').split('bin')
        if len(venv) == 2:
            venv = venv[0]
        else:
            print("Zappa requires an active virtual environment.")
            quit()
    return venv