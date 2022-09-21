import random
import string


# python3中为string.ascii_letters,而python2下则可以使用string.letters和string.ascii_letters
def GenPassword(length):
    chars = string.ascii_letters + string.digits
    password = random.choice(string.ascii_letters) + ''.join([random.choice(chars) for i in range(length)])


if __name__ == "__main__":
    # 生成10个随机密码
    # for i in range(10):
    #     # 密码的长度为15
    #     GenPassword(15)
    GenPassword(15)