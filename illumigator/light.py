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



def update(self):
    self.flicker = 10 * math.sin(time.time())

def get_line_raycast_results(ray_x1, ray_y1, ray_x2, ray_y2, line_x1, line_y1, line_x2, line_y2) -> tuple[numpy.ndarray, numpy.ndarray]:  # distances, line indices
    # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
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

    u[(u < 0) | (t < 0) | (t > 1)] = float('inf')  # u
    min_indices = numpy.argmin(u, axis=0)

    return u.T[:, min_indices].diagonal(), min_indices

def get_arc_raycast_results(ray_x1, ray_y1, ray_x2, ray_y2, arc_x, arc_y, arc_r, arc_angle1, arc_angle2) -> tuple[numpy.ndarray, numpy.ndarray]:  # distances, line indices
    # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
    arc_centers = numpy.array((arc_x, arc_y)).T
    ray_origins = numpy.array((ray_x1, ray_y1)).T
    ray_dx_dy = numpy.array(((ray_x2 - ray_x1), (ray_y2 - ray_y1)))
    diff_x = numpy.subtract.outer(ray_x1, arc_x).T
    diff_y = numpy.subtract.outer(ray_y1, arc_y).T
    temp_calculation1 = numpy.multiply(ray_dx_dy[0], diff_x) + numpy.multiply(ray_dx_dy[1], diff_y)
    temp_calculation2 = numpy.linalg.norm(numpy.array([diff_x, diff_y]), axis=0)

    nabla = (temp_calculation1 * temp_calculation1) - (
                numpy.subtract((temp_calculation2 * temp_calculation2).T, arc_r * arc_r).T
            )
    nabla_sqrt = numpy.where(nabla >= 0, numpy.sqrt(nabla), -1)

    intersection_distance1 = numpy.where(
        nabla_sqrt != -1,
        -nabla_sqrt - temp_calculation1,
        -1
    )
    point1_x = numpy.where(
        intersection_distance1 > 0,
        ray_origins.T[0] + ray_dx_dy[0] * intersection_distance1,
        float('inf')
    )
    point1_y = numpy.where(
        intersection_distance1 > 0,
        ray_origins.T[1] + ray_dx_dy[1] * intersection_distance1,
        float('inf')
    )
    point1_angle = numpy.arctan2(
        point1_y,
        point1_x,
        where=(
                (point1_x != float('inf')) & (point1_y != float('inf'))
        )
    ).T
    point1_x = numpy.where(
        ((arc_angle1 < point1_angle) & (point1_angle < arc_angle2)) | (
                (arc_angle2 < arc_angle1) & (
                ((0 <= arc_angle1) & (arc_angle1 <= point1_angle)) |
                ((point1_angle <= arc_angle2) & (arc_angle2 <= 0))
            )
        ),
        point1_x.T,
        float('inf')
    )
    point1_y = numpy.where(
        ((arc_angle1 < point1_angle) & (point1_angle < arc_angle2)) | (
                (arc_angle2 < arc_angle1) & (
                ((0 <= arc_angle1) & (arc_angle1 <= point1_angle)) |
                ((point1_angle <= arc_angle2) & (arc_angle2 <= 0))
            )
        ),
        point1_y.T,
        float('inf')
    )

    intersection_distance2 = numpy.where(
        nabla_sqrt != -1,
        nabla_sqrt - temp_calculation1,
        -1
    )
    point2_x = numpy.where(
        intersection_distance2 > 0,
        ray_origins.T[0] + ray_dx_dy[0] * intersection_distance2,
        float('inf')
    )
    point2_y = numpy.where(
        intersection_distance2 > 0,
        ray_origins.T[1] + ray_dx_dy[1] * intersection_distance2,
        float('inf')
    )
    point2_angle = numpy.arctan2(
        point2_y,
        point2_x,
        where=(
                (point2_x != float('inf')) & (point2_y != float('inf'))
        )
    ).T
    point2_x = numpy.where(
        ((arc_angle2 < point2_angle) & (point2_angle < arc_angle2)) | (
                (arc_angle2 < arc_angle1) & (
                ((0 <= arc_angle1) & (arc_angle1 <= point2_angle)) |
                ((point2_angle <= arc_angle2) & (arc_angle2 <= 0))
            )
        ),
        point2_x.T,
        float('inf')
    )
    point2_y = numpy.where(
        ((arc_angle1 < point2_angle) & (point2_angle < arc_angle2)) | (
                (arc_angle2 < arc_angle1) & (
                ((0 <= arc_angle1) & (arc_angle1 <= point2_angle)) |
                ((point2_angle <= arc_angle2) & (arc_angle2 <= 0))
            )
        ),
        point2_y.T,
        float('inf')
    )



    print("===================================\nNEW WAY:\ntemp1")
    # print(temp_calculation1)
    # print("temp2")
    # print(temp_calculation2)
    # print("nabla")
    # print(nabla)
    print("nabla_sqrt")
    print(nabla_sqrt)
    print("intersect1")
    print(intersection_distance1)
    print("point1 x, y")
    print(point1_x)
    print(point1_y)
    print("point2 x, y")
    print(point2_x)
    print(point2_y)

    # print("intersect2")
    # print(intersection_distance2)


    # min_indices = numpy.argmin(u, axis=0)

    return
    return u.T[:, min_indices].diagonal(), min_indices



