import timeit

def ToH(n: int, src: list[int], dest: list[int], aux: list[int], s=1):
    print(src, dest, aux, f"{n=} {src=} {dest=} {aux=} {s=}")
    if n == 1:
        top = src.pop()
        dest.append(top)
        return src, dest, aux
    src, aux, dest = ToH(n - 1, src, aux, dest, 1)
    src, dest, aux = ToH(1, src, dest, aux, 2)
    aux, dest, src = ToH(n - 1, aux, dest, src, 3)
    return src, dest, aux


number = int(input("Enter size: "))

start = timeit.default_timer()
print(ToH(number, list(range(number)), [], []))
end = timeit.default_timer()
print(f"Execution time: {end - start}")
