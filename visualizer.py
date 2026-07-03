import pygame
from models import Drone
from models import Hub

pygame.init()

WIDTH, HEIGHT = 2000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Simulation")
clock = pygame.time.Clock()


class Camera:
    def __init__(self, scale=100, offset_x=200, offset_y=200):
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y

    def world_to_screen(self, x, y):
        return (
            int(x * self.scale + self.offset_x),
            int(y * self.scale + self.offset_y),
        )


class Visualizer:
    def __init__(self, network, camera):
        self.network = network
        self.camera = camera
        self.font = pygame.font.SysFont("Arial", 20)

    def draw_hub(self, hub: Hub):
        x, y = self.camera.world_to_screen(hub.x, hub.y)
        pygame.draw.circle(screen, hub.get_rvb_color(), (x, y), 15)

    def draw_connections(self):
        for c in self.network.connections:
            x1, y1 = self.camera.world_to_screen(c.hub1.x, c.hub1.y)
            x2, y2 = self.camera.world_to_screen(c.hub2.x, c.hub2.y)
            pygame.draw.line(screen, (180, 180, 180), (x1, y1), (x2, y2), 2)

    def draw_drone(self, drone):

        if drone.in_transit:
            h1 = drone.current_connection.hub1
            h2 = drone.current_connection.hub2

            t = getattr(drone, "progress", 0)

            x = h1.x + (h2.x - h1.x) * t
            y = h1.y + (h2.y - h1.y) * t
        else:
            x = drone.current_hub.x
            y = drone.current_hub.y

        if drone.animating:
            h1 = drone.anim_from
            h2 = drone.anim_to

            t = drone.anim_progress

            x = h1.x + (h2.x - h1.x) * t
            y = h1.y + (h2.y - h1.y) * t
        else:
            x = drone.current_hub.x
            y = drone.current_hub.y

        sx, sy = self.camera.world_to_screen(x, y)
        pygame.draw.circle(screen, (0, 0, 255), (sx, sy), 8)

    def draw_debug(self, game):
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

    def draw(self, sim):
        screen.fill((20, 20, 20))

        self.draw_connections()

        for hub in self.network.hubs.values():
            self.draw_hub(hub)

        for drone in sim.drones:
            self.draw_drone(drone)


class Game:
    def __init__(self, network, sim):
        self.network = network
        self.sim = sim
        self.camera = Camera()
        self.visualizer = Visualizer(network, self.camera)
        self.auto_play = False
        self.step_requested = False

    # def step_back(self):
    #     if self.history:
    #         self.sim = self.history.pop()
    #         self.turn -= 1

    def update_animation(self, dt=0.1):
        for drone in self.sim.drones:
            if not getattr(drone, "animating", False):
                continue

            drone.anim_progress += dt

            if drone.anim_progress >= 1.0:
                drone.anim_progress = 1.0
                drone.animating = False
    
    def reset(self):

        drones = [
            Drone(i, self.network.start_hub)
            for i in range(len(self.sim.drones))
        ]

        self.sim.reset(drones)
        self.turn = 0
        self.step_requested = False
        self.auto_play = False
        
    def run(self):
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
                if not all(d.current_hub == self.sim.network.end_hub for d in self.sim.drones):
                    self.sim.turn += 1
                self.sim.resolve_transits()
                moves = self.sim.compute_turn()
                self.sim.apply_moves(moves)
                self.step_requested = False

            self.sim.update_animation(dt=0.1)
            self.visualizer.draw(self.sim)
            self.visualizer.draw_debug(self)
            pygame.display.flip()
            clock.tick(60)