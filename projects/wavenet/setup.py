from distutils.core import setup
import py2exe

Mydata_files = [('', ['src/wavenetserver.cfg'])]

setup(
    name="WaveNet Server",
    version="0.1",
    description="Wavenet: Wavemeter data made accessible",
    author="Gergely Imreh",
    console=['src/wavenetserver.py'],
    data_files=Mydata_files,
    options={
                "py2exe":{
                        "unbuffered": True,
                        "optimize": 2,
                }
        }
    )
