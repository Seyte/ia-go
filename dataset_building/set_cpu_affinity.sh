#!/bin/bash
echo "password" | sudo -S /opt/homebrew/bin/python3.10 /Users/charles/Desktop/Cours/S8/IA/GO/dataset_building/make_dataset.py 1.json 2 14 &

pid=$! # get the process ID of the last backgrounded command

ret=0
while [ $ret -ne 0 ]; do
  echo "Trying to set CPU affinity for process $pid"
  proc_setthread_cpumask $pid 0x01 # set affinity to the first CPU core
  ret=$?
done

echo "CPU affinity set for process $pid"
