# amana-privnet-launcher

amana-privnet-launcher was created to quickly launch nodes running on the "Amana" PoA network. The nodes would be created and expected to run locally with the intention of creating a test environment for development and research purposes. **It probably isn't a good idea to use this script to generate nodes for a production environment** 

## Installation
Most modules used are available from the Python Standard Library 

Install `eth-account`

`pip install eth-account`


## Creating Private Network
To generate a private network you would need to run the `launch_privnet.py` script:

`python3 launch_privnet.py`

You should see a new directory created in the home directory: `qng_privnet`. Inside this directory, there should be 3 subdirectories each containing the neccesary files to run each of the nodes: `node1`, `node2`, `node3`. The private keys used for each of the nodes and their corresponding addresses will be available in the `private_keys.json` file.

```
qng_privnet/
├── node1
├── node2
├── node3
└── private_keys.json
```