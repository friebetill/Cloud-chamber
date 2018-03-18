import unittest
import util
import numpy as np

class Test_angleBetween(unittest.TestCase):
    def test_degree0(self):
        angle = util.angleBetween(0,0,1,0)
        self.assertTrue(abs(angle - 0) < 0.0000001)

    def test_degree45(self):
        angle = util.angleBetween(0,0,1,1)
        self.assertTrue(abs(angle - 45) < 0.0000001)
        angle = util.angleBetween(0,0,2,2)
        self.assertTrue(abs(angle - 45) < 0.0000001)

    def test_degree90(self):
        angle = util.angleBetween(0,0,0,1)
        self.assertTrue(abs(angle - 90) < 0.0000001)

    def test_degree135(self):
        angle = util.angleBetween(0,0,-1,1)
        self.assertTrue(abs(angle - 135) < 0.0000001)

    def test_degree180(self):
        angle = util.angleBetween(0,0,-1,0)
        self.assertTrue(abs(angle - 180) < 0.0000001)

    def test_degreeMinus45(self):
        angle = util.angleBetween(0,0,1,-1)
        self.assertTrue(abs(angle + 45) < 0.0000001)
        angle = util.angleBetween(0,1,1,0)
        self.assertTrue(abs(angle + 45) < 0.0000001)

    def test_degreeMinus90(self):
        angle = util.angleBetween(0,0,0,-1)
        self.assertTrue(abs(angle + 90) < 0.0000001)

    def test_degreeMinus135(self):
        angle = util.angleBetween(0,0,-1,-1)
        self.assertTrue(abs(angle + 135) < 0.0000001)


class Test_isAlmostSameAngle(unittest.TestCase):
    def test_compare_smaller_with_bigger(self):
        self.assertTrue(util.isAlmostSameAngle(0, 5, 5))
        self.assertFalse(util.isAlmostSameAngle(0, 5, 4))
        self.assertTrue(util.isAlmostSameAngle(-45, -40, 5))
        self.assertFalse(util.isAlmostSameAngle(-45, -39, 5))
        self.assertTrue(util.isAlmostSameAngle(-175, 180, 5))
        self.assertFalse(util.isAlmostSameAngle(-174, 180, 5))

    def test_compare_bigger_with_smaller(self):
        self.assertTrue(util.isAlmostSameAngle(5, 0, 5))
        self.assertFalse(util.isAlmostSameAngle(5, 0, 4))
        self.assertTrue(util.isAlmostSameAngle(-45, -50, 5))
        self.assertFalse(util.isAlmostSameAngle(-45, -51, 5))
        self.assertTrue(util.isAlmostSameAngle(175, -180, 5))
        self.assertFalse(util.isAlmostSameAngle(174, -180, 5))

    def test_compare_180_degrees_rotated_angles(self):
        self.assertTrue(util.isAlmostSameAngle(90, -90, 5))
        self.assertTrue(util.isAlmostSameAngle(-90, 90, 5))
        self.assertTrue(util.isAlmostSameAngle(45, -135, 5))
        self.assertTrue(util.isAlmostSameAngle(135, -45, 5))

class Test_intersect(unittest.TestCase):
    def test_easy(self):
        line1 = [0,0,2,2]
        line2 = [2,0,0,2]
        self.assertTrue(util.intersect(line1, line2))

    def test_almost_same_start(self):
        line1 = [0,0,2,2]
        line2 = [0.1,0,1.9,2]
        self.assertTrue(util.intersect(line1, line2))

    # Should be working but does not yet
    #def test_almost_same_start(self):
    #    line1 = [0,0,2,2]
    #    line2 = [0,0,1.9,2]
    #    self.assertTrue(util.intersect(line1, line2))

class Test_sortForAngle(unittest.TestCase):
    def test_no_line(self):
        lines = []
        self.assertEqual(util.sortByAngle(lines, 5), [])

    def test_single_line(self):
        line = util.Line(0,0,1,1,'Testfile.jpg')
        lines = [line]
        self.assertEqual(util.sortByAngle(lines, 5), [[line]])

    def test_two_line(self):
        line1 = util.Line(0,0,1,1,'Testfile.jpg')
        line2 = util.Line(0,0,0,0,'Testfile.jpg')
        lines = [line1, line2]
        self.assertEqual(util.sortByAngle(lines, 5), [[line1], [line2]])

    def test_three_line(self):
        line1 = util.Line(0,0,1,1,'Testfile.jpg')
        line2 = util.Line(0,0,0,0,'Testfile.jpg')
        line3 = util.Line(0,0,1,1.1,'Testfile.jpg')
        lines = [line1, line2, line3]
        self.assertEqual(util.sortByAngle(lines, 5), [[line1, line3], [line2]])


#class Test_filterLines(unittest.TestCase):
#    def test_two_values(self):
#        lines = [[0,0,2,2],[0.1,0,1.9,2]]
#        self.assertEqual(util.filterLines(lines), [[0,0,2,2]])
#
#        lines = [[0,0,2,2], [0,2,2,0]]
#        self.assertEqual(util.filterLines(lines), [[0,0,2,2], [0,2,2,0]])
#
#        lines = [[0,0,2,2], [1,1,3,3]]
#        self.assertEqual(util.filterLines(lines), [[0,0,2,2], [1,1,3,3]])
#
#    def test_three_values(self):
#        lines = [[0,0,2,2], [1.1,1,1.9,2], [0.1,0,1.9,2]]
#        self.assertEqual(util.filterLines(lines), [[0,0,2,2]])
#
#        lines = [[0,0,2,2], [3,3,5,5], [0.1,0,1.9,2]]
#        self.assertEqual(util.filterLines(lines), [[0,0,2,2], [3,3,5,5]])

if __name__ == '__main__':
    unittest.main()
