Accounts = {"Admin": "Admin"}

def accountSearch(text):
    for key, value in Accounts.items():
                if value.lower() in text.lower():
                    return True, key
    return False, None