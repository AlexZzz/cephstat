#!/usr/bin/python

from __future__ import print_function
import ceph_daemon
import json
from StringIO import StringIO
from os import listdir
from time import sleep
import argparse

# perf dump schema
schema=""
# saved counters to calc diff
previous_counters={}
# values to print
actual_vals={}
# update/show interval
interval='1.0'

# values to print
default_vals=['op_r','op_r_out_bytes','op_w','op_w_in_bytes','op_r_latency','op_w_latency']

def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("osd_num",help='Osd number')
    argparser.add_argument("-i","--interval", default='1', action='store',type=float,
        help="Amount of time between reports (default = 1 second)")
    argparser.add_argument("-m","--metric",nargs="+",required=False,
        help="Metrics to parse. -l for more info")
    argparser.add_argument("-l","--list-metrics",action='store_true',required=False,
        help="List available metrics")
    return argparser.parse_args()


def get_osd_asok(NUM):
        import glob
        asoks=[]
        for i in glob.glob('/var/run/ceph/ceph-osd.'+NUM+'.asok'):
                asoks.append(i)
        return asoks

def get_avg(param):
        if 'avgcount' in json.dumps(param):
                return param.get('avgcount')

def get_sum(param):
        if 'sum' in json.dumps(param):
                return param.get('sum')

def parse_option(option,dump,osd_num):
	global schema,actual_vals
	res = json.loads(json.dumps(dump[option]))
        for key,value in res.items():
		key_schema = json.dumps(schema[key])
		key_type = json.dumps(json.loads(key_schema)["type"])
                # type = 10 - bytes-based metric
		if key_type == "10":
			if key in previous_counters.keys():
				actual_vals[key] = value - previous_counters[key]
			previous_counters[key] = value
			continue
                # type = 5 - latency metric
		if key_type == "5":
			avg = get_avg(value)
			summ = get_sum(value)
			latency_vals = {'avg' : avg, 'summ' : summ}
			if key in previous_counters.keys():
				previous_avg = previous_counters[key]['avg']
				previous_summ = previous_counters[key]['summ']
				last_summ = summ - previous_summ
				if last_summ != 0:
					actual_vals[key] = '%.5f'%(last_summ / (avg - previous_avg))
				else:
					actual_vals[key] = 0
			previous_counters[key] = latency_vals
				
	
def parse_schema(option,dump):
	global schema
	schema = json.loads(json.dumps(dump[option]))

def list_metrics(osd_num):
    global schema
    for asok in get_osd_asok(osd_num):
        asok_perf_schema = json.loads(ceph_daemon.admin_socket(asok,['perf','schema'],'format'))
        parse_schema('osd',asok_perf_schema)
        for k,v in schema.items():
            print (k)
		

def read_asok(osd_num):
	global interval
	for asok in get_osd_asok(osd_num):
		asok_perf_schema = json.loads(ceph_daemon.admin_socket(asok,['perf','schema'],'format'))
#		osd_num = asok.rsplit('/',1)[1].split('.')[1]
		parse_schema('osd',asok_perf_schema)
		line = 0
		while(1):
        		asok_perf_dump = json.loads(ceph_daemon.admin_socket(asok,['perf','dump'],'format'))
			parse_option('osd',asok_perf_dump,osd_num)
			head_string = ""
			metrics_string = ""
			for k,v in actual_vals.items():
				if k in default_vals:
					if (line == 1 or line % 10 == 0):
						head_string += k + '\t'
					metrics_string += str(v) + '\t'
			if head_string != "":
				print ("\n"+head_string)
			print (metrics_string)
			line+=1
			sleep(interval)

def main():
  args = parse_args()
  global interval,default_vals

  if args.metric :
    default_vals=args.metric

  if args.list_metrics :
    list_metrics(args.osd_num)
    return

  interval = args.interval
  read_asok(args.osd_num)

if __name__ == "__main__":
  main()
