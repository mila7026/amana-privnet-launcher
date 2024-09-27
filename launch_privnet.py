import os
from eth_account import Account
import secrets
import json
import sys
import subprocess
from ellipticcurve.privateKey import PrivateKey


# We will assume "qng" directory to be located in users home directory 
QNG_DIRECTORY = os.path.expanduser("~") + "/qng_privnet"
NODE_1_DIRECTORY =  QNG_DIRECTORY + "/node1"
NODE_2_DIRECTORY =  QNG_DIRECTORY + "/node2"
NODE_3_DIRECTORY =  QNG_DIRECTORY + "/node3"
QNG_BINARY = os.path.expanduser("~") + "/qng/build/bin/qng"

PRIV_KEY_1 = "0x" + secrets.token_hex(32)  # generate 256 bit (32 bytes) private key
PRIV_KEY_2 = "0x" + secrets.token_hex(32)  
PRIV_KEY_3 = "0x" + secrets.token_hex(32)  

# Customise as necessary - Change these if they will be remote nodes
IP_ADDRESS_1 = "127.0.0.1"
IP_ADDRESS_2 = "127.0.0.1"
IP_ADDRESS_3 = "127.0.0.1"

PORT_1 = 30303
PORT_2 = 30303
PORT_3 = 30303

# Generate enode private key (ECDSA 128 bit) for each node
ENODE_PREFIX = "enode://"
# ENODE_1 = ENODE_PREFIX + PrivateKey().publicKey().toString() + "@" + IP_ADDRESS_1 + ":30303"
ENODE_PRIV_1 = PrivateKey()
ENODE_PRIV_2 = PrivateKey()
ENODE_PRIV_3 = PrivateKey()


def create_directories():
    # Lets create some directories to host our files
    try:
        os.mkdir(QNG_DIRECTORY)    # First our parent directory
        # Now our sub-directories : node {1,2,3}
        os.mkdir(NODE_1_DIRECTORY)
        os.mkdir(NODE_2_DIRECTORY)
        os.mkdir(NODE_3_DIRECTORY)

    except FileExistsError:
        print("You must delete all directories before creating new privnet!")
        sys.exit(1)

def generate_priv_keys():
    # Lets store our keys, addresses & enode address inside the file "private_keys.json" file    
    priv_json = {
        "node_1": {
            "private_key": PRIV_KEY_1,
            "address": Account.from_key(PRIV_KEY_1).address,
            "enode": ENODE_PREFIX + ENODE_PRIV_1.publicKey().toString() + "@" + IP_ADDRESS_1 + ":" + str(PORT_1)
        },
        "node_2": {
            "private_key": PRIV_KEY_2,
            "address": Account.from_key(PRIV_KEY_2).address,
            "enode": ENODE_PREFIX + ENODE_PRIV_2.publicKey().toString() + "@" + IP_ADDRESS_2 + ":" + str(PORT_2)
        },
        "node_3": {
            "private_key": PRIV_KEY_3,
            "address": Account.from_key(PRIV_KEY_3).address,
            "enode": ENODE_PREFIX + ENODE_PRIV_3.publicKey().toString() + "@" + IP_ADDRESS_3 + ":" + str(PORT_3)
        }
    }

    print("Writing to private_keys.json...")
    json_object = json.dumps(priv_json, indent=4) # Dict -> JSON object

    with open(QNG_DIRECTORY + "/private_keys.json", "w") as json_file:
        json_file.write(json_object)
    
def gen_binary():
    # Generate our custom extraData field here
    print("Generating custom extraData field...")

    vanity = "0" * 64   # 32 bytes
    sealer_addr_1 = Account.from_key(PRIV_KEY_1).address[2:]    # Truncate "0x"
    sealer_addr_2 = Account.from_key(PRIV_KEY_2).address[2:]
    sealer_addr_3 = Account.from_key(PRIV_KEY_3).address[2:]

    sig = "0" * 130     # 65 bytes
    # Edit this to decide who becomes a sealer
    extraData = "0x" + vanity + sealer_addr_1 + sealer_addr_2 + sealer_addr_3 + sig  

    # Modiy custom_amana.json file
    with open("custom_amana_template.json", "r+") as json_file:
        amana_gen = json.load(json_file)
        amana_gen["extraData"] = extraData
        
        # allocate some funds to specified accounts 
        # e.g. amana_gen["alloc"] = {"0x123ABC....": {"balance": "0x33b2e3c9fd0803ce8000000"}, ...}        
        amana_gen["alloc"] = {
            Account.from_key(PRIV_KEY_1).address: {"balance": "0x33b2e3c9fd0803ce8000000"}
        }
        
        # Write new json object to file
        with open("custom_amana.json", "w") as json_file:
            json_file.write(json.dumps(amana_gen, indent=4))
        
    # Copy the genesis file to each node directory
    subprocess.Popen("cp custom_amana.json " + NODE_1_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp custom_amana.json " + NODE_2_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp custom_amana.json " + NODE_3_DIRECTORY, shell=True).wait()


def create_node_files():
    # Copy binary into eacb one of the nodes
    subprocess.Popen("cp " + QNG_BINARY + " " + NODE_1_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp " + QNG_BINARY + " " + NODE_2_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp " + QNG_BINARY + " " + NODE_3_DIRECTORY, shell=True).wait()

    # Run cleanup to generate the neccesary files for nodes
    subprocess.Popen(NODE_1_DIRECTORY + "/qng --privnet -A " + NODE_1_DIRECTORY + " --amana --cleanup", shell=True).wait()
    subprocess.Popen(NODE_2_DIRECTORY + "/qng --privnet -A " + NODE_2_DIRECTORY + " --amana --cleanup", shell=True).wait()
    subprocess.Popen(NODE_3_DIRECTORY + "/qng --privnet -A " + NODE_3_DIRECTORY + " --amana --cleanup", shell=True).wait()
    
      # Add the network key to each node
    with open(NODE_1_DIRECTORY + "/data/privnet/network.key", "w") as network_key_file:
        network_key_file.write(ENODE_PRIV_1.toString())

    with open(NODE_2_DIRECTORY + "/data/privnet/network.key", "w") as network_key_file:
        network_key_file.write(ENODE_PRIV_2.toString())
    
    with open(NODE_3_DIRECTORY + "/data/privnet/network.key", "w") as network_key_file:
        network_key_file.write(ENODE_PRIV_3.toString())
    
     
def keystore():
    print("Generating keystore files for each node...")

    # Create keystore directories
    os.mkdir(NODE_1_DIRECTORY + "/data/privnet/keystore")
    os.mkdir(NODE_2_DIRECTORY + "/data/privnet/keystore")
    os.mkdir(NODE_3_DIRECTORY + "/data/privnet/keystore")

    with open(NODE_1_DIRECTORY + "/data/privnet/keystore/keystore_1.json", "w") as node1_file:

        # Encrypt our private key using the passphrase "amana1"
        node_1_json = json.dumps(Account.encrypt(PRIV_KEY_1, "amana1"), indent=4)
        node1_file.write(node_1_json)
    
    with open(NODE_2_DIRECTORY + "/data/privnet/keystore/keystore_2.json", "w") as node2_file:

        node_2_json = json.dumps(Account.encrypt(PRIV_KEY_2, "amana1"), indent=4)
        node2_file.write(node_2_json)
    
    with open(NODE_3_DIRECTORY + "/data/privnet/keystore/keystore_3.json", "w") as node3_file:

        # Encrypt our private key using the passphrase "amana1"
        node_3_json = json.dumps(Account.encrypt(PRIV_KEY_3, "amana1"), indent=4)
        node3_file.write(node_3_json)
    
    # Password files to unlock accounts
    subprocess.Popen("cp password.txt " + NODE_1_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp password.txt " + NODE_2_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp password.txt " + NODE_3_DIRECTORY, shell=True).wait()
    

def gen_config(config_num: int) -> str:
    # num -> ETH address
    num_to_address = { 1: Account.from_key(PRIV_KEY_1).address,
                       2: Account.from_key(PRIV_KEY_2).address,
                       3: Account.from_key(PRIV_KEY_3).address }
    
    num_to_port = { 1: PORT_1, 2: PORT_2, 3: PORT_3 }
    # http_port = {1: 8545, 2: 8546, 3: 8547}
    enode_addrs = { 1: ENODE_PREFIX + ENODE_PRIV_1.publicKey().toString() + "@" + IP_ADDRESS_1 + ":" + str(PORT_1),
                    2: ENODE_PREFIX + ENODE_PRIV_2.publicKey().toString() + "@" + IP_ADDRESS_2 + ":" + str(PORT_2),
                    3: ENODE_PREFIX + ENODE_PRIV_3.publicKey().toString() + "@" + IP_ADDRESS_3 + ":" + str(PORT_3) }
    
    bootnodeToConfig = { 1: enode_addrs[2] + "," + enode_addrs[3], 
                         2: enode_addrs[1] + "," + enode_addrs[3], 
                         3: enode_addrs[1] + "+" + enode_addrs[2] }
    
    # Weird formatting but must be kept like this - do not alter!
    # We will disable blockDAG RPC as this is not needed if solely using Amana
    # Update - disabled the RPC server for qng EVM

    config_text = f'''privnet=true
amana=true
amanaenv="--unlock { num_to_address[config_num] } --password password.txt --port { num_to_port[config_num] } --bootnodes { bootnodeToConfig[config_num] } --miner.pending.feeRecipient { num_to_address[config_num] } --mine"
amanagen="custom_amana.json"
norpc=true
evmenv="--nodiscover --networkid 0 --port 0"

    '''
    return config_text

def create_config():
    print("Creating configuration files for nodes...")

    with open(NODE_1_DIRECTORY + "/config_1.toml", "w") as config_file:
        config_text = gen_config(1)
        config_file.write(config_text)

    with open(NODE_2_DIRECTORY + "/config_2.toml", "w") as config_file:
        config_text = gen_config(2)
        config_file.write(config_text)

    with open(NODE_3_DIRECTORY + "/config_3.toml", "w") as config_file:
        config_text = gen_config(3)
        config_file.write(config_text)


def main():
    create_directories()
    generate_priv_keys()
    gen_binary()
    create_node_files()
    keystore()
    create_config()
    print("\n\nNodes should now be ready to start!")

if __name__ == "__main__":
    main()

