#!/usr/bin/python3

core_count = 32

item_count = 10000

items_per_core = item_count // core_count

items = [n for n in range(item_count)]


def do_work(x_endpoints: tuple[int, int], y_endpoints: tuple[int, int]):
    for x in items[x_endpoints[0] : x_endpoints[1]]:
        for y in items[y_endpoints[0] : y_endpoints[1]]:
            if x <= y:
                continue

            print(x, y)


squares = [
    ((x_start, x_start + items_per_core - 1), (y_start, y_start + items_per_core - 1))
    for x_start in range(0, item_count, items_per_core)
    for y_start in range(0, item_count, items_per_core)
    if x_start <= y_start
]

print(len(squares), " squares created")

for square in squares:
    do_work(*square)
