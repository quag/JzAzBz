#include <iostream>

#include "affine.hpp"

using namespace affine;

constexpr double sandbox() {
    auto f = A2() / 2;
    auto g = A2() - 1;
    return (~g(f))(4);
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;

    auto x = sandbox();
    std::cout << x;
    return 0;
}
