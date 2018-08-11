from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StringType
import sys


spark = SparkSession \
    .builder \
    .appName("LinkSocialApp") \
    .getOrCreate()

path = sys.argv[1]

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


mac_ssidDF.write.mode("append").json(path+"mac_ssid")
ssid_macDF.write.mode("append").json(path+"ssid_mac")