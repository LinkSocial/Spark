from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StringType


spark = SparkSession \
    .builder \
    .appName("LinkSocialApp") \
    .getOrCreate()

path = "../"

schema = StructType().add("mac", StringType()).add("ssid", StringType())
schema2 = StructType().add("ssid", StringType()).add("mac", StringType())

jsonDF = spark \
    .read \
    .schema(schema) \
    .json(path+"mac.json")  # Equivalent to format("json").load("/path/to/directory")

mac_ssid = jsonDF.rdd.map(lambda row: Row(row[0], [row[1]])).reduceByKey(lambda x, y: x+y)
mac_ssidDF = spark.createDataFrame(mac_ssid, schema)

ssid_mac = jsonDF.rdd.map(lambda row: Row(row[1], [row[0]])).reduceByKey(lambda x, y: x+y)
ssid_macDF = spark.createDataFrame(ssid_mac, schema2)

jsonDF.printSchema()

mac_ssidDF.show()
ssid_macDF.show()

mac_ssid_file = open(path + "mac_ssid.json", "a")
ssid_mac_file = open(path + "ssid_mac.json", "a")

mac_ssid_file.write(mac_ssidDF.toJSON())
ssid_mac_file.write(ssid_macDF.toJSON())


# 
# mac_ssidDF.write.mode("append").json(path+"mac_ssidDF")
# ssid_macDF.write.mode("append").json(path+"ssid_macDF")