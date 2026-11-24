from pymongo import MongoClient
uri = "mongodb+srv://chatterjeesamya7_db_user:NtWMMwnCkJzZEQWk@bargain-baazaar.kam3aak.mongodb.net/"
client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()

except Exception as e:
    raise Exception(
        "The following error occurred: ", e)