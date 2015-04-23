# subnet_counter
This program in python is developed to detect all alive machines in a certain subnet using multithread technology.

This work is based on https://github.com/michaelimfeld/netpulse and thanks.

This program is designed to find ipv4 addresses released by dhcpd, with maxjump function you can avoid waiting too long.

It will write the result (Number of alive IPv4 addresses) to a specified file, and you can check 

# examples
Now assume in a subnet there exists 5 machines with addresses: 
192.168.10.1
192.168.10.3
192.168.10.4
192.168.10.230
192.168.10.231

1 :
python subnet_count.py -t 192.168.10.1/24
will find all 5 machines

2 :
python subnet_count.py -t 192.168.10.1/24 -m 20 -f counter.tmp > /dev/null &
will find all 5 machines faster

3 :
python subnet_count.py -t 192.168.10.1/24 -m 20 -j 100 -f counter.tmp > /dev/null &
will find the first 3 machines because maxjump(j) is set to 100

while the program is running, you can periodly check the output file to get the current number of alive machines
