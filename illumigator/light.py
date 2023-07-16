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
    raycast_results = numpy.full((2, len(ray_x1)), float('inf'))
    for line_i in range(len(line_x1)):  # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
        line_i_x1, line_i_y1, line_i_x2, line_i_y2 = line_x1[line_i], line_y1[line_i], line_x2[line_i], line_y2[line_i]

        temp_calc_x = (ray_x1 - ray_x2)
        temp_calc_y = (ray_y1 - ray_y2)
        denominators = (line_i_x1 - line_i_x2)*temp_calc_y - (line_i_y1 - line_i_y2)*temp_calc_x

        t = numpy.where(denominators != 0, ((line_i_x1 - ray_x1)*temp_calc_y - (line_i_y1 - ray_y1)*temp_calc_x) / denominators, float('inf'))
        u = numpy.where(denominators != 0, ((line_i_y1 - line_i_y2)*(line_i_x1 - ray_x1) - (line_i_x1 - line_i_x2)*(line_i_y1 - ray_y1)) / denominators, float('inf'))

        xy_dists = numpy.where(((0 < t) & (t < 1)) & (u > 0), u * [temp_calc_x, temp_calc_y], float('inf'))
        distances_squared = xy_dists[0, :]*xy_dists[0, :] + xy_dists[1, :]*xy_dists[1, :]

        raycast_results = numpy.where(
            [distances_squared < raycast_results[0, :], distances_squared < raycast_results[0, :]],
            [distances_squared, numpy.full((len(ray_x1)), line_i)],
            raycast_results
        )

    raycast_results[0, :] = numpy.sqrt(raycast_results[0, :])
    return raycast_results.T
