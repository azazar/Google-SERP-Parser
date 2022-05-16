# Google SERP Parser

A small tool to load Google SERP results and parse them into a JSON or CSV format.

## Usage

### Install prerequisites

    $ apt-get update -y
    $ apt-get install --no-install-recommends -y chromium git python3 python3-pip

### Download and Configure Python environment

    $ git clone https://github.com/azazar/Google-SERP-Parser
    $ cd Google-SERP-Parser
    $ virtualenv -p python3 venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    $ python3 google-serp.py -o <filename.json> <search query>

## Build and Use Docker Image

    $ git clone https://github.com/azazar/Google-SERP-Parser
    $ cd Google-SERP-Parser
    $ docker build -t google-serp-parser .
    $ docker run --rm -it google-serp-parser "example.org"
