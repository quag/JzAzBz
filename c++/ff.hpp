#pragma once

#include <cstdint>
#include "vec.hpp"

namespace ff {
    typedef vec::V4 (*Map)(vec::V4);
    void mapCinCout(Map);
    void speedupStdio();

    typedef uint16_t u16;
    typedef uint32_t u32;

    struct Bounds {
        u32 width;
        u32 height;
    };

    struct RGBAFFFF {
        u16 r;
        u16 g;
        u16 b;
        u16 a;
    };

    namespace w {
        void w16(u16);
        void w32(u32);
        void header(Bounds);
        void rgbaFFFF(RGBAFFFF);
        void rgba1clip(vec::V4);
        void rgba1mask(vec::V4);
    }

    namespace r {
        u16 r16();
        u32 r32();
        Bounds header();
        RGBAFFFF rgbaFFFF();
        vec::V4 rgba1();
    }
}
