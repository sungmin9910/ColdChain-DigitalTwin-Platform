# Exact coordinates where ALL modules clear M3 holes, female header housings, and Beetle C6:

# 1. SHT45 (Bottom, Top-Left):
#    Module size: 25.5 x 17.8 mm.
#    Let Y in [125.5, 143.3] (Height = 17.8 mm).
#    Since Y_max = 143.3 < 143.75 (M3 pad bottom), it is 100% CLEAR of M3 hole H3 (103.5, 146.5)!
#    Let X in [100.5, 126.0] (Width = 25.5 mm).
#    Header 1x05 horizontal at Y = 127.5 mm, X in [108.0, 118.16] (center X = 113.25 mm).
#    Female socket housing (2.54mm wide): Y in [126.23, 128.77].
#    Clearance to Beetle C6 top edge (Y = 125.0): 126.23 - 125.0 = 1.23 mm!

# 2. GY-521 (Bottom, Top-Right):
#    Module size: 20.70 x 15.65 mm.
#    Let Y in [127.0, 142.65] (Height = 15.65 mm).
#    Since Y_max = 142.65 < 143.75 (M3 pad bottom), it is 100% CLEAR of M3 hole H4 (146.5, 146.5)!
#    Let X in [123.0, 143.7] (Width = 20.70 mm).
#    Since X_max = 143.7 < 143.75 (M3 pad left), it clears H4 in both X and Y!
#    Header 1x08 horizontal at Y = 128.5 mm, X in [124.5, 142.28] (center X = 133.39 mm).
#    Female socket housing (2.54mm wide): Y in [127.23, 129.77].
#    Clearance to Beetle C6 top edge (Y = 125.0): 127.23 - 125.0 = 2.23 mm!

# 3. GPS ATGM336H (Bottom, Right-Wing):
#    Module size: 13.1 x 15.7 mm.
#    Let X in [136.5, 149.6] (Width = 13.1 mm).
#    Let Y in [108.0, 123.7] (Height = 15.7 mm).
#    H2 is at (146.5, 103.5), pad top is at Y = 106.25 mm.
#    Since Y_min = 108.0 > 106.25, it clears H2!
#    Header 1x05 vertical at X = 143.0 mm, Y in [110.0, 120.16].
#    Female socket housing (2.54mm wide): X in [141.73, 144.27].
#    Distance to Beetle C6 right pin (133.89): 141.73 - 133.89 = 7.84 mm!

# 4. BH1750 (Top, Top-Right):
#    Module size: 13.9 x 18.5 mm.
#    Header 1x05 horizontal at Y = 144.5 mm, X in [130.5, 140.66] (center X = 135.58 mm).
#    Body extends down: Y in [127.5, 146.0] (Height = 18.5 mm).
#    X in [128.63, 142.53] (Width = 13.9 mm).
#    Clearance to Beetle C6 top edge (Y = 125.0): 127.5 - 125.0 = 2.5 mm!
#    Clearance to M3 hole H4 (146.5, 146.5): pad left is 143.75 > 142.53 (clearance = 1.22 mm)!

# 5. JST-PH & SW1 (Top, Top-Center):
#    JST-PH: X in [120.0, 126.0], Y in [144.5, 149.0]. Pins at (122.0, 147.0), (124.0, 147.0).
#    SW1: X in [119.5, 126.5], Y in [137.0, 141.0]. Pads at Y=139.0, X in [121.5, 124.5].
