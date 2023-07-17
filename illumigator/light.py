import arcade
import numpy

from illumigator import timer



class LightRay:
    def __init__(self, origin, direction, generation=0):
        self._origin = origin
        self._direction = direction
        self._end = numpy.zeros(2)
        self._child_ray: LightRay | None = None
        self._generation = generation

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
        arcade.draw_line(
            self._origin[0],
            self._origin[1],
            self._end[0],
            self._end[1],
            arcade.color.WHITE,
        )
        if self._child_ray is not None:
            self._child_ray.draw()

def get_raycast_results(ray_x1, ray_y1, ray_x2, ray_y2, line_x1, line_y1, line_x2, line_y2) -> numpy.ndarray | None:   # list that contains (nearest_distance_squared, nearest_line_index)
    pre_timer = timer.Timer("precalculations")
    raycast_results = numpy.full((2, len(ray_x1)), float('inf'))
    ray_dx_dy = numpy.array(((ray_x1 - ray_x2), (ray_y1 - ray_y2)))
    line_dx_dy = numpy.array(((line_x1 - line_x2), (line_y1 - line_y2)))
    x_dif = numpy.subtract.outer(line_x1, ray_x1)
    y_dif = numpy.subtract.outer(line_y1, ray_y1)
    # indices = numpy.arange(len(line_x1))
    pre_timer.stop()

    tu_timer = timer.Timer("t and u")
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
    tu_timer.stop()

    dists_timer = timer.Timer("distances")
    distances_squared = numpy.where(
        ((0 < t) & (t < 1)) & (u > 0),
        u,
        float('inf')
    )
    dists_timer.stop()

    lines_timer = timer.Timer("line")
    for line_i in range(len(line_x1)):  # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
        raycast_results = numpy.where(
            distances_squared[line_i] < raycast_results[0, :],
            [distances_squared[line_i], numpy.full((len(ray_x1)), line_i)],
            raycast_results
        )



    lines_timer.stop()
    return raycast_results.T
