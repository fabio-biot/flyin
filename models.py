# class ReadError(Exception):
#     def __init__(self, message: str):
#         self.message = message
#         super().__init__(message)

class Simulation:
    def __init__(self, network, drones):
        self.network = network
        self.drones = drones
        self.turn = 0

class Hub():
    def __init__(self, name, x, y, max_drones=None, zone_type="normal", color=None):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


class Connection:
    def __init__(self, hub1: Hub, hub2: Hub, max_capacity: int = 1):
        self.hub1 = hub1
        self.hub2 = hub2
        self.max_capacity = max_capacity
        self.drones_in_transit: list["Drone"] = []

    def other_side(self, current: Hub) -> Hub:
        if current == self.hub1:
            return self.hub2
        return self.hub1


class Drone:
    def __init__(self, drone_id: int, start_hub: Hub):
        self.id = drone_id
        self.current_hub = start_hub
        self.path: list[Hub] = []
        self.remaining_turns = 0
        self.current_connection = None


class Move:
    def __init__(self, drone, source, destination, connection):
        self.drone = drone
        self.source = source
        self.destination = destination
        self.connection = connection


class Network:
    def __init__(self):
        self.connections = {}
        self.hubs = []
        self.starthub = None
        self.endhub = None


class StartHub(Hub):
    def __init__(self):
        super().__init__()


class EndHub(Hub):
    def __init__(self):
        super().__init__()


class Drone():
    def __init__(self):
        pass


class Parser:
    def __init__(self, path):
        self.path = path

    def parse(self) -> tuple["Network", int]:
        network = Network()
        nb_drones = 0

        try:
            with open(self.path, "r") as file:
                lines = file.readlines()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error while reading {self.path}: {e}")
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("nb_drones:"):
                nb_drones = int(line.split(":")[1].strip())
            elif line.startswith("start_hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                zone_type, color, max_drones = self._parse_metadata(parts[4:])
                hub = Hub(name, x, y, zone_type, color, max_drones)
                network.hubs[name] = hub
                network.start_hub = hub
            elif line.startswith("end_hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                zone_type, color, max_drones = self._parse_metadata(parts[4:])
                hub = Hub(name, x, y, zone_type, color, max_drones)
                network.hubs[name] = hub
                network.end_hub = hub
            elif line.startswith("hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                zone_type, color, max_drones = self._parse_metadata(parts[4:])
                hub = Hub(name, x, y, zone_type, color, max_drones)
                network.hubs[name] = hub
            elif line.startswith("connection:"):
                parts = line.split()

                nodes = parts[1]
                node1_name, node2_name = nodes.split("-")

                hub1 = network.hubs[node1_name]
                hub2 = network.hubs[node2_name]

                max_link_capacity = 1

                # to get metadqata with good formating
                if len(parts) > 2:
                    meta = " ".join(parts[2:]).strip("[]")
                    for tag in meta.split():
                        key, value = tag.split("=")
                        if key == "max_link_capacity":
                            max_link_capacity = int(value)

                connection = Connection(hub1, hub2, max_link_capacity)

                network.connections.append(connection)

                hub1.connections.append(connection)
                hub2.connections.append(connection)

        return network, nb_drones

    def _parse_metadata(self, meta_parts: list[str]):
        zone_type = "normal"
        color = "none"
        max_drones = 1

        if not meta_parts:
            return zone_type, color, max_drones
        meta = " ".join(meta_parts).strip("[]")
        tags = meta.split()
        for tag in tags:
            key, value = tag.split("=")
            if key == "zone":
                zone_type = value
            elif key == "color":
                color = value
            elif key == "max_drones":
                max_drones = int(value)

        return zone_type, color, max_drones