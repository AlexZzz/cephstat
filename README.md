# cephstat
report statistics for ceph daemons

## Howto

#### Show local available daemons:
```
~# ./cephstat -d
osd.64
osd.75
osd.74
osd.73
osd.72
```
It scans local /var/lib/ceph/\* for daemon admin sockets.
You may change path with `-p` option.

#### Report statistics:
```
~# ./cephstat osd.64




op_w  op_r  op_w_in_bytes op_r_out_bytes  op_w_latency  op_r_latency  
33    129   8389188       6407682         0.00112       0.00030       
144   62    4277248       137509          0.00056       0.00025       
3     64    0             81944           0.00038       0.00056       
32    512   428195        1093121         0.00046       0.00042       
^C~#
```

#### List available metrics:
```
~# ./cephstat osd.64 -l
initial_latency
journal_queue_bytes
waitremoterecoveryreserved_latency
queue_len
stat_bytes_avail
op_w_prepare_latency
repwaitbackfillreserved_latency
tier_proxy_read
journal_bytes
subop_w_latency
tier_whiteout
...
```

#### Report specified metrics:
```
~# ./cephstat osd.64 -m op_r_prepare_latency




op_r_prepare_latency  
0.00066               
0.00050               
0.00073               
^C~#
```

### For more info use `-h` or `--help`
