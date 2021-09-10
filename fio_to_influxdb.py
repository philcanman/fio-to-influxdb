#!/usr/bin/env python3

import sys
import os
import time 
from datetime import datetime
import textwrap
import argparse
import platform

try:
  import influxdb
except ImportError:
  print("Trying to Install required module: influxdb\n")
  os.system('python3 -m pip install influxdb')
  time.sleep(5)

import requests

def fioinput(ip, port, database, hostname):
    client = influxdb.InfluxDBClient(host=ip, port=8086)
        
    try:
        client.ping()
        client.create_database(database)
        client.switch_database(database)
    except:
        print("!!Was unable to connect to the Influxdb!!\
            \nPlease check that the IP address and port information is correct.\
            \nKilling the fio session as well.\
            \n")
        os.system('pkill fio')
        quit()

    # minimal format found here: https://www.andypeace.com/fio_minimal.html
    for line in sys.stdin:
        fullfio_data = line.split(",")
        fullfio_data = fullfio_data[0].split(";")
        
        # Run info
        terseversion = fullfio_data[0]
        fioversion = fullfio_data[1]
        jobname = fullfio_data[2]

        # Read IO info
        readtotalio = (int(fullfio_data[5]) / 1024)
        readbandwidthio = (int(fullfio_data[6]) / 1024)
        readiopsio = fullfio_data[7]
        readpercent = float(fullfio_data[43].strip('%'))

        # Read Submission Latency info
        rdsubmissionmin = int(fullfio_data[9])
        rdsubmissionmax = int(fullfio_data[10])
        rdsubmissionmean = int(float(fullfio_data[11]))
        rdsubmissiondeviation = int(float(fullfio_data[12]))

        # Read Completion Latency info
        rdcompletionmin = int(fullfio_data[13])
        rdcompletionmax = int(fullfio_data[14])
        rdcompletionmean = int(float(fullfio_data[15]))
        rdcompletiondeviation = int(float(fullfio_data[16]))

        # Read Total Latency info
        rdtotalmin = int(fullfio_data[37])
        rdtotalmax = int(fullfio_data[38])
        rdtotalmean = int(float(fullfio_data[39]))
        rdtotaldeviation = int(float(fullfio_data[40]))

        # Write IO info
        writetotalio = (int(fullfio_data[46]) / 1024)
        writebandwidthio = (int(fullfio_data[47]) / 1024)
        writeiopsio = fullfio_data[48]
        writepercent = float(fullfio_data[84].strip('%'))

        # Write Submission Latency info
        wrsubmissionmin = int(fullfio_data[50])
        wrsubmissionmax = int(fullfio_data[51])
        wrsubmissionmean = int(float(fullfio_data[52]))
        wrsubmissiondeviation = int(float(fullfio_data[53]))

        # Write Completion Latency info
        wrcompletionmin = int(fullfio_data[54])
        wrcompletionmax = int(fullfio_data[55])
        wrcompletionmean = int(float(fullfio_data[56]))
        wrcompletiondeviation = int(float(fullfio_data[57]))

        # Write Total Latency info
        wrtotalmin = int(fullfio_data[78])
        wrtotalmax = int(fullfio_data[79])
        wrtotalmean = int(float(fullfio_data[80]))
        wrtotaldeviation = int(float(fullfio_data[81]))

        # IO depth distribution
        iodepth01 = float(fullfio_data[92].strip('%'))
        iodepth02 = float(fullfio_data[93].strip('%'))
        iodepth04 = float(fullfio_data[94].strip('%'))
        iodepth08 = float(fullfio_data[95].strip('%'))
        iodepth16 = float(fullfio_data[96].strip('%'))
        iodepth32 = float(fullfio_data[97].strip('%'))
        iodepth64 = float(fullfio_data[98].strip('%'))

        # Block size 
        # Bandwidth / IOPS
        if readiopsio == "0":
            readblocksize = float(0)
        else:
            readblocksize = round((int(readbandwidthio) / int(readiopsio)) * 1024, 1)

        if writeiopsio == "0":
            writeblocksize = float(0)
        else:
            writeblocksize = round((int(writebandwidthio) / int(writeiopsio)) * 1024, 1)

        # Calculate percentage of read vs write IOPS
        totaliops = int(readiopsio) + int(writeiopsio)
        readiopspercentage = int(readiopsio) / int(totaliops)
        writeiopspercentage =  int(writeiopsio) / int(totaliops)

        # CPU Usage
        cpuuser = float(fullfio_data[87].strip('%'))
        cpusystem = float(fullfio_data[88].strip('%'))

        # print("Read IOPS % : "+str(readiopspercentage))
        # print("Write IOPS % : "+str(writeiopspercentage))

        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        print(current_time+" | Job Name: "+jobname+" | Read IOPS: "+readiopsio+" | Write IOPS: "+writeiopsio+" | Block(read/write): "+str(readblocksize)+" / "+str(writeblocksize), end='\r')


        sys.stdout.flush()

        json_body = [
            {
                "measurement": "FIO",
                "tags": {
                    "runId": jobname,
                    "hostname": hostname
                },
                "time": current_time,
                "fields": {
                    "Read_IOPS": int(readiopsio),
                    "Read_Percentage": readpercent,
                    "Read_Total_I/O_(MB)": readtotalio,
                    "Read_bandwidth_(MB/s)": readbandwidthio,
                    "Read_Latency_Submission_min": rdsubmissionmin,
                    "Read_Latency_Submission_max": rdsubmissionmax,
                    "Read_Latency_Submission_mean": rdsubmissionmean,
                    "Read_Latency_Submission_deviation": rdsubmissiondeviation,
                    "Read_Latency_Completion_min": rdcompletionmin,
                    "Read_Latency_Completion_max": rdcompletionmax,
                    "Read_Latency_Completion_mean": rdcompletionmean,
                    "Read_Latency_Completion_deviation": rdcompletiondeviation,
                    "Read_Latency_Total_min": rdtotalmin,
                    "Read_Latency_Total_max": rdtotalmax,
                    "Read_Latency_Total_mean": rdtotalmean,
                    "Read_Latency_Total_deviation": rdtotaldeviation,
                    "Write_IOPS": int(writeiopsio),
                    "Write_Percentage": writepercent,
                    "Write_Latency_Submission_min": wrsubmissionmin,
                    "Write_Latency_Submission_max": wrsubmissionmax,
                    "Write_Latency_Submission_mean": wrsubmissionmean,
                    "Write_Latency_Submission_deviation": wrsubmissiondeviation,
                    "Write_Latency_Completion_min": wrcompletionmin,
                    "Write_Latency_Completion_max": wrcompletionmax,
                    "Write_Latency_Completion_mean": wrcompletionmean,
                    "Write_Latency_Completion_deviation": wrcompletiondeviation,
                    "Write_Latency_Total_min": wrtotalmin,
                    "Write_Latency_Total_max": wrtotalmax,
                    "Write_Latency_Total_mean": wrtotalmean,
                    "Write_Latency_Total_deviation": wrtotaldeviation,
                    "Write_Total_I/O_(MB)": writetotalio,
                    "Write_bandwidth_(MB/s)": writebandwidthio,
                    "Read Block Size (KB)": readblocksize,
                    "Write Block Size (KB)": writeblocksize,
                    "CPU User": cpuuser,
                    "CPU System": cpusystem,
                    "IOdepthdist01": iodepth01,
                    "IOdepthdist02": iodepth02,
                    "IOdepthdist04": iodepth04,
                    "IOdepthdist08": iodepth08,
                    "IOdepthdist16": iodepth16,
                    "IOdepthdist32": iodepth32,
                    "IOdepthdist64": iodepth64,
                    "Read_IOPS_Percentage": readiopspercentage,
                    "Write_IOPS_Percentage": writeiopspercentage
                }
            }
        ]


        client.write_points(json_body)
        

def main():
    parser = argparse.ArgumentParser(
      prog='fio_to_influxdb',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog=textwrap.dedent('''\
         The following options must be added to the fio command for this script to function
             --status-interval=1
             --minimal
         Example usage:
         fio instructionfile.fio --status-interval=1 --minimal | fio_to_influxdb.py
        --
         '''))
    parser.add_argument("-ip", default='localhost',help="IP or DNS name of host running influxdb.  Default is localhost", type=str)
    parser.add_argument("-port", default='8086',help="Port used to connect to influxdb.  Default is 8086", type=int)
    parser.add_argument("-database", default='fio',help="Name of database created in influxdb.  Default is fio", type=str)
    parser.parse_args()
    args = parser.parse_args()

    print(\
        "\nConnecting to influx database with the following parameters\n\
            \tIP/DNS:   "+args.ip+"\n\
            \tPort:     "+str(args.port)+"\n\
            \tDatabase: "+args.database+"\n\
            "
            )

    # Get OS host name
    hostname = platform.uname()[1]

    fioinput(args.ip, args.port, args.database, hostname)

    print("\n\nJob complete\n")

main()
