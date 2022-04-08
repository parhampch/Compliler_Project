#Shahab Hosseini Moghaddam 98015716
from scanner import Scanner

sc = Scanner()
while True:
    token = sc.get_next_token()
    if token == "END": break