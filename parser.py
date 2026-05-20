from models import StartHub, EndHub, Hub, Drone, Connection, Parser


    
def params(data):
    nb_drones = "nb_drones: x"
    start_hub = StartHub("start", 0, 0, max_drones, zone_type, color)
        

def main():
    parser = Parser("maps/easy/01_linear_path.txt")
    network, nb_drones = parser.parse()
    print(f"network {network}")
    for i in  range(len(network.connections)):
        print(f"Connection {i} = ")
        print(f"network {network.connections[i].hub1.name} à {network.connections[i].hub2.name}")
    print(f"network {network.hubs['goal'].x}")
    print(f"nb drones {nb_drones}")

if __name__ == "__main__":
    main()
