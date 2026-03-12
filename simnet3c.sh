#!/bin/bash

echo "100ms delay | 10mbps | 5% loss"
sudo tc qdisc add dev lo root netem delay 100ms rate 10mbit loss 5%
