class A:
    def __init__(self, param):
        print(f'helllo {param}')


class B(A):
    def __init__(self):
        super().__init__(param="helaa")


b = B()
