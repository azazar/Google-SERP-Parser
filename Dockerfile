FROM debian:11

RUN apt-get update -y \
 && apt-get install --no-install-recommends -y chromium git python3 python3-pip \
 && apt-get clean \
 && cd /opt \
 && git clone https://github.com/azazar/Google-SERP-Parser \
 && cd Google-SERP-Parser \
 && rm -rf .git .gitignore .vscode \
 && pip3 install -r requirements.txt \
 && apt remove -y --autoremove git python3-pip

WORKDIR /opt/Google-SERP-Parser

ENTRYPOINT [ "/usr/bin/python3", "google-serp.py", "-o", "/dev/stdout" ]
