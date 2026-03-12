#!/bin/bash

sudo tc qdisc add dev lo root netem delay 5ms rate 10mbit loss 5%
