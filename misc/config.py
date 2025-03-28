import socket

# Das ist der LDAP-Server der Universität, der für die Authentifizierung verwendet wird.
server="ldaps://ldap.uni-freiburg.de"
base_dn = "ou=people,dc=uni-freiburg,dc=de"

# Hier ist die MongoDBsocket.gethostname()
if socket.gethostname() == "www2":
    mongo_location = "mongodb://localhost:27017"
else:
    mongo_location = "mongodb://localhost:27017"

# Name der Berechtigung für diese App in der Datenbank
app_name = "news"

# Die log-Datei
log_file = 'mi.log'

# Feste Vortragsreihen, deren Kurzname nicht gelöscht werden soll:
kurznamen = ["Logik", "Kolloquium", "GeoAna", "FDMAI", "DiffGeo", "Stochastik", "AM", "Algebra", "Didaktik", "alle"]

# Falls alltags geändert wird, muss das Datenbank-Schema angepasst werden.
alltags = ["Monitor", "Lehre", "Institut"]
