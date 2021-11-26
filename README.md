# chilean-jobs-scraping

Set of scripts made with Python, Selenium, etc. for scraping jobs data from chilean web pages.

## Requirements

* google chrome
* python
* virtualenv
* chromedriver compatible with installed chrome version

## Installation

*The recommendation is to create a tmux terminal to leave the script running*

* First a folder for the project and then create virtualenv in previous folder (install virtualenv if it is not installed)

```bash
virtualenv env
```
* Activate virtualenv
```bash
source env/bin/activate
```
* Then install all the requirements
```bash
pip install -r requirements.txt
```
## Usage
Run the script you need, example:

```python
python3 bne/bne.py
```