# fio-to-influxdb

A simple Python 3 script to help graph FIO output in real-time. This script parses FIO minimal terse output and feeds it to InfluxDB. Includes an example grafana dashboard that can be tweaked as needed.

![Alt text](blob/FIO_Example_Dashboard.jpg?raw=true "Example Grafana FIO Dashboard")

```sh
./fio_to_influxdb.py -h
usage: fio_to_influxdb [-h] [-ip IP] [-port PORT] [-database DATABASE]

optional arguments:
  -h, --help          show this help message and exit
  -ip IP              IP or DNS name of host running influxdb. Default is
                      localhost
  -port PORT          Port used to connect to influxdb. Default is 8086
  -database DATABASE  Name of database created in influxdb. Default is fio

 The following options must be added to the fio command for this script to function
     --status-interval=1
     --minimal
 Example usage:
 fio instructionfile.fio --status-interval=1 --minimal | fio_to_influxdb.py
```

