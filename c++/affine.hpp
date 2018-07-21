#pragma once

namespace affine {
    class A2 {
    private:
        const double _m;
        const double _a;
    public:
        constexpr A2(): _m(1), _a(0) {}
        constexpr A2(double m, double a): _m(m), _a(a) {}
        constexpr double operator() (double x) const { return x*_m+_a; }
        constexpr A2 operator() (A2 x) const { return A2(x._m*_m, x._a*_m+_a); }
        constexpr A2 operator+ (double a) const { return A2(_m, _a+a); }
        constexpr A2 operator- (double s) const { return A2(_m, _a-s); }
        constexpr A2 operator- () const { return A2(-_m, -_a); }
        constexpr A2 operator* (double m) const { return A2(_m*m, _a*m); }
        constexpr A2 operator/ (double d) const { return A2(_m/d, _a/d); }
        constexpr A2 operator~ () const { return A2(1/_m, -_a/_m); }
        constexpr A2 rsub (const double x) const { return A2(-_m, x-_a); }
    };

    constexpr A2 operator+ (const double x, const A2 y) { return y+x; }
    constexpr A2 operator* (const double x, const A2 y) { return y*x; }
    constexpr A2 operator- (const double x, const A2 y) { return y.rsub(x); }

    constexpr A2 mix(const double x0, const double x1, const double y0, const double y1) {
        return A2(y1-y0, y0)(~A2(x1-x0, x0));
    }
}
