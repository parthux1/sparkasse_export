# sparkasse export

A script for downloading transaction history of Sparkasse - Online Banking using selenium.
Currently only tested for german language.

You'll need to supply login username and password. 
An oauth2 request will be sent every time the script runs.

## Setup procedure

- duplicate `config_template.yaml` as `config.yaml`
- replace all values in it
- create your venv:
```bash
cd sparkasse_export
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
- run the script