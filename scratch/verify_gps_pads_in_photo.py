# Check J_GPS pads orientation on bottom view
# In KiCad Top View (looking at F.Cu with Y pointing down, X pointing right):
# J_GPS footprint:
# Pad 1 is at (-5.08, 0) relative to footprint base (107.41, 109.5).
# So Pad 1 global X = 102.33
# Pad 5 is at (+5.08, 0). Global X = 112.49.
#
# When you flip the board to look at Bottom (B.Cu) with the USB connector at the bottom:
# Global X = 100 is on the LEFT of the photo (near the left edge).
# Global X = 150 is on the RIGHT of the photo (near the right edge).
# Wait! Let's check:
# In media_1790770307774.jpg, which side is X=100 and which side is X=150?
# SHT45 (X=113) is on the LEFT.
# MPU6050 (X=138) is on the RIGHT.
# That means in the photo:
# LEFT is small X (X=100~115).
# RIGHT is large X (X=135~150).
#
# So on J_GPS:
# Pad 1 (X=102.33) is on the LEFT!
# Pad 5 (X=112.49) is on the RIGHT!

print("Pad 1 (3V3): X=102.33 (LEFT in photo)")
print("Pad 2 (GND): X=104.87")
print("Pad 3 (GPS_TX): X=107.41 (CENTER)")
print("Pad 4 (GPS_RX): X=109.95")
print("Pad 5 (NC):   X=112.49 (RIGHT in photo)")
