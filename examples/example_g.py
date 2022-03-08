from guess_testing.generators import AnyGenerator

a = AnyGenerator()
for _ in range(5):
    print(a())

for _ in range(5):
    print(a.generate_generator())
