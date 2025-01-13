 #!/bin/bash

 #while [ 1 ]; do sleep 1; clear; tail api_counter.json; done
 
 watch tail -n 1 api_counter.json