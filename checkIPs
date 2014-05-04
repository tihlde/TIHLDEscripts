#!/bin/bash
#
# torvaldl 5/11/11
#
for ip in `seq 2 62`; do 
    fullip=$(ping -W 1 -c 1 158.38.48.$ip | grep 'statistic' -A 1 | egrep -o '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}')
    ans=$(ping -W 1 -c 1 158.38.48.$ip | grep 'statistic' -A 1 | egrep -io "0 rec|1 rec")
    host=$(cat /etc/bind/tihlde.org | grep $fullip | head -n 1 | awk '{print $1}')
    rev=$(cat /etc/bind/tihlde.rev | grep "$ip " | head -n 1 | awk '{print $4}')
    if [ "$ans" = "0 rec" ]; then
        comment=$(cat /etc/bind/tihlde.org | grep $fullip -A 1 | head -n 2 | tail -n 1 | cut -d'"' -f2)
        echo "$ip (BIND: $host, rev: $rev) is DOWN. ($comment)"
    else
        echo "$ip (BIND: $host) is up."
    fi
    host=""
    rev=""
        
done
echo "Husk at Windass ikke nødvendigvis svarer på ping."


#--- 158.38.48.4 ping statistics ---
#1 packets transmitted, 0 received, +1 errors, 100% packet loss, time 0ms
#--- 158.38.48.5 ping statistics ---
#1 packets transmitted, 1 received, 0% packet loss, time 0ms

