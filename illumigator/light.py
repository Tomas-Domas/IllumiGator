import math

import arcade
import numpy

import time


class LightRay:
    def __init__(self, origin, direction, generation=0):
        self._origin = origin
        self._direction = direction
        self._end = numpy.zeros(2)
        self._child_ray: LightRay | None = None
        self._generation = generation
        self._flicker = 20

    def _generate_child_ray(self, direction):
        if self._child_ray is None:
            self._child_ray = LightRay(
                self._end + direction * 0.001,
                direction,
                generation=self._generation + 1,
            )
        else:
            self._child_ray._origin = self._end + direction * 0.001
            self._child_ray._direction = direction

    def draw(self):
        alpha = int(32 + 32 * math.sin(2 * time.time()))
        color = (255, 255, 255, alpha + self._flicker)
        arcade.draw_line(
            self._origin[0],
            self._origin[1],
            self._end[0],
            self._end[1],
            color,
            10
        )
        if self._child_ray is not None:
            self._child_ray.draw()


def get_raycast_results(ray_x1, ray_y1, ray_x2, ray_y2, line_x1, line_y1, line_x2, line_y2) -> \
        tuple[numpy.ndarray, numpy.ndarray]:  # distances, line indices
    # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
    # print("INPUTS")
    # print(ray_x1, ray_y1, ray_x2, ray_y2)
    # print(line_x1, line_y1, line_x2, line_y2)
    ray_dx_dy = numpy.array(((ray_x1 - ray_x2), (ray_y1 - ray_y2)))
    line_dx_dy = numpy.array(((line_x1 - line_x2), (line_y1 - line_y2)))
    x_dif = numpy.subtract.outer(line_x1, ray_x1)
    y_dif = numpy.subtract.outer(line_y1, ray_y1)

    denominators = numpy.multiply.outer(line_dx_dy[0], ray_dx_dy[1]) - numpy.multiply.outer(line_dx_dy[1], ray_dx_dy[0])
    t = numpy.where(
        denominators != 0,
        (x_dif * ray_dx_dy[1] - y_dif * ray_dx_dy[0]) / denominators,
        float('inf')
    )
    u = numpy.where(
        denominators != 0,
        (x_dif.T * line_dx_dy[1] - y_dif.T * line_dx_dy[0]).T / denominators,
        float('inf')
    )

    u[(u <= 0) | (t <= 0) | (t >= 1)] = float('inf')  # u
    min_indices = numpy.argmin(u, axis=0)

    return u.T[:, min_indices].diagonal(), min_indices


def update(self):
    self.flicker = 10 * math.sin(time.time())
