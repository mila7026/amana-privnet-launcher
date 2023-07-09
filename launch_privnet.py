import os
from eth_account import Account
import secrets
import json
import sys
import subprocess


# We will assume "qng" directory to be located in users home directory 
QNG_DIRECTORY = os.path.expanduser("~") + "/qng_privnet"
NODE_1_DIRECTORY =  QNG_DIRECTORY + "/node1"
NODE_2_DIRECTORY =  QNG_DIRECTORY + "/node2"
NODE_3_DIRECTORY =  QNG_DIRECTORY + "/node3"
GENESIS_SOURCE_CODE = os.path.expanduser("~") + "/qng/meerevm/amana/genesis.go"
QNG_BINARY = os.path.expanduser("~") + "/qng/build/bin/qng"


PRIV_KEY_1 = "0x" + secrets.token_hex(32)  # generate 256 bit (32 bytes) private key
PRIV_KEY_2 = "0x" + secrets.token_hex(32)  
PRIV_KEY_3 = "0x" + secrets.token_hex(32)  



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

    # Lets store our keys and addresses inside the file "private_keys.json" file
    
    priv_json = {

        "node_1": {
            "private_key": PRIV_KEY_1,
            "address": Account.from_key(PRIV_KEY_1).address
        },

        "node_2": {
            "private_key": PRIV_KEY_2,
            "address": Account.from_key(PRIV_KEY_2).address
        },

        "node_3": {
            "private_key": PRIV_KEY_3,
            "address": Account.from_key(PRIV_KEY_3).address
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

    extraData = "0x" + vanity + sealer_addr_1 + sealer_addr_2 + sealer_addr_3 + sig  


    print("Modifying genesis.go...")

    if os.stat(GENESIS_SOURCE_CODE).st_size == 0:

        print("Genesis source file cannot be empty!")
        sys.exit(1)
        

    custom_genesis = ""

    with open("genesis.go", "r") as genesis_file:

        read_content = genesis_file.read()
        
        repl_extra_data = read_content.replace("0x000000000000000000000000000000000000000000000000000000000000000071bc4403af41634cda7c32600a8024d54e7f64990000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                                 extraData)
        
        repl_alloc_ether = repl_extra_data.replace("0x71bc4403af41634cda7c32600a8024d54e7f6499", Account.from_key(PRIV_KEY_1).address) 
        custom_genesis = repl_alloc_ether
    

    with open(GENESIS_SOURCE_CODE, "w") as orig_binary:
        orig_binary.write(custom_genesis) # replace genesis.go with our modified version

    
    # Lets compile our new binary from source code
    print ("Compiling qng binary...")

    #subprocess.Popen("/bin/bash && source ~/.profile && cd ~/qng && make") # Force Python to use "bash" instead of default "sh", source .profile to ensure "go" can be accessed 

    # subprocess.Popen("/bin/bash; source .profile && cd ~/qng && make", shell=True, executable='/bin/bash').wait()
    subprocess.Popen("cd " + os.path.expanduser("~") + "/qng && make", shell=True).wait()


def create_node_files():

    # Copy binary into eacb one of the nodes
    subprocess.Popen("cp " + QNG_BINARY + " " + NODE_1_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp " + QNG_BINARY + " " + NODE_2_DIRECTORY, shell=True).wait()
    subprocess.Popen("cp " + QNG_BINARY + " " + NODE_3_DIRECTORY, shell=True).wait()

    # Run cleanup to generate the neccesary files for nodes
    subprocess.Popen(NODE_1_DIRECTORY + "/qng --privnet -A " + NODE_1_DIRECTORY + " --amana --cleanup", shell=True).wait()
    subprocess.Popen(NODE_2_DIRECTORY + "/qng --privnet -A " + NODE_2_DIRECTORY + " --amana --cleanup", shell=True).wait()
    subprocess.Popen(NODE_3_DIRECTORY + "/qng --privnet -A " + NODE_3_DIRECTORY + " --amana --cleanup", shell=True).wait()


            
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


def gen_config(config_num:int) -> str:

    # num -> ETH address
    num_to_address = {1: Account.from_key(PRIV_KEY_1).address,
                      2: Account.from_key(PRIV_KEY_2).address,
                      3: Account.from_key(PRIV_KEY_3).address}
    
    num_to_port = {1: 38528, 2:38529, 3: 38530}

    
    # Weird formatting but must be kept like this - do not alter!
    # We will disable RPC as this is not needed if solely using Amana

    config_text = f'''privnet=true
amana=true
amanaenv="--unlock {num_to_address[config_num]} --password password.txt --http.port {num_to_port[config_num]} --miner.etherbase {num_to_address[config_num]} --mine"
norpc=true
p2ptcpport={num_to_port[config_num]}
p2pudpport={num_to_port[config_num]}

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



main()











