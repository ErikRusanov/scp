import random

with open("dom.csv", "a+") as f:
    for i in range(10, 20):
        f.write(",".join(
            [
                str(random.randint(10, 100)),
                str(90 + i),
                "-",
            ]
        ))
        f.write("\n")
