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

def get_line_raycast_results(ray_p1, ray_p2, line_p1, line_p2) -> tuple[numpy.ndarray, numpy.ndarray]:  # distances, line indices
    # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
    ray_dx_dy = -ray_p2.T
    line_dx_dy = numpy.array((line_p1[:, 0] - line_p2[:, 0], line_p1[:, 1] - line_p2[:, 1]))
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

    return numpy.min(u, axis=0), numpy.argmin(u, axis=0)

def get_arc_raycast_results(ray_ori_x, ray_ori_y, ray_dir_x, ray_dir_y, arc_x, arc_y, arc_r, arc_angle1, arc_angle2) -> numpy.ndarray:  # distances, line indices
    # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
    temp_calc = (
        (ray_ori_x * (ray_ori_y + ray_dir_y)
         - (ray_ori_x + ray_dir_x) * ray_ori_y)
         - numpy.multiply.outer(arc_x, ray_dir_y)
         + numpy.multiply.outer(arc_y, ray_dir_x)
    )
    nabla = (arc_r * arc_r - temp_calc.T * temp_calc.T).T
    numpy.sqrt(nabla, where=nabla > 0, out=nabla)

    point1_rel_x = (ray_dir_y * temp_calc - ray_dir_x * nabla).T
    point1_rel_y = -(ray_dir_x * temp_calc + ray_dir_y * nabla).T
    point1_dst_x = (point1_rel_x + arc_x).T - ray_ori_x
    point1_dst_y = (point1_rel_y + arc_y).T - ray_ori_y
    point1_rel_angle = numpy.arctan2(point1_rel_y, point1_rel_x)
    intersection_distance1 = numpy.where(
        ((nabla >= 0) & (point1_dst_x * ray_dir_x >= 0) & (point1_dst_y * ray_dir_y >= 0)).T &
        (
            ((arc_angle1 < point1_rel_angle) & (point1_rel_angle < arc_angle2)) | (
                (arc_angle2 < arc_angle1) & (
                    ((0 <= arc_angle1) & (arc_angle1 <= point1_rel_angle)) |
                    ((point1_rel_angle <= arc_angle2) & (arc_angle2 <= 0))
                )
            )
        ),
        numpy.sqrt(point1_dst_x*point1_dst_x + point1_dst_y*point1_dst_y).T,
        float('inf')
    )
    intersection_arc_index1 = numpy.argmin(intersection_distance1, axis=1)
    intersection_distance1 = numpy.min(intersection_distance1, axis=1)

    point2_rel_x = (ray_dir_y*temp_calc + ray_dir_x*nabla).T
    point2_rel_y = (ray_dir_y*nabla - ray_dir_x*temp_calc).T
    point2_dst_x = (point2_rel_x + arc_x).T - ray_ori_x
    point2_dst_y = (point2_rel_y + arc_y).T - ray_ori_y
    point2_rel_angle = numpy.arctan2(point2_rel_y, point2_rel_x)
    intersection_distance2 = numpy.where(
        ((nabla >= 0) & (point2_dst_x * ray_dir_x >= 0) & (point2_dst_y * ray_dir_y >= 0)).T &
        (
            ((arc_angle1 < point2_rel_angle) & (point2_rel_angle < arc_angle2)) | (
                (arc_angle2 < arc_angle1) & (
                    ((0 <= arc_angle1) & (arc_angle1 <= point2_rel_angle)) |
                    ((point2_rel_angle <= arc_angle2) & (arc_angle2 <= 0))
                )
            )
        ),
        numpy.sqrt(point2_dst_x*point2_dst_x + point2_dst_y*point2_dst_y).T,
        float('inf')
    )
    intersection_arc_index2 = numpy.argmin(intersection_distance2, axis=1)
    intersection_distance2 = numpy.min(intersection_distance2, axis=1)

    return numpy.where(
        intersection_distance1 < intersection_distance2,
        [intersection_distance1, intersection_arc_index1],
        [intersection_distance2, intersection_arc_index2]
    )
