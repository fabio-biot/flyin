import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from types import SimpleNamespace

import visualizer


def test_draw_drone_handles_missing_current_hub(monkeypatch):
    camera = visualizer.Camera(scale=1, offset_x=0, offset_y=0)
    viz = visualizer.Visualizer(SimpleNamespace(connections=[]), camera)

    drone = SimpleNamespace(
        in_transit=False,
        current_hub=None,
        animating=False,
        anim_from=None,
        anim_to=None,
        target_hub=None,
        current_connection=None,
    )

    monkeypatch.setattr(visualizer, "screen", object())
    monkeypatch.setattr(visualizer.pygame.draw, "circle", lambda *args, **kwargs: None)

    viz.draw_drone(drone)


def test_color_to_rgb_uses_map_color_names():
    camera = visualizer.Camera(scale=1, offset_x=0, offset_y=0)
    viz = visualizer.Visualizer(SimpleNamespace(connections=[]), camera)

    assert viz.color_to_rgb("green") == (0, 255, 0)
    assert viz.color_to_rgb("red") == (255, 0, 0)
    assert viz.color_to_rgb("unknown", default=(1, 2, 3)) == (1, 2, 3)
