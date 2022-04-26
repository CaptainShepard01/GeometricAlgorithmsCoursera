import numpy as np

# Algorithm LEGALTRIANGULATION(T)
# Input. Some triangulation T of a point set P.
# Output. A legal triangulation of P.
# 1. while T contains an illegal edge pipj
# 2.    do (∗ Flip pipj ∗)
# 3.        Let pipj pk and pi pj pl be the two triangles adjacent to pi pj.
# 4.        Remove pi pj from T, and add pk pl instead.
# 5. return T


n = 0
m = 0
Points = []
Triangles = []
flip_counter = 0


class Point:
    def __init__(self, id: int, x: int, y: int):
        self.id = id
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __lt__(self, other) -> bool:
        return self.x < other.x or (self.x == other.x and self.y < other.y)

    def __gt__(self, other) -> bool:
        return self.x > other.x or (self.x == other.x and self.y > other.y)

    def get_point_info(self):
        return f"{self.id} [pos=\"{self.x},{self.y}!\"]"



class Triangle:
    def __init__(self, point_1: Point, point_2: Point, point_3: Point):
        self.point_1 = point_1
        self.point_2 = point_2
        self.point_3 = point_3

    def get_point_list(self):
        return [self.point_1, self.point_2, self.point_3]

    def change_point(self, from_p: Point, to_p: Point):
        if self.point_1 == from_p:
            self.point_1 = to_p
        elif self.point_2 == from_p:
            self.point_2 = to_p
        else:
            self.point_3 = to_p

    def get_info(self):
        return f"{self.point_1.get_point_info()} -- {self.point_2.get_point_info()}\n{self.point_1.get_point_info()} -- {self.point_3.get_point_info()}\n{self.point_2.get_point_info()} -- {self.point_3.get_point_info()}\n"


def get_graphviz_info():
    graph_string = "graph Triangulation {\n"

    for triangle in Triangles:
        graph_string += triangle.get_info()

    graph_string += "}\n"

    return graph_string


def write_to_file(filename, number_of_edge_flips):
    with open(f"output_files/{filename}.txt", "w") as f:
        f.write(str(number_of_edge_flips))


def write_graph_viz(data):
    with open(f"output_files/graphviz.txt", "w") as f:
        f.write(str(data))


def read_file(filename):
    try:
        with open(f"input_files/{filename}.txt") as my_file:
            arr = list(map(int, my_file.readline().split(" ")))
            n, m = arr[0], arr[1]

            for i in range(n):
                arr = list(map(int, my_file.readline().split(" ")))
                Points.append(Point(arr[0], arr[1], arr[2]))

            for i in range(m):
                arr = list(map(int, my_file.readline().split(" ")))
                Triangles.append(Triangle(Points[arr[0]], Points[arr[1]], Points[arr[2]]))

    except FileNotFoundError as err:
        print('File do not exist')
        raise err
    except IOError as err:
        print('IO error')
        raise err


def sort_counterclockwise(a: Point, b: Point, c: Point) -> (Point, Point, Point):
    matrix = np.array(
        [[a.x, a.y, 1],
         [b.x, b.y, 1],
         [c.x, c.y, 1]])

    a_new = a
    b_new = b
    c_new = c
    
    while np.linalg.det(matrix) <= 0:
        matrix[[1, 2]] = matrix[[2, 1]]
        temp_point = b_new
        b_new = c_new
        c_new = temp_point

    return a_new, b_new, c_new


def is_in_circle(a: Point, b: Point, c: Point, d: Point) -> bool:
    a_n, b_n, c_n = sort_counterclockwise(a, b, c)
    matrix = np.array(
        [[a_n.x - d.x, a_n.y - d.y, (a_n.x - d.x) ** 2 + (a_n.y - d.y) ** 2],
         [b_n.x - d.x, b_n.y - d.y, (b_n.x - d.x) ** 2 + (b_n.y - d.y) ** 2],
         [c_n.x - d.x, c_n.y - d.y, (c_n.x - d.x) ** 2 + (c_n.y - d.y) ** 2]])
    return np.linalg.det(matrix) > 0


def get_opposite_edge(triangle: Triangle, p_r: Point):
    return np.setdiff1d(triangle.get_point_list(), [p_r])


def find_adjacent_triangle(point_1: Point, point_2: Point, p_r: Point) -> (bool, Triangle):
    for tr in Triangles:
        if point_1 in tr.get_point_list() and point_2 in tr.get_point_list() and p_r not in tr.get_point_list():
            return False, tr

    return True, Triangle(Point(0, 0, 0), Point(0, 0, 0), Point(0, 0, 0))


def get_opposite_vertex(triangle: Triangle, point_1: Point, point_2: Point):
    return np.setdiff1d(triangle.get_point_list(), [point_1, point_2])


def flip(triangle: Triangle, adjacent_triangle: Triangle, p_r: Point) -> (Triangle, Triangle):
    global flip_counter
    (p_A, p_B) = get_opposite_edge(triangle, p_r)
    p_C = np.setdiff1d(adjacent_triangle.get_point_list(), [p_A, p_B])[0]

    triangle.change_point(p_B, p_C)
    adjacent_triangle.change_point(p_A, p_r)

    flip_counter += 1

    return triangle, adjacent_triangle


def legalize_edge(triangle: Triangle, p_r: Point):
    opposite_edge = get_opposite_edge(triangle, p_r)
    err, adjacent_triangle = find_adjacent_triangle(opposite_edge[0], opposite_edge[1], p_r)

    if err:
        # print("Error in adjacent_triangle!")
        return

    if is_in_circle(adjacent_triangle.point_1,
                    adjacent_triangle.point_2,
                    adjacent_triangle.point_3,
                    p_r):
        triangle1, triangle2 = flip(triangle, adjacent_triangle, p_r)
        legalize_edge(triangle1, p_r)
        legalize_edge(triangle2, p_r)


if __name__ == "__main__":
    for i in range(1, 6):
        flip_counter = 0
        prev_counter = 0
        # while True:
        #     prev_counter = flip_counter
        #
        #     print(f"Previous flips count: {prev_counter}")
        #     if flip_counter - prev_counter == 0:
        #         break
        read_file(f"inputTriangulation{i}")
        write_graph_viz(get_graphviz_info())
        for triangle in Triangles:
            legalize_edge(triangle, triangle.point_1)
            legalize_edge(triangle, triangle.point_2)
            legalize_edge(triangle, triangle.point_3)
        print(f"Current flips count: {flip_counter}")

        write_to_file(f"flip_count{i}", flip_counter)
        n = 0
        m = 0
        Points = []
        Triangles = []

