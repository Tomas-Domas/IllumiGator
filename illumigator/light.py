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

def get_raycast_results(ray_coordinates: list[float], line_coordinates: list[float]) -> list[tuple[float, int] | None]:   # tuple is (nearest_distance_squared, nearest_line_index)
    raycast_results = [0] * (len(ray_coordinates)//4)
    for ray_i in range(0, len(ray_coordinates), 4):
        nearest_distance_squared = float('inf')
        nearest_line_index = -1

        ray_x1, ray_y1, ray_x2, ray_y2 = ray_coordinates[ray_i: ray_i+4]
        for line_i in range(0, len(line_coordinates), 4):
            line_x1, line_y1, line_x2, line_y2 = line_coordinates[line_i: line_i+4]

            # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
            denominator = (line_x1 - line_x2) * (ray_y1 - ray_y2) - (line_y1 - line_y2) * (ray_x1 - ray_x2)
            if denominator == 0:  # Line and ray are parallel
                current_distance_squared = float('inf')
            else:
                t = ((line_x1 - ray_x1) * (ray_y1 - ray_y2) - (line_y1 - ray_y1) * (ray_x1 - ray_x2)) / denominator
                u = -((line_x1 - line_x2) * (line_y1 - ray_y1) - (line_y1 - line_y2) * (line_x1 - ray_x1)) / denominator

                if 0 < t < 1 and u > 0:
                    x_dist = u * (ray_x1 - ray_x2)
                    y_dist = u * (ray_y1 - ray_y2)
                    current_distance_squared = x_dist * x_dist + y_dist * y_dist
                else:
                    current_distance_squared = float('inf')

            if current_distance_squared < nearest_distance_squared:
                nearest_distance_squared = current_distance_squared
                nearest_line_index = line_i//4
        if nearest_distance_squared == float('inf'):
            raycast_results[ray_i//4] = None
        else:
            raycast_results[ray_i//4] = (nearest_distance_squared, nearest_line_index)

    return raycast_results
