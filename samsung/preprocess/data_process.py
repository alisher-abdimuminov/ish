import os
import re
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType


class DataProcessor:
	__mapping_id = ["TIMESTAMP", "NE_UNIQUE_ID", "CNUM"]
	__mapping_id_lte_alpt = ["TIMESTAMP", "NE_UNIQUE_ID"]
	__mapping_id_nr_cell = ["TIMESTAMP", "DU_UNIQUE_ID", "CELLIDENTITY"]
	__mapping_id_nr_cell_vonr = [
		"TIMESTAMP",
		"DU_UNIQUE_ID",
		"FR1_FR2_INDICATOR",
		"LS3_LS6_INDICATOR",
	]
	__mapping_id_nr_cell_complex = [
		"TIMESTAMP",
		"DU_UNIQUE_ID",
		"FR1_FR2_INDICATOR",
		"LS3_LS6_INDICATOR",
	]
	__mapping_id_nr_ng_ducell = [
		"TIMESTAMP",
		"DU_UNIQUE_ID",
		"FR1_FR2_INDICATOR",
		"LS3_LS6_INDICATOR",
	]
	__mapping_id_nr_ng = ["TIMESTAMP", "GNB_ID"]
	__mapping_id_nr_site = ["TIMESTAMP", "DU_UNIQUE_ID"]
	__mapping_id_nr_gnb = ["TIMESTAMP", "GNB_ID"]

	def __init__(self, spark, logger, date, tech, data_type, hours, operator, freq):
		self.log = logger
		self.date = date
		self.tech = tech
		self.operator = operator
		self.data_type = data_type
		self.hours = hours
		self.freq = freq

		self.spark = spark

	def _remove_rows_with_duplicated_data(self, df, map_cols):
		from pyspark.sql.window import Window

		window_spec = Window.partitionBy(*map_cols)

		df_with_count = df.withColumn("_row_count", F.count("*").over(window_spec))
		df_cleaned = df_with_count.filter(F.col("_row_count") == 1).drop("_row_count")

		return df_cleaned

	def _remove_rows_with_nans(self, df, cols):
		condition = F.lit(True)
		for col in cols:
			condition = condition & F.col(col).isNotNull() & (~F.isnan(F.col(col)))
		return df.filter(condition)

	def _remove_rows_with_invalid_du_and_band(self, df):
		if self.data_type in ["GNB", "GNB_QCI", "NG"]:
			id_column = "GNB_ID"
		else:
			id_column = "DU_UNIQUE_ID"

		df = df.filter(F.col(id_column).cast("string") != "-")
		df = df.filter(F.col("FR1_FR2_INDICATOR") != "Unknown")
		return df

	def _remove_rows_invalid_numeric_data(self, df, col):
		return df.filter(F.col(col).cast("string").rlike("^[0-9]+$"))

	def data_cleaning(self, input_view_name):
		df = self.spark.table(input_view_name).filter(
			(F.to_date(F.col("timestamp")) <= F.to_date(F.lit(self.date), "yyyyMMdd"))
			& (
				F.to_date(F.col("timestamp"))
				>= F.date_sub(F.to_date(F.lit(self.date), "yyyyMMdd"), 20)
			)
		)

		print("count_df", df.count())

		cols = df.columns

		if self.tech == "NR":
			if self.operator == "VZW":
				if self.data_type in ["GNB", "GNB_QCI", "NG"]:
					exclude = {
						"TIMESTAMP",
						"GNB_ID",
						"DU_AREA-1",
						"SUB_MARKET_NAME",
						"FR1_FR2_INDICATOR",
						"LS3_LS6_INDICATOR",
						"Hour24",
					}
				else:
					exclude = {
						"TIMESTAMP",
						"DU_UNIQUE_ID",
						"DU_AREA-1",
						"SUB_MARKET_NAME",
						"FR1_FR2_INDICATOR",
						"LS3_LS6_INDICATOR",
						"Hour24",
					}
			else:
				exclude = {
					"TIMESTAMP",
					"DU_UNIQUE_ID",
					"DU_AREA-1",
					"DU_AREA-2",
					"Hour24",
				}
		else:
			exclude = {"TIMESTAMP", "NE_UNIQUE_ID", "AREA-1", "AREA-2", "Hour24"}

		target_cols = [c for c in cols if c not in exclude]

		select_exprs = []
		for col in cols:
			if col in target_cols:
				select_exprs.append(F.col(col).cast(DoubleType()).alias(col))
			else:
				select_exprs.append(F.col(col))
		df = df.select(*select_exprs)

		print("df_select:", df.count())

		if self.tech == "NR":
			if self.data_type in ["SITE", "DU"]:
				df = self._remove_rows_with_nans(df, ["`DU_AREA-2`"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_nr_site
				)
				if self.operator == "VZW":
					df = self._remove_rows_with_invalid_du_and_band(df)
					df = df.withColumn(
						"`DU_AREA-2`", F.col("`DU_AREA-2`").cast(IntegerType())
					)

			elif self.data_type in ["GNB", "GNB_QCI"]:
				df = self._remove_rows_with_nans(df, ["`DU_AREA-2`"])
				print("remove_rows:", df.count)
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_nr_gnb
				)
				print("elif_df:", df.count())
				if self.operator == "VZW":
					df = self._remove_rows_with_invalid_du_and_band(df)
					df = df.withColumn(
						"`DU_AREA-2`", F.col("`DU_AREA-2`").cast(IntegerType())
					)
					print("vzw_df:", df.count())

			elif self.data_type == "NG":
				df = self._remove_rows_with_nans(df, ["`DU_AREA-2`"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_nr_ng
				)
				if self.operator == "VZW":
					df = self._remove_rows_with_invalid_du_and_band(df)
					df = df.withColumn(
						"`DU_AREA-2`", F.col("`DU_AREA-2`").cast(IntegerType())
					)

			elif self.data_type == "CELL_VONR":
				df = self._remove_rows_with_nans(df, ["`DU_AREA-2`"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_nr_cell_vonr
				)
				if self.operator == "VZW":
					df = self._remove_rows_with_invalid_du_and_band(df)
					df = df.withColumn(
						"`DU_AREA-2`", F.col("`DU_AREA-2`").cast(IntegerType())
					)

			elif self.data_type == "NG_DUCELL":
				df = self._remove_rows_with_nans(df, ["`DU_AREA-2`"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_nr_ng_ducell
				)
				if self.operator == "VZW":
					df = self._remove_rows_with_invalid_du_and_band(df)
					df = df.withColumn(
						"`DU_AREA-2`", F.col("`DU_AREA-2`").cast(IntegerType())
					)

			elif self.data_type == "CELL_COMPLEX":
				df = self._remove_rows_with_nans(df, ["`DU_AREA-2`"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_nr_cell_complex
				)
				if self.operator == "VZW":
					df = self._remove_rows_with_invalid_du_and_band(df)
					df = df.withColumn(
						"`DU_AREA-2`", F.col("`DU_AREA-2`").cast(IntegerType())
					)
			else:
				df = self._remove_rows_with_nans(df, ["`DU_AREA-2`", "CELLIDENTITY"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_nr_cell
				)
				if self.operator == "VZW":
					df = self._remove_rows_with_invalid_du_and_band(df)
					df = df.withColumn(
						"`DU_AREA-2`", F.col("`DU_AREA-2`").cast(IntegerType())
					)
					df = df.withColumn(
						"CELLIDENTITY", F.col("CELLIDENTITY").cast(IntegerType())
					)
				else:
					df = df.withColumn(
						"CELLIDENTITY", F.col("CELLIDENTITY").cast(IntegerType())
					)
		else:
			if self.data_type == "ALPT":
				df = self._remove_rows_with_nans(df, ["AREA-2"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id_lte_alpt
				)
				if self.operator == "VZW":
					df = df.withColumn("AREA-2", F.col("AREA-2").cast(IntegerType()))
			else:
				df = self._remove_rows_with_nans(df, ["AREA-2", "CNUM"])
				df = self._remove_rows_with_duplicated_data(
					df, DataProcessor.__mapping_id
				)
				if self.operator == "VZW":
					df = df.withColumn("AREA-2", F.col("AREA-2").cast(IntegerType()))
					df = df.withColumn("CNUM", F.col("CNUM").cast(IntegerType()))
				else:
					df = df.withColumn("CNUM", F.col("CNUM").cast(IntegerType()))
		return df

	def __call__(self):
		print("starting data_preprocessor")
		data_type = "USM" if self.data_type == "BAND" else self.data_type

		input_view_name = f"dlt.databricks_ps.{self.tech}_{data_type}_view_fm".lower()

		print("input_view_name", input_view_name)

		df_kpi = self.data_cleaning(input_view_name)
		print("finished data_cleaning")

		base_view_name = f"{self.tech}_{data_type}_view_pre".lower()
		df_kpi.createOrReplaceTempView(base_view_name)

		return df_kpi
