# DP
A simple admin panel to manage a DefensePro.

<p align="center">
  <img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/dp.jpg">
</p>

## Configure
Change the Vision IP Address, user and password on ```app/views.py```:

```python
################
#### config ####
################

VisionIP = "<IP>"
VisionUser = "<USER>"
VisionPasswd = "<PASSWORD>"
```

## Usage

```bash
$ . venv/bin/activate
$ python -V
Python 3.5.2
$ python run.py
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## Screenshots

### Add multiple IPs to Black List

<kbd><img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/8.png" /></kbd>

### Add multiple IPs to White List

<kbd><img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/9.png" /></kbd>

### Modify network protection policies

<kbd><img src="https://raw.githubusercontent.com/alexfrancow/DP/master/PoC/7.png" /></kbd>
---
