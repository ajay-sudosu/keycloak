class A:
    def __init__(self, domain_name):
        self.domain_name = domain_name
        print(domain_name)


class A1(A):

    def __init__(self):
        super().__init__(domain_name="admin")


class B(A):
    def __init__(self, domain_name):
        super().__init__(domain_name="member")

        self.admin_token_obj = A1()


b = B("member")
