import jabz

import math
import decimal
import typing

from decimal import Decimal
from dataclasses import dataclass

decimal.getcontext().prec = 100


@dataclass(frozen=True)
class Expr:
    precedence = None

    def bracketCode(self, e:'Expr'):
        c = e.code()
        if e.precedence > self.precedence:
            return f'({c})'
        return c

    def opCode(self, sep:str, x:'Expr', y:'Expr'):
        xc = self.bracketCode(x)
        yc = self.bracketCode(y)
        return f'{xc}{sep}{yc}'

    def factorAddMul(self, factors):
        return self, False

    def multiplicands(self):
        yield self

    def addends(self):
        yield self

    def subs(self, s):
        try:
            return s[self], True
        except KeyError:
            return self._subs(s)

@dataclass(frozen=True)
class Var(Expr):
    symbol: str

    precedence = 0

    def code(self):
        return self.symbol

    def expandMulAdd(self):
        return (self, False)

    def evalConst(self):
        return (self, False)

    def _subs(self, s):
        return (self, False)

@dataclass(frozen=True)
class Num(Expr):
    value: Decimal

    precedence = Var.precedence

    def code(self):
        return f'{self.value:0.19g}'

    def expandMulAdd(self):
        return (self, False)

    def evalConst(self):
        return (self, False)

    def _subs(self, s):
        return (self, False)

def num(text):
    return Num(Decimal(text))

zero = num('0')
one = num('1')
negOne = num('-1')

@dataclass(frozen=True)
class Inv(Expr):
    e: Expr

    precedence = Var.precedence + 1

    def code(self):
        return self.opCode('/', one, self.e)

    def evalConst(self):
        e, ec = self.e.evalConst()
        if isinstance(e, Num):
            return Num(one.value/e.value), True
        if ec:
            return Inv(e), True
        return self, False

    def _subs(self, s):
        e, ec = self.e.subs(s)
        if ec:
            return Inv(e), True
        return self, False

    def expandMulAdd(self):
        e, ec = self.e.expandMulAdd()
        if ec:
            return Inv(e), True
        return self, False

@dataclass(frozen=True)
class Neg(Expr):
    e: Expr

    precedence = Inv.precedence

    def code(self):
        return f'-{self.bracketCode(self.e)}'

    def evalConst(self):
        e, ec = self.e.evalConst()
        if isinstance(e, Num):
            return Num(-e.value), True
        if ec:
            return Neg(e), True
        return self, False

    def _subs(self, s):
        e, ec = self.e.subs(s)
        if ec:
            return Neg(e), True
        return self, False

    def expandMulAdd(self):
        e, ec = Mul(negOne, self.e).expandMulAdd()
        if ec:
            return e, True
        return self, False

    def multiplicands(self):
        yield negOne
        yield self.e

@dataclass(frozen=True)
class Mul(Expr):
    x: Expr
    y: Expr

    precedence = Inv.precedence + 1

    @classmethod
    def simplifyZeroOne(cls, x, y):
        if x == zero or y == zero:
            return zero
        if x == one:
            return y
        if y == one:
            return x
        return cls(x, y)

    def code(self):
        return self.opCode('*', self.x, self.y)

    def multiplicands(self):
        yield from self.x.multiplicands()
        yield from self.y.multiplicands()

    def expandMulAdd(self):
        x, xc = self.x.expandMulAdd()
        y, yc = self.y.expandMulAdd()
        changed = xc or yc
        if isinstance(x, Add):
            return Add(expandMulAdd(Mul(x.x, y)), expandMulAdd(Mul(x.y, y))), True
        elif isinstance(y, Add):
            return Add(expandMulAdd(Mul(x, y.x)), expandMulAdd(Mul(x, y.y))), True
        else:
            return (Mul.simplifyZeroOne(x, y) if changed else self, changed)

    def factorAddMul(self, factors):
        x, xc = self.x.factorAddMul(factors)
        y, yc = self.y.factorAddMul(factors)
        if xc or yc:
            return Mul.simplifyZeroOne(x, y), True
        return self, False

    def evalConst(self):
        x, xc = self.x.evalConst()
        y, yc = self.y.evalConst()
        e = one
        n = one
        for m in (*x.multiplicands(), *y.multiplicands()):
            if isinstance(m, Num):
                n = Num(n.value * m.value)
            else:
                e = Mul.simplifyZeroOne(e, m)

        r = Mul.simplifyZeroOne(e, n)
        return r, r != self

    def _subs(self, s):
        x, xc = self.x.subs(s)
        y, yc = self.y.subs(s)
        if xc or yc:
            return Mul(x, y), True
        return self, False


@dataclass(frozen=True)
class Add(Expr):
    x: Expr
    y: Expr

    precedence = Mul.precedence + 1

    @classmethod
    def simplifyZero(cls, x, y):
        if x == zero:
            return y
        if y == zero:
            return x
        return cls(x, y)

    def code(self):
        return self.opCode(' + ', self.x, self.y)

    def addends(self):
        yield from self.x.addends()
        yield from self.y.addends()

    def expandMulAdd(self):
        x, xc = self.x.expandMulAdd()
        y, yc = self.y.expandMulAdd()
        changed = xc or yc
        return (Add.simplifyZero(x, y) if changed else self, changed)

    def factorAddMul(self, factors):
        x, xc = self.x.factorAddMul(factors)
        y, yc = self.y.factorAddMul(factors)

        factorGroups = {}
        for addend in [*x.addends(), *y.addends()]:
            d = {e:i for i, e in enumerate(factors)}
            fm = []
            ms = []
            for multiplicand in addend.multiplicands():
                try:
                    i = d.pop(multiplicand)
                    fm.append(i)
                except KeyError:
                    ms.append(multiplicand)

            fm = tuple(sorted(fm))
            if fm not in factorGroups:
                factorGroups[fm] = []
            factorGroups[fm].append(ms)

        result = adds(muls([*(factors[i] for i in fm), adds(muls(g) for g in group)]) for fm, group in factorGroups.items())
        return result, result != self

    def evalConst(self):
        x, xc = self.x.evalConst()
        y, yc = self.y.evalConst()
        e = zero
        n = zero
        for m in (*x.addends(), *y.addends()):
            if isinstance(m, Num):
                n = Num(n.value + m.value)
            else:
                e = Add.simplifyZero(e, m)

        r = Add.simplifyZero(e, n)
        return r, r != self

    def _subs(self, s):
        x, xc = self.x.subs(s)
        y, yc = self.y.subs(s)
        if xc or yc:
            return Add.simplifyZero(x, y), True
        return self, False


def vars(symbols):
    return [Var(symbol) for symbol in symbols.split()]

def varMatrix(symbol, n, m):
    return [[Var(f'{symbol}{i}{j}') for j in range(1, m+1)] for i in range(1, n+1)]

def dot(xs, ys):
    result = zero
    for x, y in zip(reversed(xs), reversed(ys)):
        m = Mul(x, y)
        if result is zero:
            result = m
        else:
            result = Add(m, result)
    return result

def adds(xs):
    result = zero
    for x in reversed(list(xs)):
        if result is zero:
            result = x
        else:
            result = Add(x, result)
    return result


def muls(xs):
    result = one
    for x in reversed(list(xs)):
        if result is one:
            result = x
        else:
            result = Mul(x, result)
    return result

def expandMulAdd(e:Expr):
    r, changed = e.expandMulAdd()
    return r

def factorAddMul(factors, e:Expr):
    r, changed = e.factorAddMul(factors)
    return r

def vecMatMul(vec, mat):
    return [dot(m, vec) for m in mat]

def vecMatsMul(vec, *mats):
    v = vec
    for mat in mats:
        v = vecMatMul(v, mat)
    return v

def evalConst(e:Expr):
    r, changed = e.evalConst()
    return r

def subs(s:typing.Dict[Expr, Expr], e:Expr):
    r, changed = e.subs(s)
    return r

r, g, b, x, y, z = vars('t3.r t3.g t3.b x y z')
values = {
    Var('x1'): adds([
        Mul(num(float.fromhex('0x1.a64c2f52ea72dp-2')), r),
        Mul(num(float.fromhex('0x1.6e2eb1f1be0c8p-2')), g),
        Mul(num(float.fromhex('0x1.71a9fdd4910cdp-3')), b),
    ]),

    Var('y1'): adds([
        Mul(num(float.fromhex('0x1.b3679fbabb7e3p-3')), r),
        Mul(num(float.fromhex('0x1.6e2eb13cc6544p-1')), g),
        Mul(num(float.fromhex('0x1.27bb34179021ap-4')), b),
    ]),

    Var('z1'): adds([
        Mul(num(float.fromhex('0x1.3c362381906d4p-6')), r),
        Mul(num(float.fromhex('0x1.e83e4d9c14333p-4')), g),
        Mul(num(float.fromhex('0x1.e6a7f1325153ep-1')), b),
    ]),
}
def mkValue(v, e):
    values[v] = subs(values, e)

mkValue(Var('x100'), Mul(Var('x1'), num('100')))
mkValue(Var('y100'), Mul(Var('y1'), num('100')))
mkValue(Var('z100'), Mul(Var('z1'), num('100')))
mkValue(Var('b'), num('1.15'))
mkValue(Var('g'), num('0.66'))
mkValue(Var('x_'), Add(Mul(Var('b'), Var('x100')), Neg(Mul(Add(Var('b'), Neg(one)), Var('z100')))))
mkValue(Var('y_'), Add(Mul(Var('g'), Var('y100')), Neg(Mul(Add(Var('g'), Neg(one)), Var('x100')))))
mkValue(Var('z_'), Var('z100'))
mkValue(Var('l'), dot([num(x) for x in '0.41478972 0.579999 0.0146480'.split()], vars('x_ y_ z_')))
mkValue(Var('m'), dot([num(x) for x in '-0.2015100 1.120649 0.0531008'.split()], vars('x_ y_ z_')))
mkValue(Var('s'), dot([num(x) for x in '-0.0166008 0.264800 0.6684799'.split()], vars('x_ y_ z_')))

mkValue(Var('l__'), Mul(Var('l'), Inv(num('10000'))))
mkValue(Var('m__'), Mul(Var('m'), Inv(num('10000'))))
mkValue(Var('s__'), Mul(Var('s'), Inv(num('10000'))))

mkValue(Var('c1'), Mul(num('3424'), Inv(num(2**12))))
mkValue(Var('c2'), Mul(num('2413'), Inv(num(2**7))))
mkValue(Var('c3'), Mul(num('2392'), Inv(num(2**7))))
mkValue(Var('n'), Mul(num('2610'), Inv(num(2**14))))
mkValue(Var('p'), Mul(Mul(num('1.7'), num('2523')), Inv(num(2**5))))

mkValue(Var('iz'), adds([Mul(num('0.5'), Var('l_')), Mul(num('0.5'), Var('m_'))]))
mkValue(Var('az'), adds([Mul(num('3.524000'), Var('l_')), Mul(num('-4.066708'), Var('m_')), Mul(num('0.542708'), Var('s_'))]))
mkValue(Var('bz'), adds([Mul(num('0.199076'), Var('l_')), Mul(num('1.096799'), Var('m_')), Mul(num('-1.295875'), Var('s_'))]))

mkValue(Var('d'), num('-0.56'))
mkValue(Var('d0'), num('1.6295499532821566e-11'))

exprs = [
    Var('iz'),
    Mul(Var('iz'), num('0.44')),
    Add(Mul(Var('iz'), num('-0.56')), one),
    Var('az'),
    Var('bz'),
]
for expr in exprs:
    print(expr.code(), '=', evalConst(factorAddMul(vars('t3.r t3.g t3.b'), expandMulAdd(subs(values, expr)))).code())


def c_linear(c):
    if c <= 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** 2.4

def srgb255ToJzAzBz_(sr, sg, sb):
    def nonlinear1(c):
        if c <= 10.31475:
            return c*0.0003035269835488375
        else:
            return (c*0.003717126661090977 + 0.052132701421800948) ** 2.4

    def nonlinear2(a):
        b = a**0.1593017578125
        c = b*18.8515625 + 0.8359375
        d = b*18.6875 + 1
        return (c/d)**134.034375

    r = nonlinear1(sr)
    g = nonlinear1(sg)
    b = nonlinear1(sb)
    
    l = nonlinear2(r*0.003585083359727932572 + g*0.005092044060011000719 + b*0.001041169201586239260)
    m = nonlinear2(r*0.002204179837045521148 + g*0.005922988107728221186 + b*0.001595495732321790141)
    s = nonlinear2(r*0.0007936150919572405067 + g*0.002303422557560143382 + b*0.006631801538878254703)

    iz = l*0.5 + m*0.5
    jz = (iz*0.44)/(iz*-0.56 + 1) + -1.6295499532821566e-11

    az = l*3.524 + m*-4.066708 + s*0.542708
    bz = l*0.199076 + m*1.096799 + s*-1.295875

    return jz, az, bz

def srgb255ToJzAzBz(sr, sg, sb):
    r = (sr*0.0003035269835488375) if sr <= 10.31475 else ((sr*0.003717126661090977 + 0.052132701421800948) ** 2.4)
    g = (sg*0.0003035269835488375) if sg <= 10.31475 else ((sg*0.003717126661090977 + 0.052132701421800948) ** 2.4)
    b = (sb*0.0003035269835488375) if sb <= 10.31475 else ((sb*0.003717126661090977 + 0.052132701421800948) ** 2.4)

    l1 = r*0.003585083359727932572 + g*0.005092044060011000719 + b*0.001041169201586239260
    m1 = r*0.002204179837045521148 + g*0.005922988107728221186 + b*0.001595495732321790141
    s1 = r*0.0007936150919572405067 + g*0.002303422557560143382 + b*0.006631801538878254703

    l2 = l1**0.1593017578125
    m2 = m1**0.1593017578125
    s2 = s1**0.1593017578125

    l3 = l2*18.8515625 + 0.8359375
    m3 = m2*18.8515625 + 0.8359375
    s3 = s2*18.8515625 + 0.8359375

    l4 = l2*18.6875 + 1
    m4 = m2*18.6875 + 1
    s4 = s2*18.6875 + 1

    l = (l3/l4)**134.034375
    m = (m3/m4)**134.034375
    s = (s3/s4)**134.034375
    
    jz0 = l*0.5 + m*0.5
    jz1 = jz0*0.44
    jz2 = jz0*-0.56 + 1
    jz3 = jz1/jz2

    jz = jz3 + -1.6295499532821566e-11

    az = l*3.524 + m*-4.066708 + s*0.542708
    bz = l*0.199076 + m*1.096799 + s*-1.295875

    return jz, az, bz

def check(r, g, b):
    c1 = jabz.SRGB255(r, g, b).srgb1().rgb1().xyz1().xyz100().jzazbz()
    jz, az, bz = srgb255ToJzAzBz(r, g, b)
    s1 = f'{c1.jz:+0.13f} {c1.az:+0.13f} {c1.bz:+0.13f}'
    s2 = f'{jz:+0.13f} {az:+0.13f} {bz:+0.13f}'
    if s2 == s1:
        s2 = ''
    print(f'{r:0<2x},{g:0<2x},{b:0<2x} {s1} {s2}')


#check(0, 0, 0)
check(0, 0, 255)
check(0, 255, 0)
check(0, 255, 255)
check(255, 0, 0)
check(255, 0, 255)
check(255, 255, 0)
check(255, 255, 255)
check(1, 2, 3)
