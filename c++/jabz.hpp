#pragma once

#include <cmath>
#include "affine.hpp"

#define ALIGN __attribute__ ((aligned (__BIGGEST_ALIGNMENT__)))

namespace jabz {
    using namespace affine;

    struct jabz1 { double j, a, b; };
    struct jchz1 { double j, c, h; };
    struct srgb1 { double r, g, b; };

    struct jzczhz { double jz, cz, hz; };
    struct jzazbz { double jz, az, bz; };
    struct izazbz { double iz, az, bz; };
    struct lms1 { double l, m, s; };
    struct lms1_ { double l, m, s; };
    struct xyz100_ { double x_, y_, z_; };
    struct xyz100 { double x, y, z; };
    struct rgb1 { double r, g, b; };

    namespace rgb_srgb {
        constexpr auto linear(auto c) {
            if (c <= 0.04045) {
                return c / 12.92;
            } else {
                return pow((~A2(1.055, -0.055))(c), 2.4);
            }
        }

        constexpr auto nonlinear(auto c) {
            if (c <= 0x1.9a5c61c57a062p-9) {
                return c * 12.92;
            } else {
                return A2(1.055, -0.055)(pow(c, 1/2.4));
            }
        }

        constexpr srgb1 forth(const rgb1& rgb) {
            return {
                nonlinear(rgb.r),
                nonlinear(rgb.g),
                nonlinear(rgb.b),
            };
        }

        constexpr rgb1 back(const srgb1& srgb) {
            return {
                linear(srgb.r),
                linear(srgb.g),
                linear(srgb.b)
            };
        }
    };

    namespace jab_rgb {
        constexpr auto b = 1.15;
        constexpr auto g = 0.66;
        constexpr auto d = -0.56;
        constexpr auto d0 = 1.6295499532821566e-11;

        constexpr auto c1 = 3424.0/4096.0;
        constexpr auto c2 = 2413.0/128.0;
        constexpr auto c3 = 2392.0/128.0;
        constexpr auto n = 2610.0/16384.0;
        constexpr auto p = 1.7*2523.0/32.0;

        constexpr double dot(double a0, double a1, double b0, double b1, double c=0) {
            return a0*b0 + a1*b1 + c;
        }

        constexpr double dot(const double a0, const double a1, const double a2, const double b0, const double b1, const double b2) {
            return a0*b0 + a1*b1 + a2*b2;
        }

        template <class T> constexpr T matmul3(double x, double y, double z, double m00, double m01, double m02, double m10, double m11, double m12, double m20, double m21, double m22) {
            return {
                dot(x, y, z, m00, m01, m02),
                dot(x, y, z, m10, m11, m12),
                dot(x, y, z, m20, m21, m22),
            };
        }

        static constexpr jzazbz forth(const rgb1& rgb) {
            xyz100 xyz = matmul3<xyz100>(rgb.r, rgb.g, rgb.b,
                100*0x1.a64c2f52ea72dp-2, 100*0x1.6e2eb1f1be0c8p-2, 100*0x1.71a9fdd4910cdp-3,
                100*0x1.b3679fbabb7e3p-3, 100*0x1.6e2eb13cc6544p-1, 100*0x1.27bb34179021ap-4,
                100*0x1.3c362381906d4p-6, 100*0x1.e83e4d9c14333p-4, 100*0x1.e6a7f1325153ep-1);

            xyz100_ xyz_ = {
                xyz.x*b + xyz.z*(1-b),
                xyz.y*g + xyz.x*(1-g),
                xyz.z,
            };

            lms1 lms = matmul3<lms1>(xyz_.x_, xyz_.y_, xyz_.z_,
                0.41478972, 0.579999, 0.0146480,
                -0.2015100, 1.120649, 0.0531008,
                -0.0166008, 0.264800, 0.6684799);
            
            constexpr auto f = [](auto x) {
                auto y = pow(x/10000, n);
                return pow((c1 + c2*y)/(1 + c3*y), p);
            };

            lms1 lms_ = {
                f(lms.l),
                f(lms.m),
                f(lms.s),
            };

            izazbz iab = matmul3<izazbz>(lms_.l, lms_.m, lms_.s,
                0.5, 0.5, 0,
                3.524000, -4.066708, 0.542708,
                0.199076, 1.096799, -1.295875);

            return {
                ((1 + d)*iab.iz)/(1 + d*iab.iz) - d0,
                iab.az,
                iab.bz,
            };
        }

        static constexpr rgb1 back(const jzazbz& jab) {
            auto iz = (jab.jz + d0) / (1 + d - d*(A2() + d0))(jab.jz);
            
            izazbz iab = {
                iz,
                jab.az,
                jab.bz,
            };
            
            constexpr auto f = [](auto x) {
                if (x < 0.) {
                    return 0.;
                }
                auto y = pow(x, 1/p);
                return 10000*pow((c1 - y)/(c3*A2() - c2)(y), 1/n);
            };

            lms1 lms = {
                f(dot(iab.az, iab.bz, 0x1.1bdcf5ff4b9ffp-3, 0x1.db860b905af44p-5, iab.iz)),
                f(dot(iab.az, iab.bz, -0x1.1bdcf5ff4b9fep-3, -0x1.db860b905af4fp-5, iab.iz)),
                f(dot(iab.az, iab.bz, -0x1.894b7904a2cf8p-4, -0x1.9fb04b6ae56fdp-1, iab.iz)),
            };

            xyz100_ xyz_ = matmul3<xyz100_>(lms.l, lms.m, lms.s,
                0x1.ec9a1a8bce714p+0, -0x1.013a11a9de8acp+0, 0x1.3470b79eb8366p-5,
                0x1.66b96ff1c1292p-2, 0x1.73f557d230e47p-1, -0x1.0bd08963ad7e9p-4,
                -0x1.74aa645ab6306p-4, -0x1.403bd8515285fp-2, 0x1.85d407843f9bep+0);

            auto x = xyz_.z_ * ((b-1)/b) + (xyz_.x_/b);

            xyz100 xyz = {
                x,
                x * ((g-1)/g) + (xyz_.y_/g),
                xyz_.z_,
            };
            
            rgb1 rgb = matmul3<rgb1>(xyz.x, xyz.y, xyz.z,
                0.01*3.2406255, 0.01*-1.537208, 0.01*-0.4986286,
                0.01*-0.9689307, 0.01*1.8757561, 0.01*0.0415175,
                0.01*0.0557101, 0.01*-0.2040211, 0.01*1.0569959);

            return rgb;
        }
    };

    namespace jabz_jzazbz {
        constexpr auto j2jz = A2(0x1.565fa72decba2p-3, 0);
        constexpr auto a2az = A2(0x1.9d724a74e87bep-3, -0x1.7c5e1c16b37efp-4);
        constexpr auto b2bz = A2(0x1.1612754d5608ep-2, -0x1.40259bce72b63p-3);

        constexpr jzazbz forth(const jabz1& jabz) {
            return {
                j2jz(jabz.j),
                a2az(jabz.a),
                b2bz(jabz.b)
            };
        }

        constexpr jabz1 back(const jzazbz& jab) {
            return {
                (~j2jz)(jab.jz),
                (~a2az)(jab.az),
                (~b2bz)(jab.bz),
            };
        }
    };

    namespace jzczhz_jzazbz {
        constexpr jzazbz forth(const jzczhz& zjch) {
            return {
                zjch.jz,
                zjch.cz * std::cos(zjch.hz),
                zjch.cz * std::sin(zjch.hz),
            };
        }

        constexpr jzczhz back(const jzazbz& jab) {
            return {
                jab.jz,
                std::hypot(jab.az, jab.bz),
                atan2(jab.bz, jab.az),
            };
        }
    };

    namespace jchz_jzczhz {
        constexpr auto tau = 0x1.921fb54442d18p+2;
        constexpr auto pi = 0x1.921fb54442d18p+1;

        constexpr auto j2jz = A2(0x1.565fa72decba2p-3, 0);
        constexpr auto c2cz = A2(0x1.465725747b7fep-3, 0);
        constexpr auto h2hz = A2(tau, -pi);

        constexpr jzczhz forth(const jchz1& jch) {
            return {
                j2jz(jch.j),
                c2cz(jch.c),
                h2hz(jch.h)
            };
        }

        constexpr jchz1 back(const jzczhz& zjch) {
            return {
                (~j2jz)(zjch.jz),
                (~c2cz)(zjch.cz),
                (~h2hz)(zjch.hz),
            };
        }
    };

    constexpr double perceptualDiff(const jzczhz& x, const jzczhz& y) {
        const auto a = y.jz - x.jz;
        const auto b = y.cz - x.cz;
        const auto c = sin((y.hz - x.hz)/2);
        return sqrt(a*a + b*b + 4*x.cz*y.cz*c*c);
    }

    constexpr jzazbz to_jzazbz(const jzczhz& zjch) {
        return jzczhz_jzazbz::forth(zjch);
    }

    constexpr jzczhz to_jzczhz(const jzazbz& jab) {
        return jzczhz_jzazbz::back(jab);
    }

    constexpr jzczhz to_jzczhz(const jchz1& jch) {
        return jchz_jzczhz::forth(jch);
    }

    constexpr jchz1 to_jchz(const jzczhz& zjch) {
        return jchz_jzczhz::back(zjch);
    }

    constexpr srgb1 to_srgb(const rgb1& rgb) {
        return rgb_srgb::forth(rgb);
    }

    constexpr rgb1 to_rgb(const srgb1& srgb) {
        return rgb_srgb::back(srgb);
    }

    constexpr jzazbz to_jzazbz(const rgb1& rgb) {
        return jab_rgb::forth(rgb);
    }

    constexpr rgb1 to_rgb(const jzazbz& jab) {
        return jab_rgb::back(jab);
    }

    constexpr jzazbz to_jzazbz(const jabz1& jabz) {
        return jabz_jzazbz::forth(jabz);
    }

    constexpr jabz1 to_jabz(const jzazbz& jab) {
        return jabz_jzazbz::back(jab);
    }

    constexpr jzazbz to_jzazbz(const srgb1& srgb) {
        return to_jzazbz(to_rgb(srgb));
    }

    constexpr srgb1 to_srgb(const jzazbz& jab) {
        return to_srgb(to_rgb(jab));
    }

    constexpr srgb1 to_srgb(const jzczhz& jch) {
        return to_srgb(to_rgb(to_jzazbz(jch)));
    }

    constexpr jabz1 to_jabz(const srgb1& srgb) {
        return to_jabz(to_jzazbz(srgb));
    }

    constexpr srgb1 to_srgb(const jabz1& jabz) {
        return to_srgb(to_jzazbz(jabz));
    }

    constexpr jchz1 to_jchz(const srgb1& srgb) {
        return to_jchz(to_jzczhz(to_jzazbz(srgb)));
    }

    constexpr srgb1 to_srgb(const jchz1& jch) {
        return to_srgb(to_jzazbz(to_jzczhz(jch)));
    }

    constexpr jzczhz to_jzczhz(const srgb1& srgb) {
        return jzczhz_jzazbz::back(to_jzazbz(srgb));
    }

}

#undef ALIGN
