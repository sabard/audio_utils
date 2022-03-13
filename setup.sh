#!/bin/sh

eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv install 3.8.12 -s
pyenv virtualenv 3.8.12 audio_utils
./update-deps.sh

pyenv activate audio_utils
pre-commit install
