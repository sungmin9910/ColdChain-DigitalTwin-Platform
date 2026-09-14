import numpy as np

# Let's define a smooth apple profile using cubic splines or Bezier curves
# r >= 0, z is vertical axis
# Let Z range from 0 to 80 mm.
# Profile points in (r, z):
# Bottom dimple center: (0, 6)
# Bottom rim: (18, 0)
# Lower flank: (36, 18)
# Mid flank (max width): (42.5, 42)
# Upper shoulder: (38, 66)
# Top rim: (26, 78)
# Top stem dimple center: (0, 68)

pts = [
    (0.0, 6.0),
    (6.0, 3.5),
    (12.0, 1.0),
    (18.0, 0.0),
    (24.0, 0.8),
    (30.0, 5.0),
    (36.0, 14.0),
    (40.5, 26.0),
    (43.0, 42.0),
    (42.5, 52.0),
    (40.0, 62.0),
    (34.0, 72.0),
    (26.0, 78.0),
    (18.0, 77.0),
    (10.0, 73.5),
    (4.0, 69.5),
    (0.0, 68.0)
]

print(f"Total control points: {len(pts)}")
