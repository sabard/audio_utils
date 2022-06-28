from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='audio_utils',
    version='0.0.2',
    license='MIT,',
    description='Template for creating generic Python packages',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Sabar Dasgupta',
    author_email='s@bardasgupta.com',
    install_requires=[],
    packages=['audio_utils'],
    python_requires='>=3.7'
)
