# sparkasse export

A script for downloading transaction history of Sparkasse - Online Banking using selenium.
Currently only tested for german language.

You'll need to supply login username and password. 
An oauth2 request will be sent every time the script runs.

## Setup procedure

- duplicate `config_template.yaml` as `config.yaml`
- replace all values in it
- create your venv (tested with python 3.13):
```bash
cd sparkasse_export
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
- run the script

# list of steps this script executes

| Page               | Action                    | Component found using... |
|--------------------|---------------------------|--------------------------|
| Login Page         | Decline Cookies           | Classname                |
| Login Page         | Enter Login Name          | Classname                | 
| Login Page         | Press Continue-Button     | XPATH                    |
| Login Page         | Enter PIN                 | ID                       |
| Login Page         | Press Login-Button        | XPATH                    |
| Banking Main Page  | (maybe) close overlay-ad  | XPATH                    |
| Banking Main Page  | Click on IBAN             | XPATH                    |
| IBAN Overview Page | Click on Export-Button    | XPATH                    |
| IBAN Overview Page | Click on Specified Format | XPATH                    |
| IBAN Overview Page | Logout                    | XPATH                    |

# what if it doesn't work

> Last checkd and fixed on 30.6.2025

Webscraping is always tricky because you heavily depend on how the websites components are set up.   
If the script doesn't work, probaby one of the implemented ways for finding a component is outdated.

You can either 

- set your application to debug mode in your config file. Find out which component causes the problem and update the selector (XPATH/ID/..) to find it again
- message me and I'll fix it
