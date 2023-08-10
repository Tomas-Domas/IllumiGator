import arcade
import numpy

from illumigator import geometry

class LightRay:
    def __init__(self, origin, direction, generation=0):
        self.origin = origin
        self.direction = direction
        self._end = numpy.zeros(2)
        self.child_ray: LightRay | None = None
        self.generation = generation

    def generate_child_ray(self, direction):
        if self.child_ray is None:
            self.child_ray = LightRay(
                self._end + direction * 0.001,
                direction,
                generation=self.generation + 1,
            )
        else:
            self.child_ray.origin = self._end + direction * 0.001
            self.child_ray.direction = direction

    def draw(self, alpha):
        color = (255, 255, 255, alpha)
        arcade.draw_line(*self.origin, *self._end, color=color, line_width=6)
        arcade.draw_line(*self.origin, *self._end, color=color, line_width=4)
        arcade.draw_line(*self.origin, *self._end, color=color, line_width=3)
        if self.child_ray is not None:
            self.child_ray.draw(alpha)

    def get_reflected_direction(self, line):
        return self.direction - (2 * line._normal * (line._normal @ self.direction))


def calculate_intersections(ray_origin, ray_dir, line_p1, line_p2) -> tuple[numpy.ndarray, numpy.ndarray]:  # distances, line indices
    # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
    # Given Line = [x1  y1] + t[x2-x1  y2-y1] and Ray = [x3  y3] + t[x4-x3  y4-y3] as parametric equations,
    # there is an intersection if u >= 0 and 0 <= t <= 1, where
    # denom = (x1-x2)(y3-y4) - (y1-y2)(x3-x4)
    # t = ((x1-x3)(y3-y4) - (y1-y3)(x3-x4)) / denom
    # u = ((x1-x3)(y1-y2) - (y1-y3)(x1-x2)) / denom

    ray_dx_dy = -ray_dir.T
    line_dx_dy = numpy.array((line_p1[:, 0] - line_p2[:, 0], line_p1[:, 1] - line_p2[:, 1]))

    lineX_minus_rayX = numpy.subtract.outer(line_p1[:, 0], ray_origin[:, 0])
    lineY_minus_rayY = numpy.subtract.outer(line_p1[:, 1], ray_origin[:, 1])

    denominator = numpy.multiply.outer(line_dx_dy[0], ray_dx_dy[1]) - numpy.multiply.outer(line_dx_dy[1], ray_dx_dy[0])
    t = numpy.where(
        denominator != 0,  # Guard against div by 0
        (lineX_minus_rayX * ray_dx_dy[1] - lineY_minus_rayY * ray_dx_dy[0]) / denominator,
        float('inf')
    )
    u = numpy.where(
        (t < 0) | (t > 1),  # Only bother calculating u if t passess checks
        float('inf'),
        (lineX_minus_rayX.T * line_dx_dy[1] - lineY_minus_rayY.T * line_dx_dy[0]).T / denominator
    )

    # Since ray_dir is normalized, the value of u represents the distance to intersection
    u[u < 0] = float('inf')

    return numpy.min(u, axis=0), numpy.argmin(u, axis=0)
