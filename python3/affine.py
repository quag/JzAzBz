import typing


class A2(typing.NamedTuple):
    m : float
    a : float

    def __call__(self, x):
        return x*self.m + self.a

    def inverse(self):
        mi = 1/self.m
        return A2(mi, -self.a*mi)

    def hex(self):
        return f'{self.__class__.__name__}(m=float.fromhex({self.m.hex()!r}), a=float.fromhex({self.a.hex()!r}))'

    @classmethod
    def mix(cls, y0, y1):
        return A2(y1-y0, y0)

    @classmethod
    def norm(cls, x0, x1):
        return cls.mix(x0, x1).inverse()

    @classmethod
    def map(cls, x0, x1, y0, y1):
        return cls.mix(y0, y1) @ cls.norm(x0, x1)

    def __matmul__(self, t):
        return A2(t.m*self.m, self.m*t.a + self.a)

    def __rmatmul__(self, t):
        return A2(self.m*t.m, t.m*self.a + t.a)

    def __add__(self, a):
        return A2(self.m, self.a + a)

    def __radd__(self, a):
        return A2(self.m, self.a + a)

    def __sub__(self, s):
        return A2(self.m, self.a - s)

    def __rsub__(self, s):
        return A2(self.m, self.a - s)

    def __mul__(self, m):
        return A2(self.m*m, self.a*m)

    def __rmul__(self, m):
        return A2(self.m*m, self.a*m)

    def __div__(self, d):
        return A2(self.m/d, self.a/d)

    def __rdiv__(self, d):
        return A2(self.m/d, self.a/d)

    def __neg__(self):
        return A2(-self.m, -self.a)

A2eye = A2(1, 0)
