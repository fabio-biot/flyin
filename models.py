from __future__ import annotations
from dataclasses import dataclass


class ParserError(Exception):
    pass


@dataclass
class PathInfo:
    path: list[Hub]
    cost: float
    load: int
    bottleneck: int


class Hub():
    def __init__(self, name: str, x: int,
                 y: int, zone_type: str = "normal",
                 color: str = "none",
                 max_drones: int = 1) -> None:
        self.name: str = name
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

    def get_rvb_color(self) -> tuple[int, int, int]:
        if self.color == "red":
            return (255, 0, 0)
        elif self.color == "green":
            return (0, 255, 0)
        elif self.color == "blue":
            return (0, 0, 255)
        elif self.color == "yellow":
            return (255, 255, 0)
        elif self.color == "cyan":
            return (0, 255, 255)
        elif self.color == "magenta":
            return (255, 0, 255)
        else:
            return (200, 200, 200)


class Simulation:
    def __init__(self, network: Network,
                 drones: list[Drone],
                 pathfinder: Pathfinder) -> None:
        self.network: Network = network
        self.drones: list[Drone] = drones
        self.pathfinder: Pathfinder = pathfinder
        self.turn: int = 0
        self.all_deliv: bool = False

    def init_paths(self) -> None:
        self.assign_paths()
        for drone in self.drones:
            drone.next_index = 0

    def run(self, pathfinder: Pathfinder) -> None:
        self.init_paths()

        while not self.all_delivered():
            self.turn += 1
            moves = self.resolve_transits()
            moves.extend(self.compute_turn())
            self.apply_moves(moves)
            self.print_turn(moves)

        print("ALL DRONES DELIVERED =", self.all_delivered())
        self.all_deliv = True

    def run_pygame(self, pathfinder: Pathfinder) -> None:
        self.init_paths()

        while not self.all_delivered():
            self.turn += 1
            moves = self.resolve_transits()
            moves.extend(self.compute_turn())
            self.apply_moves(moves)
            self.print_turn(moves)

        print("ALL DRONES DELIVERED =", self.all_delivered())

    def all_delivered(self) -> bool:
        return all(d.delivered for d in self.drones)

    def process_transit(
        self,
        drone: Drone,
        moves: list[
            tuple[
                Drone,
                Hub | Connection,
                Hub | Connection,
                str,
            ]
        ],
    ) -> None:
        if drone.target_hub is None:
            return

        if drone.current_connection is None:
            return

        connection = drone.current_connection
        target = drone.target_hub

        drone.remaining_turns = 0
        drone.current_hub = target
        drone.target_hub = None
        drone.current_connection = None
        drone.in_transit = False

        moves.append(
            (drone, connection, target, "a")
        )

    def compute_turn(self) -> list[tuple[Drone, Hub | Connection, Hub |
                                         Connection, str]]:
        moves: list[
            tuple[Drone, Hub | Connection, Hub | Connection, str]
            ] = []
        used_connections: dict[Connection, int] = {}
        occupancy = self.get_occupancy()

        # print(turn)
        for drone in self.drones:
            if drone.delivered:
                # print("siud")
                continue
            if drone.in_transit:
                # print("drone.id")
                # print(drone.id)
                # print(f"drone.in_transit {drone.in_transit}")
                # print(f"drone.target hub {drone.target_hub.name}")
                # print(f"drone connection {drone.
                # current_connection.hub1.name}
                # -{drone.current_connection.hub2.name}")
                continue

            path = drone.path
            i = drone.next_index
            if i >= len(path) - 1:
                continue

            current = path[i]
            next_hub = path[i + 1]

            # print(f"drone = {drone.id}")
            # for i in range(len(path)):
            #     print(f"path = {path[i].name}")
            # print(f"current = {current.name} et next = {next_hub.name}")
            # print(f"current_count = {current_count}
            # et max = {next_hub.max_drones}")
            if next_hub != self.network.end_hub:
                if occupancy.get(next_hub, 0) >= next_hub.max_drones:
                    continue

            connection = None
            for c in self.network.connections:
                if c.other_side(current) == next_hub:
                    connection = c
                    break

            if connection is None:
                continue

            used_connections.setdefault(connection, 0)
            if used_connections[connection] >= connection.max_capacity:
                continue
            used_connections[connection] += 1
            if next_hub.zone_type == "restricted":
                drone.in_transit = True
                drone.remaining_turns = 2
                drone.target_hub = next_hub
                drone.current_connection = connection
                # print("Je suis restricted apres")
                moves.append((drone, current, connection, 'b'))
                continue
            # print(f"occupancy of {current.name} = {occupancy[current]}")
            moves.append((drone, current, next_hub, 'a'))
            # print("NEXT ZONE RESTRICTED")

            # print(f"{current_connection.hub1.name} <->
            # {current_connection.hub2.name} nb_transit_turn =")
            # print(f"{current_connection.nb_transit_turn}")
            occupancy[current] = occupancy.get(current, 0) - 1
            occupancy[next_hub] = occupancy.get(next_hub, 0) + 1
            # print(f"{drone.id} -> {drone.current_hub.name}")
        # for d in self.drones:
        #     print(f"D{d.id} at} (delivered={d.delivered})")
        return moves

    def apply_moves(self,
                    moves: list[
            tuple[Drone, Hub | Connection, Hub | Connection, str]
            ],
    ) -> None:
        for drone, src, dst, mode in moves:
            if drone.delivered:
                continue

            if mode == "a":
                if not isinstance(src, Hub):
                    continue

                if not isinstance(dst, Hub):
                    continue

                drone.anim_from = src
                drone.anim_to = dst
                drone.anim_progress = 0.0
                drone.animating = True
                drone.current_hub = dst

                drone.next_index += 1

                if drone.current_hub == self.network.end_hub:
                    drone.delivered = True
                    drone.next_index = len(drone.path) - 1

                drone.remaining_turns = 0
                drone.target_hub = None
                drone.current_connection = None
                drone.in_transit = False

            elif mode == "b":
                if not isinstance(src, Hub):
                    continue

                if not isinstance(dst, Connection):
                    continue

                drone.in_transit = True
                drone.remaining_turns = 2
                drone.current_connection = dst
                drone.current_hub = None
                drone.target_hub = dst.other_side(src)

            else:
                raise ValueError(f"Unknown mode: {mode}")

    def update_animation(self, dt: float = 0.1) -> None:
        for drone in self.drones:
            if not drone.animating:
                continue

            drone.anim_progress += dt

            if drone.anim_progress >= 1.0:
                drone.anim_progress = 1.0
                drone.animating = False

    def print_turn(
            self,
            moves: list[
                tuple[Drone, Hub | Connection, Hub | Connection, str]
            ],
            ) -> None:
        if not moves:
            print()
            return

        line: list[str] = []

        for drone, src, dst, mode in moves:
            if mode == "b":
                if not isinstance(dst, Connection):
                    continue

                line.append(
                    f"D{drone.id}-{dst.hub1.name}-{dst.hub2.name}"
                )
            elif mode == "a":
                if not isinstance(dst, Hub):
                    continue
                line.append(f"D{drone.id}-{dst.name}")
            else:
                raise ValueError(f"Unknown mode: {mode}")
        print(" ".join(line))

    def get_occupancy(self) -> dict[Hub, int]:
        occupancy: dict[Hub, int] = {}

        for drone in self.drones:
            if drone.delivered:
                continue

            if drone.current_hub is None:
                continue

            hub = drone.current_hub
            occupancy[hub] = occupancy.get(hub, 0) + 1
        return occupancy

    def resolve_transits(self) -> list[tuple[Drone,
                                             Hub | Connection,
                                             Hub | Connection,
                                             str]]:
        moves: list[
            tuple[Drone, Hub | Connection, Hub | Connection, str]
        ] = []

        for drone in self.drones:
            if not drone.in_transit:
                continue
            drone.remaining_turns -= 1
            if drone.remaining_turns > 0:
                continue
            if drone.target_hub is None:
                continue
            if drone.current_connection is None:
                continue
            target = drone.target_hub
            connection = drone.current_connection

            drone.current_hub = target
            drone.target_hub = None
            drone.current_connection = None
            drone.in_transit = False
            drone.next_index += 1
            if drone.current_hub == self.network.end_hub:
                drone.delivered = True
            moves.append((drone, connection, target, "a"))

        return moves

    def assign_paths(self) -> None:
        if self.network.start_hub is None:
            raise ValueError("Network has no start hub")

        if self.network.end_hub is None:
            raise ValueError("Network has no end hub")

        all_paths = self.pathfinder.find_all_paths_with_cost(
            self.network.start_hub,
            self.network.end_hub,
        )
        path_infos: list[PathInfo] = []

        for path, cost in all_paths:
            bottleneck = min(
                (h.max_drones for h in path[1:-1]),
                default=1,
            )

            path_infos.append(
                PathInfo(
                    path=path,
                    cost=cost,
                    load=0,
                    bottleneck=bottleneck,
                )
            )

        for drone in self.drones:
            best: PathInfo | None = None
            best_score = float("inf")

            for info in path_infos:
                load_after = info.load + 1
                delay = load_after // info.bottleneck
                score = info.cost + delay

                if score < best_score:
                    best_score = score
                    best = info

            if best is None:
                raise TypeError("Error, no path found")

            drone.path = best.path
            best.load += 1
            drone.next_index = 0

    def reset(self, drones: list[Drone]) -> None:
        self.drones = drones
        self.turn = 0
        self.init_paths()


class Connection:
    def __init__(self, hub1: "Hub", hub2: "Hub", max_capacity: int = 1):
        self.hub1: Hub = hub1
        self.hub2: Hub = hub2
        self.max_capacity: int = max_capacity

    def other_side(self, hub: "Hub") -> "Hub":
        return self.hub2 if hub == self.hub1 else self.hub1

    def is_between(self, a: "Hub", b: "Hub") -> bool:
        return (self.hub1 == a
                and self.hub2 == b) or (self.hub1 == b and self.hub2 == a)


class Drone:
    def __init__(self, drone_id: int, start_hub: Hub):
        self.id: int = drone_id
        self.current_hub: Hub | None = start_hub
        self.path: list[Hub] = []
        self.next_index: int = 0
        self.delivered: bool = False

        self.in_transit: bool = False
        self.remaining_turns: int = 0
        self.target_hub: Hub | None = None
        self.current_connection: Connection | None = None

        self.anim_from: Hub | None = None
        self.anim_to: Hub | None = None
        self.anim_progress: float = 0.0
        self.animating: bool = False


class Move:
    def __init__(self,
                 drone: Drone,
                 source: Hub | Connection,
                 destination: Hub | Connection,
                 connection: Connection) -> None:
        self.drone: Drone = drone
        self.source: Hub | Connection = source
        self.destination: Hub | Connection = destination
        self.connection: Connection = connection


class Network:
    def __init__(self) -> None:
        self.connections: list[Connection] = []
        self.hubs: dict[str, Hub] = {}
        self.start_hub: StartHub | None = None
        self.end_hub: EndHub | None = None


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
        self, name: str, x: int, y: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 999999,
    ) -> None:
        super().__init__(
            name, x, y,
            zone_type,
            color, max_drones
        )


class Parser:
    def __init__(self, path: str) -> None:
        self.path: str = path

    def parse(self) -> tuple[Network, int]:
        network = Network()
        nb_drones = 0
        seen_connections: set[tuple[str, str]] = set()

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
                try:
                    nb_drones = int(line.split(":")[1].strip())
                except ValueError as e:
                    raise ValueError(f"nb_drones should be an int {e}")

            elif line.startswith("start_hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])

                zone_type, color, max_drones = self.parse_metadata(
                    parts[4:],
                    nb_drones,
                )

                start_hub = StartHub(
                    name,
                    x,
                    y,
                    nb_drones,
                    zone_type,
                    color,
                    max_drones,
                )

                network.hubs[name] = start_hub
                network.start_hub = start_hub

            elif line.startswith("end_hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])

                zone_type, color, max_drones = self.parse_metadata(
                    parts[4:],
                    nb_drones,
                )

                end_hub = EndHub(
                    name,
                    x,
                    y,
                    zone_type,
                    color,
                    max_drones,
                )

                network.hubs[name] = end_hub
                network.end_hub = end_hub

            elif line.startswith("hub:"):
                parts = line.split()
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])

                zone_type, color, max_drones = self.parse_metadata(
                    parts[4:],
                    nb_drones,
                )

                hub = Hub(
                    name,
                    x,
                    y,
                    zone_type,
                    color,
                    max_drones,
                )

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
                max_link_capacity: int = nb_drones
                if len(parts) > 2:
                    meta = " ".join(parts[2:]).strip("[]")
                    for tag in meta.split():
                        key, value = tag.split("=")
                        if key == "max_link_capacity":
                            max_link_capacity = int(value)
                if max_link_capacity <= 0:
                    raise ValueError(
                        "max_link_capacity must be > 0"
                    )
                connection_key: tuple[str, str] = (
                    min(node1, node2),
                    max(node1, node2),
                )
                if connection_key in seen_connections:
                    raise ValueError(
                        f"Duplicate connection {node1}-{node2}"
                    )
                seen_connections.add(connection_key)
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

    def parse_metadata(
        self,
        meta_parts: list[str],
        nb_drones: int,
    ) -> tuple[str, str, int]:
        color = "none"
        zone_type = "normal"
        max_drones = nb_drones
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
        if max_drones is None:
            raise ValueError("max_drones is NULL !")
        if zone_type not in VALID_TYPES:
            raise ValueError(f"Invalid zone type: {zone_type}")
        return zone_type, color, max_drones


class Pathfinder:
    def __init__(self) -> None:
        pass

    def zone_cost(self, hub: Hub) -> int | float:
        if hub.zone_type == "restricted":
            return 2
        if hub.zone_type == "priority":
            return 0.9
        if hub.zone_type == "blocked":
            return float("inf")
        return 1  # normal + priority

    # def find_path(self, start: Hub, end: Hub) -> list[Hub]:
    #     queue = [start]
    #     visited = set()
    #     prev: dict[Hub, Hub | None] = {start: None}
    #     distance: dict[Hub, int] = {start: 0}

    #     while queue:
    #         current = min(queue, key=lambda hub: distance[hub])
    #         queue.remove(current)

    #         visited.add(current)

    #         if current == end:
    #             break

    #         for connection in current.connections:
    #             neighbor = connection.other_side(current)
    #             if neighbor in visited:
    #                 continue
    #             if neighbor.zone_type == "blocked":
    #                 continue

    #             cost = self.zone_cost(neighbor)
    #             new_dist = distance[current] + cost

    #             if new_dist < distance.get(neighbor, float("inf")):
    #                 distance[neighbor] = new_dist
    #                 prev[neighbor] = current
    #                 queue.append(neighbor)

    #     if end not in prev:
    #         return []

    #     path = []
    #     node = end

    #     while node is not None:
    #         path.append(node)
    #         node = prev[node]

    #     path.reverse()
    #     return path

    def find_all_paths_with_cost(
        self,
        start: Hub,
        end: Hub,
    ) -> list[tuple[list[Hub], float]]:
        queue: list[list[Hub]] = [[start]]
        all_paths: list[tuple[list[Hub], float]] = []

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

        return all_paths
