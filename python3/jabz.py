import typing
import math
import hashlib

from affine import A2


def jabz(j, a, b, alpha=1):
    r, g, b = Jabz(j, a, b).srgb255()
    return htmlrgb(r, g, b, alpha)


def jchz(j, c, h, alpha=1):
    r, g, b = Jch(j, c, h).srgb255()
    return htmlrgb(r, g, b, alpha)


def jchzHash(j, c, st, alpha=1):
    h = hashlib.shake_128(st.encode()).digest(1)
    return jchz(j, c, h[0]/255, alpha)


def htmlrgb(r, g, b, alpha=1):
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    alpha = max(0, min(1, alpha))
    if alpha != 1:
        return f'rgba({round(r)}, {round(g)}, {round(b)}, {alpha})'
    return f'#{round(r):02x}{round(g):02x}{round(b):02x}'


def chromaValues(ch, st):
    h = hashlib.shake_128(st.encode()).digest(2)
    x = h[0]/255
    sb = h[1]
    signA = 1 if sb & 0x1 else -1
    signB = 1 if sb & 0x2 else -1

    a = ch*signA*x
    b = ch*signB*(1-x)
    return (a, b)


C_SRGB1 = typing.NewType('C_SRGB1', float)
C_SRGB255 = typing.NewType('C_SRGB255', float)
C_RGB1 = typing.NewType('C_RGB1', float)
C_XYZ1 = typing.NewType('C_XYZ1', float)
C_XYZ100 = typing.NewType('C_XYZ100', float)
C_FF16 = typing.NewType('C_FF16', float)

class FF16(typing.NamedTuple):
    r : C_FF16
    g : C_FF16
    b : C_FF16

    def srgb1(self):
        return SRGB1(self.r/0xFFFF, self.g/0xFFFF, self.b/0xFFFF)

def c_linear(c : C_SRGB1) -> C_RGB1:
    if c <= 0.04045:
        return C_RGB1(c / 12.92)
    else:
        return C_RGB1(((c + 0.055) / 1.055) ** 2.4)

def c_srgb(c : C_RGB1) -> C_SRGB1:
    if c <= float.fromhex('0x1.9a5c61c57a062p-9'):
        return C_SRGB1(c * 12.92)
    else:
        return C_SRGB1(1.055 * (c ** (1/2.4)) - 0.055)

class SRGB255(typing.NamedTuple):
    r : C_SRGB255
    g : C_SRGB255
    b : C_SRGB255
    
    def srgb1(self):
        return SRGB1(self.r/255, self.g/255, self.b/255)

    def jzazbz(self):
        return self.srgb1().rgb1().xyz1().xyz100().jzazbz()

    def jzczhz(self):
        return self.srgb1().rgb1().xyz1().xyz100().jzazbz().jzczhz()

    def jch(self):
        return self.srgb1().rgb1().xyz1().xyz100().jzazbz().jzczhz().jch()

    def jabz(self):
        return self.srgb1().rgb1().xyz1().xyz100().jzazbz().jzczhz().jabz()

class SRGB1(typing.NamedTuple):
    r : C_SRGB1
    g : C_SRGB1
    b : C_SRGB1
    
    def srgb255(self):
        return SRGB255(self.r*255, self.g*255, self.b*255)
    
    def rgb1(self):
        return RGB1(c_linear(self.r), c_linear(self.g), c_linear(self.b))

    def ff16(self):
        return FF16(self.r*0xFFFF, self.g*0xFFFF, self.b*0xFFFF)

class RGB1(typing.NamedTuple):
    r : C_RGB1
    g : C_RGB1
    b : C_RGB1
    
    def srgb1(self):
        return SRGB1(c_srgb(self.r), c_srgb(self.g), c_srgb(self.b))
    
    def xyz1(self):
        return XYZ1(
            math.fsum([float.fromhex('0x1.a64c2f52ea72dp-2')*self.r, float.fromhex('0x1.6e2eb1f1be0c8p-2')*self.g, float.fromhex('0x1.71a9fdd4910cdp-3')*self.b]),
            math.fsum([float.fromhex('0x1.b3679fbabb7e3p-3')*self.r, float.fromhex('0x1.6e2eb13cc6544p-1')*self.g, float.fromhex('0x1.27bb34179021ap-4')*self.b]),
            math.fsum([float.fromhex('0x1.3c362381906d4p-6')*self.r, float.fromhex('0x1.e83e4d9c14333p-4')*self.g, float.fromhex('0x1.e6a7f1325153ep-1')*self.b]),
        )
    
class XYZ1(typing.NamedTuple):
    x : C_XYZ1
    y : C_XYZ1
    z : C_XYZ1
    
    def xyz100(self):
        return XYZ100(
            self.x * 100,
            self.y * 100,
            self.z * 100,
        )
    
    def rgb1(self):
        return RGB1(
            math.fsum([3.2406255*self.x, -1.537208*self.y, -0.4986286*self.z]),
            math.fsum([-0.9689307*self.x, 1.8757561*self.y, 0.0415175*self.z]),
            math.fsum([0.0557101*self.x, -0.2040211*self.y, 1.0569959*self.z]),
        )

class XYZ100(typing.NamedTuple):
    x : C_XYZ100
    y : C_XYZ100
    z : C_XYZ100
    
    def xyz1(self):
        return XYZ1(
            self.x / 100,
            self.y / 100,
            self.z / 100,
        )
    
    def jzazbz(self):
        b = 1.15
        g = 0.66
        c1 = 3424/(2**12)
        c2 = 2413/(2**7)
        c3 = 2392/(2**7)
        n = 2610/(2**14)
        p = 1.7*2523/(2**5)
        d = -0.56
        d0 = 1.6295499532821566e-11
        
        def f(x):
            y = (x/10000)**n
            return ((c1 + c2*y)/(1 + c3*y))**p
        
        x_ = b*self.x - (b-1)*self.z
        y_ = g*self.y - (g-1)*self.x
        z_ = self.z
        
        l = math.fsum([0.41478972*x_, 0.579999*y_, 0.0146480*z_])
        m = math.fsum([-0.2015100*x_, 1.120649*y_, 0.0531008*z_])
        s = math.fsum([-0.0166008*x_, 0.264800*y_, 0.6684799*z_])
        
        l_ = f(l)
        m_ = f(m)
        s_ = f(s)
        
        iz = math.fsum([0.5*l_, 0.5*m_])
        az = math.fsum([3.524000*l_, -4.066708*m_, 0.542708*s_])
        bz = math.fsum([0.199076*l_, 1.096799*m_, -1.295875*s_])
        
        jz = ((1 + d)*iz)/(1 + d*iz) - d0
        
        return JzAzBz(jz, az, bz)

JzAzBz_jz_scale = float.fromhex('0x1.7ed54cfa78037p+2')
JzAzBz_az_scale = float.fromhex('0x1.3d05de055e237p+2')
JzAzBz_az_offset = float.fromhex('-0x1.d70940803ec74p-2')
JzAzBz_bz_scale = float.fromhex('0x1.d75c195cc2180p+1')
JzAzBz_bz_offset = float.fromhex('-0x1.26bc2f723fda1p-1')

class JzAzBz(typing.NamedTuple):
    jz : float
    az : float
    bz : float
    
    def diff(self, other):
        c1 = self.chroma()
        c2 = other.chroma()
        h = self.hue() - other.hue()
        H = 2 * math.sqrt(c1*c2) * math.sin(h/2)
        return math.sqrt((self.jz - other.jz)**2 + (c1-c2)**2 + H**2)

    def xyz100(self):
        jz = self.jz
        az = self.az
        bz = self.bz
        
        b = 1.15
        g = 0.66
        c1 = 3424/(2**12)
        c2 = 2413/(2**7)
        c3 = 2392/(2**7)
        n = 2610/(2**14)
        p = 1.7*2523/(2**5)
        d = -0.56
        d0 = 1.6295499532821566e-11
        
        def f(x):
            if x < 0:
                return 0
            y = x**(1/p)
            return 10000*((c1 - y)/(c3*y - c2))**(1/n)
        
        iz = (jz + d0) / (1 + d - d*(jz + d0))

        l_ = math.fsum([iz, float.fromhex('0x1.1bdcf5ff4b9ffp-3')*az, float.fromhex('0x1.db860b905af44p-5')*bz])
        m_ = math.fsum([iz, float.fromhex('-0x1.1bdcf5ff4b9fep-3')*az, float.fromhex('-0x1.db860b905af4fp-5')*bz])
        s_ = math.fsum([iz, float.fromhex('-0x1.894b7904a2cf8p-4')*az, float.fromhex('-0x1.9fb04b6ae56fdp-1')*bz])

        l = f(l_)
        m = f(m_)
        s = f(s_)

        try:
            x_ = math.fsum([float.fromhex('0x1.ec9a1a8bce714p+0')*l, float.fromhex('-0x1.013a11a9de8acp+0')*m, float.fromhex('0x1.3470b79eb8366p-5')*s])
            y_ = math.fsum([float.fromhex('0x1.66b96ff1c1292p-2')*l, float.fromhex('0x1.73f557d230e47p-1')*m, float.fromhex('-0x1.0bd08963ad7e9p-4')*s])
            z_ = math.fsum([float.fromhex('-0x1.74aa645ab6306p-4')*l, float.fromhex('-0x1.403bd8515285fp-2')*m, float.fromhex('0x1.85d407843f9bep+0')*s])
        except TypeError:
            print(s, s_, file=sys.stderr)
            x_ = 0
            y_ = 0
            z_ = 0

        print(f'xyz_: {x_} {y_} {z_}')
        
        z = z_
        x = (x_ + (b-1)*z)/b
        y = (y_ + (g-1)*x)/g
        return XYZ100(x, y, z)

    def jabz(self):
        return Jabz(
            jz2j(self.jz),
            az2a(self.az),
            bz2b(self.bz),
        )

    def jzczhz(self):
        return JzCzhz(self.jz, math.hypot(self.az, self.bz), math.atan2(self.bz, self.az))

class Jabz(typing.NamedTuple):
    j : float
    a : float
    b : float
    
    def jzazbz(self):
        return JzAzBz(
            j2jz(self.j),
            a2az(self.a),
            b2bz(self.b),
        )

    def srgb255(self):
        return self.jzazbz().xyz100().xyz1().rgb1().srgb1().srgb255()

def jabz2srgb(j, a, b):
    return Jabz(j, a, b).srgb255()

def srgb2jabz(r, g, b):
    return SRGB255(r, g, b).jabz()

JzCzHz_jz1 = float.fromhex('0x1.565fa72decba2p-3')
JzCzHz_cz1 = float.fromhex('0x1.465725747b7fep-3')

class JzCzhz(typing.NamedTuple):
    jz : float
    cz : float
    hz : float

    def jzazbz(self):
        return JzAzBz(self.jz, self.cz * math.cos(self.hz), self.cz * math.sin(self.hz))

    def srgb255(self):
        return self.jzazbz().xyz100().xyz1().rgb1().srgb1().srgb255()

    def jch(self):
        return Jch(self.jz/JzCzHz_jz1, self.cz/JzCzHz_cz1, 0.5 + self.hz/math.tau)

class Jch(typing.NamedTuple):
    j : float
    c : float
    h : float

    def jzczhz(self):
        return JzCzhz(self.j*JzCzHz_jz1, self.c*JzCzHz_cz1, (self.h - 0.5)*math.tau)

    def srgb1(self):
        return self.jzczhz().jzazbz().xyz100().xyz1().rgb1().srgb1()

    def srgb255(self):
        return self.jzczhz().jzazbz().xyz100().xyz1().rgb1().srgb1().srgb255()

def srgb2jch(r, g, b):
    return SRGB255(r, g, b).jzczhz()

def jch2srgb(j, c, h):
    return Jch(j, c, h).srgb255()

def findJchBounds():
    import itertools
    import random

    def r():
        return random.getrandbits(8)

    randomColors = (SRGB255(r(), r(), r()) for i in range(10000))
    gridColors = (SRGB255(C_SRGB255(r), C_SRGB255(g), C_SRGB255(b)) for r in range(0, 0x100, 0xF) for g in range(0, 0x100, 0xF) for b in range(0, 0x100, 0xF))
    allColors = (SRGB255(C_SRGB255(r), C_SRGB255(g), C_SRGB255(b)) for r in range(0, 0x100) for g in range(0, 0x100) for b in range(0, 0x100))
    # allColors: (0, 0.167174631203662) (0, 0.15934590589262138) (-3.1415923373619563, 3.1415894419474077)

    colors = itertools.chain(gridColors, randomColors)
    #colors = allColors

    j0 = 10
    j1 = -10
    c0 = 10
    c1 = -10
    h0 = 10
    h1 = -10
    for c in colors:
        x = c.jzczhz()
        j0 = min(j0, x.jz)
        j1 = max(j1, x.jz)
        c0 = min(c0, x.cz)
        c1 = max(c1, x.cz)
        h0 = min(h0, x.hz)
        h1 = max(h1, x.hz)
    print((j0, j1), (c0, c1), (h0, h1))
    print((float(j0).hex(), float(j1).hex()), (float(c0).hex(), float(c1).hex()), (float(h0).hex(), float(h1).hex()))
    # (0, 0.167174631203662) (0, 0.15934590589262138) (-3.1415923373619563, 3.1415894419474077)
    # ('0x0.0p+0', '0x1.565fa72decba2p-3') ('0x0.0p+0', '0x1.465725747b7fep-3') ('-0x1.91cc4935df026p+1', '0x1.91d47089680fbp+1')

def findJabBounds():
    import itertools
    import random

    def r():
        return random.getrandbits(8)

    randomColors = (SRGB255(r(), r(), r()) for i in range(10000))
    gridColors = (SRGB255(C_SRGB255(r), C_SRGB255(g), C_SRGB255(b)) for r in range(0, 0x100, 0xF) for g in range(0, 0x100, 0xF) for b in range(0, 0x100, 0xF))
    allColors = (SRGB255(C_SRGB255(r), C_SRGB255(g), C_SRGB255(b)) for r in range(0, 0x100) for g in range(0, 0x100) for b in range(0, 0x100))

    colors = itertools.chain(gridColors, randomColors)
    #colors = allColors

    jz0 = 10
    jz1 = -10
    az0 = 10
    az1 = -10
    bz0 = 10
    bz1 = -10
    for c in colors:
        x = c.jzazbz()
        jz0 = min(jz0, x.jz)
        jz1 = max(jz1, x.jz)
        az0 = min(az0, x.az)
        az1 = max(az1, x.az)
        bz0 = min(bz0, x.bz)
        bz1 = max(bz1, x.bz)
    print((jz0, jz1), (az0, az1), (bz0, bz1))
    # (0.0, 0.167174631203662) (-0.09286318752421585, 0.10901496121536364) (-0.15632173274783687, 0.11523305474035597)

    from affine import A2
    j = A2.norm(jz0, jz1)
    a = A2.norm(az0, az1)
    b = A2.norm(bz0, bz1)

    print('jz2j =', j.hex())
    print('az2a =', a.hex())
    print('bz2b =', b.hex())

    print('j2jz =', j.inverse().hex())
    print('a2az =', a.inverse().hex())
    print('b2bz =', b.inverse().hex())

jz2j = A2(m=float.fromhex('0x1.7ed54cfa78037p+2'), a=float.fromhex('-0x0.0p+0'))
az2a = A2(m=float.fromhex('0x1.3d05de055e237p+2'), a=float.fromhex('0x1.d70940803ec73p-2'))
bz2b = A2(m=float.fromhex('0x1.d75c195cc2180p+1'), a=float.fromhex('0x1.26bc2f723fda1p-1'))
j2jz = A2(m=float.fromhex('0x1.565fa72decba2p-3'), a=float.fromhex('0x0.0p+0'))
a2az = A2(m=float.fromhex('0x1.9d724a74e87bep-3'), a=float.fromhex('-0x1.7c5e1c16b37efp-4'))
b2bz = A2(m=float.fromhex('0x1.1612754d5608ep-2'), a=float.fromhex('-0x1.40259bce72b63p-3'))

if __name__ == '__main__':
    findJabBounds()
