import arcade
import numpy



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
    raycast_results = numpy.full((len(ray_x1), 2), float('inf'))
    for line_i in range(len(line_x1)):

        # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
        denominators = (line_x1[line_i] - line_x2[line_i])*(ray_y1 - ray_y2) - (line_y1[line_i] - line_y2[line_i])*(ray_x1 - ray_x2)
        t = numpy.where(denominators != 0, ((line_x1[line_i] - ray_x1) * (ray_y1 - ray_y2) - (line_y1[line_i] - ray_y1) * (ray_x1 - ray_x2)) / denominators, float('inf'))
        u = numpy.where(denominators != 0, -((line_x1[line_i] - line_x2[line_i]) * (line_y1[line_i] - ray_y1) - (line_y1[line_i] - line_y2[line_i]) * (line_x1[line_i] - ray_x1)) / denominators, float('inf'))
        x_and_y_distances = numpy.where(((0 < t) & (t < 1)) & (u > 0), u * numpy.array(((ray_x1 - ray_x2), (ray_y1 - ray_y2))), float('inf'))
        distances = x_and_y_distances[0]*x_and_y_distances[0] + x_and_y_distances[1]*x_and_y_distances[1]
        raycast_results[:, 0] = numpy.where(distances < raycast_results[:, 0], distances, raycast_results[:, 0])
        raycast_results[:, 1] = numpy.where(distances == raycast_results[:, 0], line_i, raycast_results[:, 1])

    raycast_results[:, 0] = numpy.sqrt(raycast_results[:, 0])
    return raycast_results
