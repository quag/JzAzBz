#include <iostream>
#include "ff.hpp"

template <typename t>
constexpr t constrain(t e0, t e1, t x) {
    if (x < e0) {
        return e0;
    } else if (x > e1) {
        return e1;
    } else {
        return x;
    }
}

namespace ff {
    namespace w {
        void w16(u16 x) {
            std::cout.put((x >> 8) & 0xFF);
            std::cout.put(x & 0xFF);
        }

        void w32(u32 x) {
            std::cout.put((x >> 24) & 0xFF);
            std::cout.put((x >> 16) & 0xFF);
            std::cout.put((x >> 8) & 0xFF);
            std::cout.put((x >> 0) & 0xFF);
        }

        void header(Bounds b) {
            std::cout << "farbfeld";
            w32(b.width);
            w32(b.height);
        }

        void rgbaFFFF(RGBAFFFF p) {
            w16(p.r);
            w16(p.g);
            w16(p.b);
            w16(p.a);
        }

        void rgba1clip(vec::V4 p) {
            w16(constrain(0, 0xFFFF, static_cast<int>(0xFFFF*p.r)));
            w16(constrain(0, 0xFFFF, static_cast<int>(0xFFFF*p.g)));
            w16(constrain(0, 0xFFFF, static_cast<int>(0xFFFF*p.b)));
            w16(constrain(0, 0xFFFF, static_cast<int>(0xFFFF*p.a)));
        }

        void rgba1mask(vec::V4 p) {
            int r = 0xFFFF*p.r;
            int g = 0xFFFF*p.g;
            int b = 0xFFFF*p.b;
            int a = 0xFFFF*p.a;

            if (r < 0 || g < 0 || b < 0 || a < 0 || r > 0xFFFF || g > 0xFFFF || b > 0xFFFF || a > 0xFFFF) {
                w16(0xFFFF);
                w16(0xFFFF);
                w16(0xFFFF);
                w16(0x0000);
            } else {
                w16(r);
                w16(g);
                w16(b);
                w16(a);
            }
        }
    }

    namespace r {
        u16 r16() {
            return (
                (std::cin.get() << 8)
                | (std::cin.get() << 0)
            );
        }

        u32 r32() {
            return (
                (std::cin.get() << 24)
                | (std::cin.get() << 16)
                | (std::cin.get() << 8)
                | (std::cin.get() << 0)
            );
        }

        Bounds header() {
            char magic[9];
            std::cin.get(magic, 9);
            if (std::string(magic) != "farbfeld") {
                throw std::runtime_error("Not farbfeld file");
            }
            return Bounds { r32(), r32() };
        }

        RGBAFFFF rgbaFFFF() {
            return { r16(), r16(), r16(), r16() };
        }

        vec::V4 rgba1() {
            return { static_cast<double>(r16())/0xFFFF, static_cast<double>(r16())/0xFFFF, static_cast<double>(r16())/0xFFFF, static_cast<double>(r16())/0xFFFF };
        }
    }

    void speedupStdio() {
        std::cin.tie(0); // Prevent std::cout from being flushed before every read.
        std::ios::sync_with_stdio(false);
        
        // Not sure if these buffers make a difference‥
        const auto bufsize = 0x4000;
        char cinbuf[bufsize];
        char coutbuf[bufsize];
        std::cin.rdbuf()->pubsetbuf(cinbuf, bufsize);
        std::cout.rdbuf()->pubsetbuf(coutbuf, bufsize);
    }

    void mapCinCout(Map map) {
        speedupStdio();

        auto bounds = ff::r::header();
        ff::w::header(bounds);
        int pixels = bounds.width * bounds.height;
        for (int i=0; i < pixels; i++) {
            ff::w::rgba1mask(map(ff::r::rgba1()));
        }
    }
}

