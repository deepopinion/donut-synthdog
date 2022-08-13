import numpy as np

np.random.seed(3141592)
LEN = 10000


def gen_number_string() -> str:
    before_comma = int(abs(np.round(np.random.normal(loc=3, scale=1.5))))
    after_comma = int(abs(np.round(np.random.normal(loc=2, scale=1.5))))
    s = []
    if before_comma == 0:
        s.append('0')
    for _ in range(before_comma):
        s.append(str(np.random.randint(0, 9)))

    if after_comma != 0:
        s.append(np.random.choice(['.', ',']))
    for _ in range(after_comma):
        s.append(str(np.random.randint(0, 9)))

    return ''.join(s)


with open('numbers.txt', mode='w') as f:
    for _ in range(LEN):
        f.write(gen_number_string() + np.random.choice(['', '$', '€'], p=[0.7, 0.15, 0.15]) + ' ')
