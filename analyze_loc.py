import re
'''
Analyze the data to answer: "On average how close is the nearest Dunkin Donuts to a Starbucks location".
'''
def find_starbucks(db):
    result = db.docs.find({"name": {"$regex": re.compile("starbucks", re.IGNORECASE) }})
    return result

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def get_nearest_dunkin(db, obj):
    result = db.docs.aggregate([
        {"$geoNear": { 
          "near": obj["pos"],
          "maxDistance": 22/3963.2,
          "distanceField": "distance",
          "includeLocs": "latlng",
          "spherical": True,
          "limit": 8000,
          "distanceMultiplier": 6371, # convert to kilometers
          "query": {
            "name": {"$exists": 1}
          }
        }},
     {"$match": {"name": {"$regex": re.compile("dunkin", re.IGNORECASE) }} },
     {"$sort": {"distance": 1}},
     {"$limit": 1}
        ])
    return result

if __name__ == '__main__':
    db = get_db('boston2')

    # step through cursor
    cursor = find_starbucks(db)
    collect_distances = []
    for c in cursor:
      print("==== ", c["pos"])
      if "address" in c:
        print("====  ", c["address"]["housenumber"], c["address"]["street"])
      result = get_nearest_dunkin(db, c)
      for od in result:
        print(">>> ", od)
        collect_distances.append(od["distance"]) # add the distance of the closest dunkin donuts to the current starbucks
      print(">>>>>>>>> DONE >>>>>>>")

    avg = sum(collect_distances)/len(collect_distances)
    print(">> average distance of closest dunkin donuts to each starbucks:  {0} kilometers or {1} miles".format(avg, avg*0.621371))

