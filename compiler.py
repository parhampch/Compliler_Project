# Shahab Hosseini Moghaddam 98105716
# Parham Chavoshian 98100118
from scanner import Scanner

sc = Scanner()
while True:
    token = sc.get_next_token()
    if token == "END": break