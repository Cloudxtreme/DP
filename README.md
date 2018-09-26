# DP
A simple admin panel to manage a DefensePro.

<p align="center">
  <img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/dp.jpg">
</p>

## Configure
Change the Vision IP Address on ```app/views.py```:

```python
################
#### config ####
################

VisionIP = "<IP>"
```

## Usage

```bash
$ . venv/bin/activate
$ python -V
Python 3.5.2
$ python run.py
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

> Logs are saved in: ```app.log```

## Screenshots

### Login with Vision users

<kbd><img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/2018-09-26_105005.png" /></kbd>

### Add multiple IPs to White List / Black List

<kbd><img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/10.png" /></kbd>

### Modify network protection policies

<kbd><img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/2018-09-26_105913.png" /></kbd>
---
