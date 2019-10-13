import numpy as np
from PIL import Image

width = 1000
height = 1000


class Vector(object):
    def __init__(self, g, e):
        """
        :param g: what the vector is pointing at
        :param e: camera location

        """
        self.g, self.e = g, e  # sets the g and e values  in the object to the values given by the user
        self.d = self.g - self.e  # stores the vector itself


class Sphere(object):
    def __init__(self, o, r, color):
        """
        :param o: center of the circle, stored as a numpy array with an x, y, z
        :param r: radius of the circle
        :param color: color of the sphere, stored as a numpy array with a red, green, and blue value
        """
        self.o, self.r, self.color = o, r, color  # sets the values for the center of the circle, the radius, and the color
        self.rSq = r ** 2  # sets the rSq variable as the value of r squared

    def checkIntersection(self, vector):
        """
        :param vector: the vector that is pointing at the image, of class Vector. The function checks whether or not
        this vector intersects the sphere.
        :return: bool, True if the vector intersects the sphere, False if it does not
        """
        self.a = np.dot(vector.d, vector.d)  # calculates the "a" value of a quadratic equation
        self.b = np.dot(2 * vector.d, vector.e - self.o)  # calculates the "b" value of a quadratic equation
        self.c = np.dot(vector.e - self.o, vector.e - self.o) - self.rSq  # calculates the "c" value of a quadratic equation
        discriminant = self.b ** 2 - 4 * self.a * self.c  # calculates the discriminant using the above a, b, and c values. If the discriminat is positive, the quadratic has a solution and the vector intersects
        if discriminant < 0:
            self.intersect = False
        else:
            self.intersect = True





    def getRGB(self, vector):
        """
        :param vector: the vector that the point of intersection was just checked for.
        :return: sets self.light to the RGB value for the given pixel.
        """
        f = open("light.txt")  # light.txt stores the information on where the light source is, how bright it is, and how many there are.
        lines = f.read()
        lines = lines.split("\n")
        t = (self.b*-1 - np.sqrt(self.b**2 - 4*self.a*self.c))/(self.a*2)  # t is the value the quadratic formula is being used to solve for.
        p = vector.e + vector.d*t  # finds p, a point on the sphere. Used to find the normal vector
        n = Vector(p, self.o)  # finds the normal (a line perpendicular to the vector)
        length = np.linalg.norm(n.d)
        n = n.d / length  # changes n into a unit vector
        light = []  # light will store all the possible RGB values, and max() will pick the highest one.
        for i in range(len(lines)//2):  # "light.txt" has two lines for every light source (one for the location and one for intensity), so this is essentially looping through every light source
            values = lines[i*2].split(",")  # splits the line into an x, a y, and a z value
            l = Vector(np.array([int(values[0]), int(values[1]), int(values[2])]), p)  # creates a vector pointing from the circle to the light source
            length = np.linalg.norm(l.d)
            l = l.d/length  # changes l into a unit vector
            light.append(np.dot(l, n) * float(lines[i*2+1]))  # multiplies the dot product of the normal and the vector pointing at the light source by the intensity (lines[i*2+1]) and appends it to light
        light.append(sum(light))  # in case both light sources hit the point, this will be the highest value
        light.append(0)  # if no light source hits the point
        light = self.color * max(light)  # combining all parts of the lighting equation
        self.light = np.clip(light, 0, 255)  # ensures that the RGB value does not cross 255 (which might happen with the sum of the dot products)


def main():
    f = open("spheres.txt")  # stores the value for the sphere
    file = f.read()
    list = file.split("\n")
    spheres = []  # will hold a list of spheres, of class Sphere
    for i in range(len(list) // 3):  # information for each sphere takes up 3 lines, looping through each sphere
        center = list[i*3].split(",")  # splits up the x, y, and z values for the center of the sphere
        RGB = list[i*3 + 2].split(",")  # splits up the RGB values in R, G, and B values.
        sphere = Sphere(np.array([int(center[0]), int(center[1]), int(center[2])]), int(list[i*3+1]), np.array([int(RGB[0]), int(RGB[1]), int(RGB[2])]))  #creates an object of class Sphere
        spheres.append(sphere)
    spheres.sort(key=lambda item: item.o[2], reverse=True)  # sorts the sphere by z values, to make sure that the correct sphere is "on top" in the image (line from https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects)
    points = np.zeros((height, width, 3), dtype=np.uint8)  # this will store all the pixels values, from which to create an image
    e = np.array([height/2, width/2, 0])  # cameras location, stored as a numpy array
    for sphere in spheres:
        for x in range(height):
            for y in range(width):
                vector = Vector(np.array([x, y, width/2]), e)  # creates a vector pointing to a point(x, y, and constant z) from the camera
                sphere.checkIntersection(vector)
                if sphere.intersect is True:
                    sphere.getRGB(vector)  # only gets RGB value if the sphere and vector intersect
                    points[x, y] = np.array(sphere.light)  # sphere.light holds the value obtained by getRGB
    im = Image.fromarray(points)  # produces an image from the numpy array
    im.show()


if __name__ == "__main__":
    main()
