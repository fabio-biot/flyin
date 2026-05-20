# class ReadError(Exception):
#     def __init__(self, message: str):
#         self.message = message
#         super().__init__(message)

class Simulation:
    def __init__(self, network, drones):
        self.network = network
        self.drones = drones
        self.turn = 0

    def run(self, pathfinder):
        drone = self.drones[0]

        drone.path = pathfinder.find_path(
            self.network.start_hub,
            self.network.end_hub
        )

        index = 0

        while index < len(drone.path) - 1:

            current = drone.path[index]
            next_hub = drone.path[index + 1]

            drone.current_hub = next_hub
            index += 1
            self.turn += 1

            print(f"Turn {self.turn}: D{drone.id}-{next_hub.name}")

        print("DONE")


class Hub():
    def __init__(self, name, x, y, zone_type="normal", color="none", max_drones=1):
        self.name = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: str = color
        self.max_drones: int = max_drones
        self.nb_drones: int = 0
        self.connections: list[Connection] = []
    def get_neighbors(self) -> list["Hub"]:
        neighbors = []
        for connection in self.connections:
            neighbors.append(connection.other_side(self))
        return neighbors


class Connection:
    def __init__(self, hub1: Hub, hub2: Hub, max_capacity: int = 1):
        self.hub1: Hub = hub1
        self.hub2: Hub = hub2
        self.max_capacity: int = max_capacity
        self.drones_in_transit: list["Drone"] = []

    def other_side(self, current: Hub) -> Hub:
        if current == self.hub1:
            return self.hub2
        return self.hub1


class Drone:
    def __init__(self, drone_id: int, start_hub: Hub):
        self.id: int = drone_id
        self.current_hub: Hub = start_hub
        self.path: list[Hub] = []
        self.remaining_turns: int = 0
        self.current_connection: Connection = None


class Move:
    def __init__(self, drone, source, destination, connection):
        self.drone: Drone = drone
        self.source: Hub = source
        self.destination: Hub = destination
        self.connection: Connection = connection


class Network:
    def __init__(self):
        self.connections: list[Connection] = []
        self.hubs: dict[str, Hub] = {}
        self.start_hub: Hub = None
        self.end_hub: Hub = None


class StartHub(Hub):
    def __init__(self, nb_drones_sim):
        super().__init__()
        self.nb_drones = nb_drones_sim


class EndHub(Hub):
    def __init__(self):
        super().__init__()


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


class Pathfinder:
    def __init__(self):
        pass

    def find_path(self, start: Hub, end: Hub):
        queue = [[start]]
        visited = set()

        while(queue):
            path = queue.pop(0)
            current_hub = path[-1]
            if current_hub == end:
                return path
            if current_hub in visited:
                continue
            visited.add(current_hub)
            for neighbor in current_hub.get_neighbors():
                if neighbor.zone_type == "blocked":
                    continue
                new_path = path + [neighbor]
                queue.append(new_path)
            
        return None