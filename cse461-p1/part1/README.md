Akshaya Akkugari aakshaya
Medha Mittal mmittal2
Keosha Chhajed keoshac

The secrets from one run of our program (and the test server) were:
A: 71
B: 36
C: 255
D: 396

To run our code (our client, our server together), open two ports on attu:
Then in one port, cd into the cse461-p1/part2/ directory
And run:
./run_server.sh hostname port
where hostname is the host, and you can replace 2222 with any valid port

In the other port, cd into the cse461-p1/part1/ directory
And run:
./run_client.sh hostname port
the host and portname here should be the same as in the server command.

For example if I was in attu8:
./run_server.sh attu8@cs.washington.edu 4444
./run_client.sh attu8@cs.washington.edu 4444

Or if I wasn't on attu and was local: 
./run_server.sh localhost 4444
./run_client.sh localhost 4444

would be my two commands, each in the separate terminal. 
The client will end once all stages have been complete, and you can end the server by entering ctrl+C