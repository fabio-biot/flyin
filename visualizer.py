from __future__ import annotations
import pygame
from models import Drone, Hub, Network, Simulation

pygame.init()

WIDTH, HEIGHT = 2000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Simulation")
clock = pygame.time.Clock()


class Camera:
    def __init__(self, scale: int = 100,
                 offset_x: int = 200,
                 offset_y: int = 200) -> None:
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        return (
            int(x * self.scale + self.offset_x),
            int(y * self.scale + self.offset_y),
        )


class Visualizer:
    def __init__(self, network: Network, camera: Camera):
        self.network = network
        self.camera = camera
        self.font = pygame.font.SysFont("Arial", 20)

    def color_to_rgb(self,
                     color_name: str,
                     default: tuple[
                         int,
                         int,
                         int] = (0, 0, 255)) -> tuple[int, int, int]:
        palette = {
            "none": default,
            "green": (0, 255, 0),
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "orange": (255, 165, 0),
            "cyan": (0, 255, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
        }
        return palette.get(color_name, default)

    def draw_hub(self, hub: Hub) -> None:
        x, y = self.camera.world_to_screen(hub.x, hub.y)
        color = self.color_to_rgb(getattr(hub, "color", "none"),
                                  default=(0, 255, 0))
        pygame.draw.circle(screen, color, (x, y), 15)

    def draw_connections(self) -> None:
        for c in self.network.connections:
            x1, y1 = self.camera.world_to_screen(c.hub1.x, c.hub1.y)
            x2, y2 = self.camera.world_to_screen(c.hub2.x, c.hub2.y)
            pygame.draw.line(screen, (180, 180, 180), (x1, y1), (x2, y2), 2)

    def draw_drone(self, drone: Drone) -> None:
        x = 0.0
        y = 0.0

        if drone.in_transit:
            connection = drone.current_connection

            if connection is not None:
                connection_hub1 = connection.hub1
                connection_hub2 = connection.hub2

                t = drone.anim_progress

                x = (
                    connection_hub1.x
                    + (connection_hub2.x - connection_hub1.x) * t
                )
                y = (
                    connection_hub1.y
                    + (connection_hub2.y - connection_hub1.y) * t
                )

        elif drone.animating:
            animation_hub1 = drone.anim_from
            animation_hub2 = drone.anim_to

            if animation_hub1 is not None and animation_hub2 is not None:
                t = drone.anim_progress

                x = (
                    animation_hub1.x
                    + (animation_hub2.x - animation_hub1.x) * t
                )
                y = (
                    animation_hub1.y
                    + (animation_hub2.y - animation_hub1.y) * t
                )
            elif drone.current_hub is not None:
                x = drone.current_hub.x
                y = drone.current_hub.y

        elif drone.current_hub is not None:
            x = drone.current_hub.x
            y = drone.current_hub.y

        elif drone.target_hub is not None:
            x = drone.target_hub.x
            y = drone.target_hub.y

        sx, sy = self.camera.world_to_screen(x, y)

        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (sx, sy),
            8,
        )

    def draw_debug(self, game: Game) -> None:
        lines = [
            f"Turn: {game.sim.turn}",
            f"Drones: {len(game.sim.drones)}",
            f"Auto: {game.auto_play}",
        ]

        y = 10
        for line in lines:
            surf = self.font.render(line, True, (255, 255, 255))
            screen.blit(surf, (10, y))
            y += 22

    def draw(self, sim: Simulation) -> None:
        screen.fill((20, 20, 20))

        self.draw_connections()

        for hub in self.network.hubs.values():
            self.draw_hub(hub)

        for drone in sim.drones:
            self.draw_drone(drone)


class Game:
    def __init__(self, network: Network, sim: Simulation) -> None:
        self.network = network
        self.sim = sim
        self.camera = Camera()
        self.visualizer = Visualizer(network, self.camera)
        self.auto_play = False
        self.step_requested = False

    def update_animation(self, dt: float = 0.1) -> None:
        for drone in self.sim.drones:
            if not getattr(drone, "animating", False):
                continue

            drone.anim_progress += dt

            if drone.anim_progress >= 1.0:
                drone.anim_progress = 1.0
                drone.animating = False

    def reset(self) -> None:
        if self.network.start_hub is None:
            raise ValueError("Network has no start hub")

        drones = [
            Drone(i, self.network.start_hub)
            for i in range(len(self.sim.drones))
        ]

        self.sim.reset(drones)
        self.step_requested = False
        self.auto_play = False

    def run(self) -> None:
        self.sim.init_paths()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.step_requested = True
                    elif event.key == pygame.K_p:
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_a:
                        self.reset()
                    elif event.key == pygame.K_q:
                        running = False

            can_step = self.auto_play or self.step_requested

            if can_step and not any(d.animating for d in self.sim.drones):
                if not all(
                    d.current_hub == self.sim.network.end_hub
                        for d in self.sim.drones):
                    self.sim.turn += 1
                moves = self.sim.resolve_transits()
                moves.extend(self.sim.compute_turn())
                self.sim.apply_moves(moves)
                self.sim.print_turn(moves)
                self.step_requested = False
                self.step_requested = False

            self.sim.update_animation(dt=0.1)
            self.visualizer.draw(self.sim)
            self.visualizer.draw_debug(self)
            pygame.display.flip()
            clock.tick(60)
