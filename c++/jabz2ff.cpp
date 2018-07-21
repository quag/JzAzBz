#include "jabz.hpp"
#include "ff.hpp"

vec::V4 jabzToSrgb(vec::V4 p) {
    auto [r, g, b] = jabz::to_srgb(jabz::jabz1{p.x, p.y, p.z});
    return {r, g, b, p.a};
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    ff::mapCinCout(jabzToSrgb);
    return 0;
}
