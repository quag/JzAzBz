#include "jabz.hpp"
#include "ff.hpp"

#include <iostream>

constexpr bool valid_srgb(const jabz::srgb1& x) {
    return x.r >= 0 && x.r <= 1
        && x.g >= 0 && x.g <= 1
        && x.b >= 0 && x.b <= 1;
}

constexpr bool valid_srgb(const jabz::jzczhz& x) {
    return valid_srgb(jabz::to_srgb(x));
}

vec::V4 jchzToSrgb(vec::V4 p) {
    const auto target = jabz::jchz1{p.x, p.y, p.z};
    auto srgb = jabz::to_srgb(target);
    if (!valid_srgb(srgb)) {
        constexpr auto probes = 8;
        auto high = target.c;
        auto low = 0.0;
        for (int i=0; i < probes; ++i) {
            const auto delta = high - low;
            if (delta < (1.0/2/2/2/2/2/2/2)) {
                break;
            }
            const auto mid = low + delta/2;
            if (valid_srgb(jabz::to_srgb(jabz::jchz1{target.j, mid, target.h}))) {
                low = mid;
            } else {
                high = mid;
            }
        }

        if (low == 0.0) {
            srgb = {target.j, target.j, target.j};
        } else {
            srgb = jabz::to_srgb(jabz::jchz1{target.j, low, target.h});
        }

        /*
        if (!valid_srgb(srgb)) {
            std::cerr << srgb.r << " " << srgb.g << " " << srgb.b << "|" << target.j << " " << low << " " << target.h << "\n";
        }
        */
    }
    return {srgb.r, srgb.g, srgb.b, p.a};
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    ff::mapCinCout(jchzToSrgb);
    return 0;
}
