#!/bin/bash

echo "5ms delay | 10mbps | 5% loss"
sudo tc qdisc add dev lo root netem delay 5ms rate 10mbit loss 5%
