class ParserError(Exception):
    pass

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


class Simulation:
    def __init__(self, network, drones, pathfinder):
        self.network = network
        self.drones = drones
        self.pathfinder = pathfinder
        self.turn = 0

    def init_paths(self):
        self.assign_paths()
        for drone in self.drones:
            drone.next_index = 0

    def run(self, pathfinder):
        self.init_paths()
        while not self.all_delivered():
            for d in self.drones:
                d.reset_if_invalid()
            self.turn += 1
            moves = self.compute_turn()
            self.apply_moves(moves)
            self.print_turn(moves)
        print("ALL DRONES DELIVERED =", self.all_delivered())

    def all_delivered(self):
        return all(d.delivered for d in self.drones)
    
    def compute_turn(self, pathfinder=None):
        moves = []
        occupancy = self.get_occupancy()
        connections = self.network.connections

        for drone in self.drones:
            if drone.delivered:
                continue

            if drone.remaining_turns > 0:
                drone.remaining_turns -= 1
                if drone.remaining_turns == 0:
                    dst = drone.destination
                    drone.current_hub = dst
                    drone.destination = None
                    drone.current_connection = None
                    drone.next_index += 1

                    if dst == self.network.end_hub:
                        drone.delivered = True
                continue

            path = drone.path
            i = drone.next_index

            if drone.current_hub == self.network.end_hub:
                drone.delivered = True
                continue

            if i >= len(path) - 1:
                if drone.current_hub == self.network.end_hub:
                    drone.delivered = True
                else:
                    drone.delivered = True
                    drone.current_hub = self.network.end_hub
                continue

            current = path[i]
            next_hub = path[i + 1]

            current_count = occupancy.get(next_hub, 0)

            if next_hub != self.network.end_hub and current_count >= next_hub.max_drones:
                continue

            current_connection = None
            for c in connections:
                if (c.hub1 == current and c.hub2 == next_hub) or (c.hub2 == current and c.hub1 == next_hub):
                    current_connection = c
                    break

            if current_connection is None:
                continue

            if current_connection.nb_transit_turn >= current_connection.max_capacity:
                continue

            if next_hub.zone_type == "restricted":
                drone.remaining_turns = 1
                drone.destination = next_hub
                drone.current_connection = current_connection
                current_connection.nb_transit_turn += 1
                occupancy[current] = occupancy.get(current, 0) - 1
                moves.append((drone, current, next_hub))
                continue

            moves.append((drone, current, next_hub))
            current_connection.nb_transit_turn += 1

        for c in connections:
            c.nb_transit_turn = 0

        return moves
        

    def apply_moves(self, moves):
        for drone, src, dst in moves:

            if drone.delivered:
                continue
            if isinstance(dst, str):
                continue
            drone.current_hub = dst
            if drone.path:
                try:
                    idx = drone.path.index(dst)
                    drone.next_index = idx
                except ValueError:
                    pass
            if drone.current_hub == self.network.end_hub:
                drone.delivered = True
                drone.next_index = len(drone.path) - 1

            drone.remaining_turns = 0
            drone.destination = None
            drone.current_connection = None
    
    def print_turn(self, moves):
        if not moves:
            print()
            return

        line = []
        for drone, src, dst in moves:
            line.append(f"D{drone.id}-{dst.name}")

        print(" ".join(line))
    
    def get_occupancy(self) -> dict[Hub, int]:
        occupancy = {}

        for drone in self.drones:
            if drone.delivered:
                continue
            hub = drone.current_hub
            occupancy[hub] = occupancy.get(hub, 0) + 1
        return occupancy
    
    def assign_paths(self):
        all_paths = self.pathfinder.find_all_paths_with_cost(
            self.network.start_hub,
            self.network.end_hub
        )
        path_infos = []

        for path, cost in all_paths:
            bottleneck = min(
                (h.max_drones for h in path[1:-1]),
                default=1
            )

            path_infos.append({
                "path": path,
                "cost": cost,
                "load": 0,
                "bottleneck": bottleneck,
            })

        for drone in self.drones:
            best = None
            best_score = float("inf")

            for info in path_infos:
                load_after = info["load"] + 1
                delay = load_after // info["bottleneck"]
                score = info["cost"] + delay

                if score < best_score:
                    best_score = score
                    best = info

            drone.path = best["path"]
            best["load"] += 1
            drone.next_index = 0


class Connection:
    def __init__(self, hub1: Hub, hub2: Hub, max_capacity: int):
        self.hub1: Hub = hub1
        self.hub2: Hub = hub2
        self.nb_transit_turn: int = 0
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
        self.restricted_lock: bool = False
        self.current_connection: Connection = None
        self.next_index = 0
        self.delivered = False
    
    def reset_if_invalid(self):
        if self.path and self.next_index >= len(self.path):
            self.next_index = len(self.path) - 1


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
        self.start_hub: StartHub = None
        self.end_hub: EndHub = None


class StartHub(Hub):
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        nb_drones_sim: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 999999,
    ):
        super().__init__(
            name,
            x,
            y,
            zone_type,
            color,
            max_drones
        )
        self.nb_drones_sim = nb_drones_sim


class EndHub(Hub):
    def __init__(
        self, name, x, y,
        zone_type="normal",
        color="none",max_drones=999999,
    ):
        super().__init__(
            name, x, y,
            zone_type,
            color, max_drones
        )


class Parser:
    def __init__(self, path):
        self.path = path

    def parse(self) -> tuple["Network", int]:
        network = Network()
        nb_drones = 0
        seen_connections = set()

        try:
            with open(self.path, "r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            raise ParserError(f"Error while reading {self.path}")

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
                zone_type, color, max_drones = self.parse_metadata(parts[4:])
                hub = StartHub(name, x, y, nb_drones, zone_type, color, max_drones)
                network.hubs[name] = hub
                network.start_hub = hub

            elif line.startswith("end_hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                zone_type, color, max_drones = self.parse_metadata(parts[4:])
                hub = EndHub(name, x, y, zone_type, color, max_drones)
                network.hubs[name] = hub
                network.end_hub = hub

            elif line.startswith("hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                zone_type, color, max_drones = self.parse_metadata(parts[4:])
                hub = Hub(name, x, y, zone_type, color, max_drones)
                if name in network.hubs:
                    raise ValueError(f"Duplicate hub '{name}'")
                network.hubs[name] = hub

            elif line.startswith("connection:"):
                parts = line.split()
                node1, node2 = parts[1].split("-")
                if node1 not in network.hubs:
                    raise ValueError(f"Unknown hub '{node1}'")
                if node2 not in network.hubs:
                    raise ValueError(f"Unknown hub '{node2}'")
                hub1 = network.hubs[node1]
                hub2 = network.hubs[node2]
                max_link_capacity = nb_drones
                if len(parts) > 2:
                    meta = " ".join(parts[2:]).strip("[]")
                    for tag in meta.split():
                        key, value = tag.split("=")
                        if key == "max_link_capacity":
                            max_link_capacity = int(value)
                if max_link_capacity <= 0:
                    raise ValueError("max_link_capacity must be > 0")
                key = tuple(sorted([node1, node2]))
                if key in seen_connections:
                    raise ValueError(f"Duplicate connection {node1}-{node2}")
                seen_connections.add(key)
                connection = Connection(hub1, hub2, max_link_capacity)
                network.connections.append(connection)
                hub1.connections.append(connection)
                hub2.connections.append(connection)
        if nb_drones <= 0:
            raise ValueError("Invalid or missing nb_drones")
        if network.start_hub is None:
            raise ValueError("Missing start_hub")
        if network.end_hub is None:
            raise ValueError("Missing end_hub")
        return network, nb_drones

    def parse_metadata(self, meta_parts: list[str]) -> tuple[str, str, int]:
        color = "none"
        zone_type = "normal"
        max_drones = 1
        VALID_TYPES = {"normal", "blocked", "restricted", "priority"}

        if not meta_parts:
            return zone_type, color, max_drones
        meta = " ".join(meta_parts).strip("[]")
        tags = meta.split()
        for tag in tags:
            key, value = tag.split("=")
            if key == "max_drones":
                if not value.isdigit():
                    raise ValueError("Value must be an int !")
            if key == "zone":
                zone_type = value
            elif key == "color":
                color = value
            elif key == "max_drones":
                max_drones = int(value)
        if max_drones <= 0:
            raise ValueError("max_drones must be > 0")
        if zone_type not in VALID_TYPES:
              raise ValueError(f"Invalid zone type: {zone_type}")
        return zone_type, color, max_drones


class Pathfinder:
    def __init__(self):
        pass

    def zone_cost(self, hub: Hub) -> int:
        if hub.zone_type == "restricted":
            return 2
        if hub.zone_type == "priority":
            return 0.9
        if hub.zone_type == "blocked":
            return float("inf")
        return 1  # normal + priority

    def find_path(self, start: Hub, end: Hub) -> list[Hub]:
        queue = [start]
        visited = set()
        prev: dict[Hub, Hub | None] = {start: None}
        distance: dict[Hub, int] = {start: 0}


        while queue:
            current = min(queue, key=lambda hub: distance[hub])
            queue.remove(current)

            visited.add(current)

            if current == end:
                break

            for connection in current.connections:
                neighbor = connection.other_side(current)
                if neighbor in visited:
                    continue
                if neighbor.zone_type == "blocked":
                    continue

                cost = self.zone_cost(neighbor)
                new_dist = distance[current] + cost
                
                if new_dist < distance.get(neighbor, float("inf")):
                    distance[neighbor] = new_dist
                    prev[neighbor] = current
                    queue.append(neighbor)

        if end not in prev:
            return []

        path = []
        node = end

        while node is not None:
            path.append(node)
            node = prev[node]

        path.reverse()
        return path


    def find_all_paths_with_cost(self, start: Hub, end: Hub) -> list[tuple[list[Hub], int]] :
        queue = [[start]]
        all_paths = []

        while queue:
            path = queue.pop(0)
            current = path[-1]

            if current == end:
                cost = sum(self.zone_cost(h) for h in path[1:])
                all_paths.append((path, cost))
                continue

            for connection in current.connections:
                neighbor = connection.other_side(current)

                if neighbor.zone_type == "blocked":
                    continue

                if neighbor in path:
                    continue

                new_path = path + [neighbor]
                queue.append(new_path)

        all_paths.sort(key=lambda x: x[1])

        # for u, c in all_paths:
        #     print(f"Cost: {c} - Path: {' -> '.join(h.name for h in u)}")
        return all_paths