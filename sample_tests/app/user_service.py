from .utils import normalize_email

'''User has email and name.
UserService only allows one unique email per user. PK: email
Email must be stripped and lowercased.
Supports create, read, update, delete operations.'''
class UserService:
    def __init__(self):
        self.users = {}  # dictionary of users
        """
        class User:
            def __init__(self, email: str, name: str):
                self.email = email
                self.name = name

        # instantiating a User object (not defined in this code)
        users = {
            "mchen@domain.com" : User("mchen@domain.com", "Molly Chen"),
            "jdoe@domain.com": User("jdoe@domain.com", "John Doe"),
            "jdoe1@domain.com": User("jdoe1@domain.com", "Jane Doe")
        }

        # ** alternatively, using dictionaries to represent users
        users = {
            "test@email.com": {email: "test@gmail.com", name: "Alice"},
            "mchen@domain.com" : {email: "mchen@domain.com", name: "Molly Chen"},
            "jdoe@domain.com": {email: "jdoe@domain.com", name: "John Doe"},
            "jdoe1@domain.com": {email: "jdoe1@domain.com", name: "Jane Doe"}
        }   
        
        # does the key (email) need to be in the nested dict?
        users = {
            "test@email.com": {name: "Alice"},
            "mchen@domain.com" : {name: "Molly Chen"},
            "jdoe@domain.com": {name: "John Doe"},
            "jdoe1@domain.com": {name: "Jane Doe"}
        }
        """

    # create
    def add_user(self, email: str, name: str):
        email_n = normalize_email(email)

        if email_n in self.users:
            raise ValueError("user already exists")

        self.users[email_n] = {"email": email_n, "name": name}
        print("User added: ", self.users[email_n])

        return self.users[email_n]
    
    # update
    def edit_user(self, email: str, name: str):
        email_n = normalize_email(email)
        if email_n not in self.users:
            raise ValueError("user does not exist")

        self.users[email_n]["name"] = name
        print("User updated: ", self.users[email_n])

        return self.users[email_n]

    # read
    def get_user(self, email: str):
        email_n = normalize_email(email)
        print("Get user: ", self.users.get(email_n))
        return self.users.get(email_n)

    # delete
    def delete_user(self, email: str):
        email_n = normalize_email(email)
        deleted = self.users.pop(email_n, None)
        print("Delete user: ", deleted), 
        return deleted