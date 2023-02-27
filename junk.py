import random
def randombin(n):
    ans = ""
    for i in range(n):
        ans = ans+str(random.randint(0,1))
    return ans
print(randombin(256))