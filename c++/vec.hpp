#pragma once

namespace vec {
    struct V2 {
        union { double x; double w; };
        union { double y; double h; };
    };

    struct V3 {
        union { double x; double r; };
        union { double y; double g; };
        union { double z; double b; };
    };

    struct V4 {
        union { double x; double r; };
        union { double y; double g; };
        union { double z; double b; };
        union { double w; double a; };
    };
}
