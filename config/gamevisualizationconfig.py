from pygame import Rect

class GameVisualizationConfig:
    # vizPos für 3 columns
    vizRects3 = [
       [ Rect(84,  72, 32, 32),                                                 Rect(372,  72, 32, 32), Rect(552,  72, 32, 32)                        ],
       [                        Rect(138, 108, 32, 32), Rect(318, 108, 32, 32),                                                 Rect(606, 108, 32, 32)],
       [ Rect(84, 144, 32, 32),                                                 Rect(372, 144, 32, 32), Rect(552, 144, 32, 32)                        ],

       [                        Rect(138, 288, 32, 32),                         Rect(372, 288, 32, 32),                         Rect(606, 288, 32, 32)],
       [ Rect(84, 324, 32, 32),                         Rect(318, 324, 32, 32),                         Rect(552, 324, 32, 32)                        ],
       [                        Rect(138, 360, 32, 32),                         Rect(372, 360, 32, 32),                         Rect(606, 360, 32, 32)]
    ]

    # vizPos für 6 columns
    vizRects6 = [
       [ Rect(84,  72, 32, 32), Rect(138,  72, 32, 32), Rect(318,  72, 32, 32), Rect(372,  72, 32, 32), Rect(552,  72, 32, 32), Rect(606,  72, 32, 32)],
       [ Rect(84, 108, 32, 32), Rect(138, 108, 32, 32), Rect(318, 108, 32, 32), Rect(372, 108, 32, 32), Rect(552, 108, 32, 32), Rect(606, 108, 32, 32)],
       [ Rect(84, 144, 32, 32), Rect(138, 144, 32, 32), Rect(318, 144, 32, 32), Rect(372, 144, 32, 32), Rect(552, 144, 32, 32), Rect(606, 144, 32, 32)],

       [ Rect(84, 288, 32, 32), Rect(138, 288, 32, 32), Rect(318, 288, 32, 32), Rect(372, 288, 32, 32), Rect(552, 288, 32, 32), Rect(606, 288, 32, 32)],
       [ Rect(84, 324, 32, 32), Rect(138, 324, 32, 32), Rect(318, 324, 32, 32), Rect(372, 324, 32, 32), Rect(552, 324, 32, 32), Rect(606, 324, 32, 32)],
       [ Rect(84, 360, 32, 32), Rect(138, 360, 32, 32), Rect(318, 360, 32, 32), Rect(372, 360, 32, 32), Rect(552, 360, 32, 32), Rect(606, 360, 32, 32)]
    ]

    vizGoatRects = [ Rect(84, 540, 64, 64), Rect(110, 540, 64, 64), Rect(318, 540, 64, 64), Rect(344, 540, 64, 64), Rect(552, 540, 64, 64), Rect(578, 540, 64, 64)]

    vizRects = None # initialized in setup/reset
