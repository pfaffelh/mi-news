from pymongo import MongoClient
import os
import datetime

# Create mongodump 
os.system(f"mongodump --db news --archive=news_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}")

# Delete complete database
os.system("mongo news --eval 'db.dropDatabase()'")

# Restore complete database
# Should be executed from mi-vvz/mongo/
os.system(f"mongorestore --archive='news_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}'")  

