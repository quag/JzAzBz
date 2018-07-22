module jabz =
  let inline srgb (c:float) : float =
    if c <= 0.0031308049535603713 then
      c * 12.92
    else
      let c' = c ** 0.41666666666666666
      c' * 1.055 + -0.055

  let inline lms t =
    if t > 0. then
      let r = t ** 0.007460772656268214
      let s = (0.8359375 - r) / (18.6875*r + -18.8515625)
      s**6.277394636015326
    else
      0.

  /// brightness ―
  ///   0.0  black
  ///   0.5  grey
  ///   1.0  white
  ///
  /// chroma ―
  ///   0.0  no color, use grey
  ///   0.5  for most hues in sRGB, full color most colorful value, only available for a few hues in sRGB
  ///   1.0  for a red and green, the furthest from grey they can get in sRGB. Most hues do not have a chroma=1
  ///
  /// hue ― 
  ///   0.0  teal
  ///   0.2  blue
  ///   0.3  purple
  ///   0.5  magenta
  ///   0.6  red
  ///   0.7  orange
  ///   0.74 yellow
  ///   0.84 green
  let jchz2srgb(brightness:float, chroma:float, hue:float) : (float*float*float) =
    let jz = brightness * +0.16717463120366200 + 1.6295499532821566e-11
    let cz = chroma     * +0.15934590589262138
    let hz = hue        * +6.28318530717958647 + -3.14159265358979323

    let iz = jz / (0.56*jz + 0.44)
    let az = cz * cos hz
    let bz = cz * sin hz

    let l' = iz + az* +0.13860504327153930 + bz* +0.058047316156118830
    let m' = iz + az* -0.13860504327153927 + bz* -0.058047316156118904
    let s' = iz + az* -0.09601924202631895 + bz* -0.811891896056039000

    let l = lms l'
    let m = lms m'
    let s = lms s'

    let lr = l* +0.0592896375540425100e4 + m* -0.052239474257975140e4 + s* +0.003259644233339027e4
    let lg = l* -0.0222329579044572220e4 + m* +0.038215274736946150e4 + s* -0.005703433147128812e4
    let lb = l* +0.0006270913830078808e4 + m* -0.007021906556220012e4 + s* +0.016669756032437408e4

    (srgb lr, srgb lg, srgb lb)

  let clamp e0 e1 x =
    if x < e0 then e0 else if x > e1 then e1 else x

  let hue = 0.84
  let colorFor x =
    let r, g, b = jchz2srgb(x, 1.-x, hue)

    // TODO: desaturate when rgb outside of bounds
    (clamp 0. 1. r), (clamp 0. 1. g), (clamp 0. 1. b)
