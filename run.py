#!venv/bin/python3
# -*- encoding: utf-8 -*-
"""
Autor: alexfrancow
"""

from app import app

if __name__ == "__main__":
	app.run(debug=True, host="192.168.0.25", port="80")
