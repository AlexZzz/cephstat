#!/usr/bin/python

from __future__ import print_function
import ceph_daemon
import json
from StringIO import StringIO
from os import listdir
from time import sleep

schema=""
previous_counters={}
actual_vals={}

default_vals=['op_r','op_r_out_bytes','op_w','op_w_in_bytes']

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
#         	print key, value
		key_schema = json.dumps(schema[key])
#		print key_schema
		key_type = json.dumps(json.loads(key_schema)["type"])
		if key_type == "10":
#			print key
			if key in previous_counters.keys():
#				print value - previous_counters[key]
				actual_vals[key] = value - previous_counters[key]
			previous_counters[key] = value
			continue

                avg = get_avg(value)
       	        summ = get_sum(value)
               	if avg is not None and summ is not None:
			continue
	
def parse_schema(option,dump,osd_num):
	global schema
	schema = json.loads(json.dumps(dump[option]))
#	for key,value in res.items():
#		print key,value
		

def read_asok(NUM):
	#Get all data from every osd
	#print (NUM)
	for asok in get_osd_asok(NUM):
		asok_perf_schema = json.loads(ceph_daemon.admin_socket(asok,['perf','schema'],'format'))
		osd_num = asok.rsplit('/',1)[1].split('.')[1]
		parse_schema('osd',asok_perf_schema,osd_num)
		line = 0
		while(1):
        		asok_perf_dump = json.loads(ceph_daemon.admin_socket(asok,['perf','dump'],'format'))
			parse_option('osd',asok_perf_dump,osd_num)
			if (line == 1 or line % 10 == 0):
				for k,v in actual_vals.items():
					if k in default_vals:
						print (k,end='\t')
				print ('\n')
			for k,v in actual_vals.items():
				if k in default_vals:
					print (v,end='\t')
			print ('\n')
			line+=1
			sleep(1)


#		parse_option('recoverystate_perf',asok_perf_dump,osd_num)
#		parse_option('filestore',asok_perf_dump,osd_num)

	return 0

def main():
  read_asok("16")

if __name__ == "__main__":
  main()
