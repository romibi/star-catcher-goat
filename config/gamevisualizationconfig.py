from pygame import Rect

class GameVisualizationConfig:
    # vizPos für 3 columns (720p)
    vizRects3B = [
       [ Rect(84,  72, 32, 32),                                                 Rect(372,  72, 32, 32), Rect(552,  72, 32, 32)                        ],
       [                        Rect(138, 108, 32, 32), Rect(318, 108, 32, 32),                                                 Rect(606, 108, 32, 32)],
       [ Rect(84, 144, 32, 32),                                                 Rect(372, 144, 32, 32), Rect(552, 144, 32, 32)                        ],

       [                        Rect(138, 288, 32, 32),                         Rect(372, 288, 32, 32),                         Rect(606, 288, 32, 32)],
       [ Rect(84, 324, 32, 32),                         Rect(318, 324, 32, 32),                         Rect(552, 324, 32, 32)                        ],
       [                        Rect(138, 360, 32, 32),                         Rect(372, 360, 32, 32),                         Rect(606, 360, 32, 32)]
    ]

    # vizPos für 6 columns (720p)
    vizRects6B = [
       [ Rect(84,  72, 32, 32), Rect(138,  72, 32, 32), Rect(318,  72, 32, 32), Rect(372,  72, 32, 32), Rect(552,  72, 32, 32), Rect(606,  72, 32, 32)],
       [ Rect(84, 108, 32, 32), Rect(138, 108, 32, 32), Rect(318, 108, 32, 32), Rect(372, 108, 32, 32), Rect(552, 108, 32, 32), Rect(606, 108, 32, 32)],
       [ Rect(84, 144, 32, 32), Rect(138, 144, 32, 32), Rect(318, 144, 32, 32), Rect(372, 144, 32, 32), Rect(552, 144, 32, 32), Rect(606, 144, 32, 32)],

       [ Rect(84, 288, 32, 32), Rect(138, 288, 32, 32), Rect(318, 288, 32, 32), Rect(372, 288, 32, 32), Rect(552, 288, 32, 32), Rect(606, 288, 32, 32)],
       [ Rect(84, 324, 32, 32), Rect(138, 324, 32, 32), Rect(318, 324, 32, 32), Rect(372, 324, 32, 32), Rect(552, 324, 32, 32), Rect(606, 324, 32, 32)],
       [ Rect(84, 360, 32, 32), Rect(138, 360, 32, 32), Rect(318, 360, 32, 32), Rect(372, 360, 32, 32), Rect(552, 360, 32, 32), Rect(606, 360, 32, 32)]
    ]

    # vizPos für 3 columns (small)
    vizRects3S = [
       [ Rect(1014,  15, 12, 12),                                                   Rect(1134,  15, 12, 12), Rect(1208,  15, 12, 12)                        ],
       [                          Rect(1037,  32, 12, 12), Rect(1111,  32, 12, 12),                                                  Rect(1231,  32, 12, 12)],
       [ Rect(1014,  47, 12, 12),                                                   Rect(1134,  47, 12, 12), Rect(1208,  47, 12, 12)                        ],

       [                          Rect(1037, 111, 12, 12),                          Rect(1134, 111, 12, 12),                         Rect(1231, 111, 12, 12)],
       [ Rect(1014, 128, 12, 12),                          Rect(1111, 128, 12, 12),                          Rect(1208, 128, 12, 12)                        ],
       [                          Rect(1037, 143, 12, 12),                          Rect(1134, 143, 12, 12),                         Rect(1231, 143, 12, 12)]
    ]

    # vizPos für 6 columns (small)
    vizRects6S = [
       [ Rect(1014,  15, 12, 12), Rect(1037,  15, 12, 12), Rect(1111,  15, 12, 12), Rect(1134,  15, 12, 12), Rect(1208,  15, 12, 12), Rect(1231,  15, 12, 12)],
       [ Rect(1014,  32, 12, 12), Rect(1037,  32, 12, 12), Rect(1111,  32, 12, 12), Rect(1134,  32, 12, 12), Rect(1208,  32, 12, 12), Rect(1231,  32, 12, 12)],
       [ Rect(1014,  47, 12, 12), Rect(1037,  47, 12, 12), Rect(1111,  47, 12, 12), Rect(1134,  47, 12, 12), Rect(1208,  47, 12, 12), Rect(1231,  47, 12, 12)],

       [ Rect(1014, 111, 12, 12), Rect(1037, 111, 12, 12), Rect(1111, 111, 12, 12), Rect(1134, 111, 12, 12), Rect(1208, 111, 12, 12), Rect(1231, 111, 12, 12)],
       [ Rect(1014, 128, 12, 12), Rect(1037, 128, 12, 12), Rect(1111, 128, 12, 12), Rect(1134, 128, 12, 12), Rect(1208, 128, 12, 12), Rect(1231, 128, 12, 12)],
       [ Rect(1014, 143, 12, 12), Rect(1037, 143, 12, 12), Rect(1111, 143, 12, 12), Rect(1134, 143, 12, 12), Rect(1208, 143, 12, 12), Rect(1231, 143, 12, 12)]
    ]

    vizGoatRectsB = [ Rect(84, 540, 64, 64), Rect(110, 540, 64, 64), Rect(318, 540, 64, 64), Rect(344, 540, 64, 64), Rect(552, 540, 64, 64), Rect(578, 540, 64, 64)]
    vizGoatRectsS = [ Rect(1014, 240, 28, 28), Rect(1024, 236, 28, 28), Rect(1111, 220, 28, 28), Rect(1121, 216, 28, 28), Rect(1208, 200, 28, 28), Rect(1218, 196, 28, 28)]

    vizRects = None # initialized in setup/reset
    vizGoatRects = None # initialized in setup/reset