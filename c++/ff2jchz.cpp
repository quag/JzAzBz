#include "jabz.hpp"
#include "ff.hpp"

vec::V4 srgbToJchz(vec::V4 p) {
    auto [r, g, b] = jabz::to_jchz(jabz::srgb1{p.x, p.y, p.z});
    return {r, g, b, p.a};
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    ff::mapCinCout(srgbToJchz);
    return 0;
}
