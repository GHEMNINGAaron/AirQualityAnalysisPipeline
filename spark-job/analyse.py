
# Importer les bibliothèques nécessaires pour Spark et l'analyse k-means
from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler, StandardScaler, PCA
from pyspark.sql.functions import col, to_timestamp, expr
import matplotlib.pyplot as plt
import pandas as pd
import os

# 📁 Créer le dossier des résultats s'il n'existe pas
output_dir = "/app/results/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
# 🚀 Initialisation Spark
spark = SparkSession.builder.appName("KMeansAnalysis").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# 📥 Lecture des données
df = spark.read.option("multiline", "true").json("hdfs://hadoop-namenode:9000/data/air_quality/air_quality_data.json")
df = df.drop("coordinates", "summary")

# 🕒 Conversion des dates
df = df.withColumn("datetimeFrom", to_timestamp(col("period.datetimeFrom.utc")))
df = df.withColumn("datetimeTo", to_timestamp(col("period.datetimeTo.utc")))
df = df.withColumn("duration_seconds", expr("unix_timestamp(datetimeTo) - unix_timestamp(datetimeFrom)"))

# ✅ Sélection des colonnes utiles
df_selected = df.select(
    col("value"),
    col("parameter.id").alias("parameter_id"),
    col("coverage.percentComplete").alias("percentComplete"),
    col("coverage.percentCoverage").alias("percentCoverage"),
    col("duration_seconds")
)

# 💾 Sauvegarde des données prétraitées
df_selected.write.mode("overwrite").json(os.path.join(output_dir, "data_selected"))

# ⚙️ Vectorisation
assembler = VectorAssembler(
    inputCols=["value", "parameter_id", "percentComplete", "percentCoverage", "duration_seconds"],
    outputCol="features"
)
df_features = assembler.transform(df_selected).select("features")

# 🔍 K-Means Clustering
kmeans = KMeans(k=3, seed=1, featuresCol="features", predictionCol="cluster")
model = kmeans.fit(df_features)
df_clusters = model.transform(df_features)

# # 💾 Sauvegarde des résultats de clustering

# df_clusters.show(truncate=False)

# dataClusters = df_clusters.toPandas()

# # Sauvegarde des résultats de clustering et dataClusters dans un fichier JSON

with open(os.path.join(output_dir, "dataClusters.json"), "w") as f:
    df_clusters.to_json(f, orient="records")

#df_clusters.select("features", "cluster").write.mode("overwrite").json(os.path.join(output_dir, "clusters"))


