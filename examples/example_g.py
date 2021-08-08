from guess_testing.generators import AnyGenerator

for _ in range(5):
    a = AnyGenerator()
    print(a)
    print(a())
