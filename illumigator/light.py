import math
import time

import arcade
import numpy


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

    def draw(self, alpha):
        color = (255, 255, 255, alpha + self._flicker)
        arcade.draw_line(*self._origin, *self._end, color=color, line_width=6)
        arcade.draw_line(*self._origin, *self._end, color=color, line_width=4)
        arcade.draw_line(*self._origin, *self._end, color=color, line_width=3)
        if self._child_ray is not None:
            self._child_ray.draw(alpha)


def get_raycast_results(ray_p1, ray_p2, line_p1, line_p2, line_reflect, line_len) -> tuple[numpy.ndarray, numpy.ndarray]:  # distances, line indices
    # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
    ray_dx_dy = -ray_p2.T
    line_dx_dy = numpy.array(((line_p1[:, 0] - line_p2[:, 0]), (line_p1[:, 1] - line_p2[:, 1])))
    x_dif = numpy.subtract.outer(line_p1[:, 0], ray_p1[:, 0])
    y_dif = numpy.subtract.outer(line_p1[:, 1], ray_p1[:, 1])

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

    u[(u < 0) | (t < 0) | (t > 1)] = float('inf')  # u
    min_indices = numpy.argmin(u, axis=0)

    # def calculate_normal(self):
    #     normal_unscaled = numpy.array(
    #         [-(self._point2[1] - self._point1[1]), self._point2[0] - self._point1[0]]
    #     )
    #     self._normal = normal_unscaled / numpy.linalg.norm(normal_unscaled)
    #
    # def get_reflected_direction(self, ray):
    #     return ray._direction - (2 * self._normal * (self._normal @ ray._direction))


    line_normals = (
        numpy.where(
            line_reflect,
            [line_dx_dy[1], -line_dx_dy[0]],
            numpy.zeros_like(line_dx_dy)
        ) / line_len
    ).T




    print(line_normals)
    print(ray_p2)
    0/0

    return u.T[:, min_indices].diagonal(), min_indices


def update(self):
    self.flicker = 10 * math.sin(time.time())
