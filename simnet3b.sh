#!/bin/bash

echo "25ms delay | 10mbps | 5% loss"
sudo tc qdisc add dev lo root netem delay 25ms rate 10mbit loss 5%
