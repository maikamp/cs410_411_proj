import unittest

from objects.member import Member 

class MemberTest(unittest.TestCase):
    
    def setUp(self):
        self.user = Member() 

    def test_setMemberUsername(self): 

       self.user.setUsername("username")
       self.assertEqual("username", self.user.username)

    def test_getMemberUsername(self): 
        
        u = "username"
        self.user.setUsername("username")
        self.assertEqual(u, self.user.getUsername())

if __name__ == '__main__':
    unittest.main()