#!/bin/bash 
# fastping2 is an adaption of code posted at http://tinyurl.com/jwxdask
# on December 4, 2011 by user "kshji".
# It has been modified by John Fraizer for use with the MRLG as a
# replacement for fastping.c
#
# The original fastping.c that shipped with previous versions of MRLG
# has been found to be vulnerable to remote memory corruption.
# See CVE-2014-3931  http://www.s3.eurecom.fr/cve/CVE-2014-3931.txt

# Print usage if we don't get the right number of command line args
[ $# -lt 3 ] && echo "usage:$0 count size target " >&2 && exit 1

grep="/bin/grep"
tail="/usr/bin/tail"
dig="/usr/bin/dig"
ping="/bin/ping"
date="/bin/date"

count=$1
size=$2
target=$3

start=$(${date} '+%Y-%m-%d %T' )

pass=0
fail=0

ipaddr=$(${dig} +short ${target} | ${tail} -n1)
echo "Sending $count ${size}-byte ICMP Packets to $target ($ipaddr)"
i=1
while ((i<=count))
do
        data=$(${ping} -n -c 1 -s $size $target | ${grep} "1 packets transmitted" )
        case "$data" in
                *100%*packet*loss*)
                        ((fail+=1))
                        echo -n .
                        ;;
                *)      ((pass+=1))
                        echo -n !
                        ;;
        esac
        ((i+=1))
done
echo
end=$(${date} '+%Y-%m-%d %T' )
((success=pass*100 / count ))
((loss=fail*100 / count ))
echo "   $success% success...   $loss% packet loss..."
echo "$start - $end "
