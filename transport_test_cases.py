from transport_optimizer import assign

# -----------------------------------------------------------------
# Test Case 1
# Standard valid allocation example from assignment specification
# -----------------------------------------------------------------

L = 16

roads = [
    (0,1,3), (0,2,5), (0,3,10),
    (1,4,1), (2,5,2), (5,6,3),
    (2,7,4), (0,8,1), (0,9,1),
    (0,10,1), (0,11,1), (6,12,2),
    (6,13,4), (6,14,3), (7,15,1)
]

students = [
    4, 10, 8, 12, 12, 13, 13, 13,
    13, 13, 13, 13, 13, 5, 7, 7,
    7, 7, 7, 15, 15, 7, 4, 8, 9
]

buses = [
    (0, 3, 5),
    (6, 5, 10),
    (15, 5, 10),
    (6, 5, 10)
]

D = 5
T = 22

print("Test Case 1")
print(assign(L, roads, students, buses, D, T))
print()


# -----------------------------------------------------------------
# Test Case 2
# Impossible allocation because exact target T cannot be satisfied
# -----------------------------------------------------------------

L = 16

roads = [
    (0,1,3), (0,2,5), (0,3,10),
    (1,4,1), (2,5,2), (5,6,3),
    (2,7,4), (0,8,1), (0,9,1),
    (0,10,1), (0,11,1), (6,12,2),
    (6,13,4), (6,14,3), (7,15,1)
]

students = [5, 8, 3, 7, 7, 15, 15, 8, 15, 7, 6, 15]

buses = [
    (0, 3, 5),
    (15, 5, 6)
]

D = 5
T = 7

print("Test Case 2")
print(assign(L, roads, students, buses, D, T))
print()


# -----------------------------------------------------------------
# Test Case 3
# Edge case where some students are too far from pickup locations
# -----------------------------------------------------------------

L = 8

roads = [
    (0, 1, 2),
    (1, 2, 2),
    (2, 3, 2),
    (4, 5, 1),
    (5, 6, 1)
]

students = [
    0, 1, 2, 5, 6, 7
]

buses = [
    (1, 2, 3),
    (5, 1, 2)
]

D = 3
T = 4

print("Test Case 3")
print(assign(L, roads, students, buses, D, T))