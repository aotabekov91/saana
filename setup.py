#!/usr/bin/env python
import os
from setuptools import setup, find_packages

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    setup(
        name="speechToCommand",
        version="1.0.0",
        author="Adhambek Otabekov",
        description="",
        keywords=[],
        package_data={
            '':['*.yaml', '*.ini', '*.db', '*.wav', '*css', '*json', '*sav', '*.*', '*'],
            },
    )
