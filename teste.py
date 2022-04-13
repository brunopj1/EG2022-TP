def ola(s : set):
    it = iter(s)
    i1 = next(it)
    s.remove(i1)

#s = { 9999, 1, "abc" }
#it = iter(s)
#i1 = next(it)
#i2 = next(it)
#print(i1)
#print(i2)

s = { 9999, 1, "abc" }
ola(s)
print(s)
