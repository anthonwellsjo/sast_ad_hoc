#!/bin/bash

# Install, init and start defect dojo

# Clone the project
git clone https://github.com/DefectDojo/django-DefectDojo
cd django-DefectDojo

# Building Docker images
./dc-build.sh

# Install code scan tools
brew install semgrep
pip3 install njsscan
