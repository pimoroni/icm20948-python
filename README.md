# ICM20948 9-DOF Accelerometer, Magnetometer and Gyroscope

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/icm20948-python/test.yml?branch=main)](https://github.com/pimoroni/icm20948-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/icm20948-python/badge.svg?branch=main)](https://coveralls.io/github/pimoroni/icm20948-python?branch=main)
[![PyPi Package](https://img.shields.io/pypi/v/icm20948.svg)](https://pypi.python.org/pypi/icm20948)
[![Python Versions](https://img.shields.io/pypi/pyversions/icm20948.svg)](https://pypi.python.org/pypi/icm20948)

Detect movement in nine different ranges of motion: 3-axis acceleration, 3-axis gyroscopic motion, and 3-axis compass heading.

## Where to buy

* [ICM20948 9DoF Motion Sensor Breakout](https://shop.pimoroni.com/products/icm20948)

# Installing

## Full install (recommended):

We've created an easy installation script that will install all pre-requisites and get you up and running with minimal efforts. To run it, fire up Terminal which you'll find in Menu -> Accessories -> Terminal on your Raspberry Pi desktop, as illustrated below:

![Finding the terminal](http://get.pimoroni.com/resources/github-repo-terminal.png)

In the new terminal window type the commands exactly as it appears below (check for typos) and follow the on-screen instructions:

```
git clone https://github.com/pimoroni/icm20948-python
cd icm20948-python
./install.sh
```

**Note** Libraries will be installed in the "pimoroni" virtual environment, you will need to activate it to run examples:

```
source ~/.virtualenvs/pimoroni/bin/activate
```

## Development:

If you want to contribute, or like living on the edge of your seat by having the latest code, you can install the development version like so:

```
git clone https://github.com/pimoroni/icm20948-python
cd icm20948-python
./install.sh --unstable
```

## Install stable library from PyPi and configure manually

* Set up a virtual environment: `python3 -m venv --system-site-packages $HOME/.virtualenvs/pimoroni`
* Switch to the virtual environment: `source ~/.virtualenvs/pimoroni/bin/activate`
* Install the library: `pip install icm20948`

In some cases you may need to us `sudo` or install pip with: `sudo apt install python3-pip`.

This will not make any configuration changes, so you may also need to enable:

* i2c: `sudo raspi-config nonint do_i2c 0`

You can optionally run `sudo raspi-config` or the graphical Raspberry Pi Configuration UI to enable interfaces.
