from datetime import datetime
from pathlib import Path

import pandas as pd


class MADPostProcessor:
	def __init__(
		self,
		date,
		tech,
		mad_result_path,
		ade_report_mail_path,
		param_path,
		data_type,
		**kwargs,
	):
		self.date = date
		self.tech = tech
		self.ade_report_mail_path = Path(ade_report_mail_path)
		self.param_path = Path(param_path)
		if data_type == "PM":
			self.data_type = "USM"
		else:
			self.data_type = data_type
		self.mad_result_path = Path(mad_result_path)
		self.market_region_file = "market_region_table.csv"

	def _set_target_date(self, target_date):
		target_date = str(target_date)
		final_date = (datetime.strptime(target_date, "%Y%m%d")).strftime(
			"%Y/%m/%d %H:%M:%S"
		)
		return final_date

	# def _get_market_region(self):
	# 	df_market_region = pd.read_csv(self.market_region_file, on_bad_lines="skip")
	# 	df_market_region = df_market_region[
	# 		[
	# 			"Market ID",
	# 			"Region",
	# 		]
	# 	]
	# 	dict_market_region = dict(df_market_region.values)
	# 	# obtain dictionary between Market ID to Region
	# 	return dict_market_region

	def _get_market_region(self):
		df = pd.read_csv(self.market_region_file, on_bad_lines="skip")
		df = df[["Market ID", "Region"]].dropna(subset=["Market ID"])
		df["Market ID"] = df["Market ID"].astype(float).astype(int)
		return dict(zip(df["Market ID"], df["Region"]))

	def _set_market_superset(self, df_mad_summary):
		dict_market_region = self._get_market_region()

		list_dict_market = list(dict_market_region.keys())  # extract market IDs
		list_dict_market = list(set(list_dict_market))  # Remove duplicates
		list_dict_market.sort()
		list_dict_market = list(map(str, list_dict_market))  # transform to string

		list_df_market = df_mad_summary.columns.values.tolist()
		# C:
		# .values unnecessary
		# list_dict_market is a list of market strings such as 65, 66, etc.
		# How about list_df_market? same?

		for market in list_dict_market:
			if str(market) not in list_df_market:
				df_mad_summary[str(market)] = ""

		if self.data_type == "BAND":
			df_mad_summary_columns = ["kpi_name"] + ["band"] + list_dict_market
			# Result might be like ['kpi_name', 'band', '23', '66']
		else:
			df_mad_summary_columns = ["kpi_name"] + list_dict_market

		if df_mad_summary.empty:
			df_mad_summary = df_mad_summary.reindex(columns=df_mad_summary_columns)
			# C: This is different from the normal usuage of .reindex which is
			# usually reindex(index=....)
		else:
			df_mad_summary = df_mad_summary[df_mad_summary_columns]
		return df_mad_summary

	def _column_rename(self, df_mad_summary):
		dict_market_region = self._get_market_region()

		list_market = df_mad_summary.columns.values.tolist()
		list_market.remove("kpi_name")

		if self.data_type == "BAND":
			list_market.remove("band")

		for market in list_market:
			region = dict_market_region[int(market)]
			df_mad_summary.rename(
				columns={str(market): region + "_" + str(market)}, inplace=True
			)

		return df_mad_summary

	def _save_market_summary(self, df_mad_summary, prefix):
		processed_path = self.ade_report_mail_path / "processed"
		collected_path = self.ade_report_mail_path / "collected"

		processed_path.mkdir(exist_ok=True, parents=True)
		collected_path.mkdir(exist_ok=True, parents=True)

		ade_report_mail_filename = (
			prefix
			+ self.tech
			+ "_"
			+ self.data_type
			+ "_"
			+ str(self.threshold)
			+ "_"
			+ str(self.day_range)
			+ "_days_result_"
			+ str(self.date)
			+ ".csv"
		)

		processed_summary_file = (
			self.ade_report_mail_path / "processed" / ade_report_mail_filename
		)

		if Path.is_file(processed_summary_file):
			print(f"MAD Report already processed: {processed_summary_file}")
		else:
			market_summary_file = (
				self.ade_report_mail_path / "collected" / ade_report_mail_filename
			)
			df_mad_summary.to_csv(
				market_summary_file, index=None, header=True, na_rep=""
			)
			print(f"Save MAD Report : {market_summary_file}")

	def _save_summary_dump(self, df_mad_summary, file_name):

		if self.tech == "LTE":
			dump_date_path = self.param_path / self.tech / str(self.date)
		else:
			dump_date_path = self.param_path / str(self.date)
		dump_date_path.mkdir(exist_ok=True, parents=True)
		dump_file_name = str(self.date) + "_" + self.data_type + "_" + file_name
		dump_summary_file = dump_date_path / dump_file_name

		df_mad_summary.to_csv(dump_summary_file, index=None, header=True, na_rep="")
		print(f"Save MAD Report Summary Table Dump : {dump_summary_file}")

	def report_market_summary(self, threshold=None, day_range=None):
		if threshold is None:
			threshold = 10
		if day_range is None:
			day_range = 2

		if (
			self.tech == "LTE"
		):  # 'C:/Users/l.yang.CORP/Desktop/ade/data/mad_result/BH/LTE/ALPT/20240830/summ...
			self.mad_summary_path = (
				self.mad_result_path / str(self.date) / "summary_tables"
			)
		else:
			self.mad_summary_path = (
				self.mad_result_path / str(self.date) / "summary_tables"
			)
		mad_summary_fileList = [x for x in self.mad_summary_path.glob("*.csv")]
		mad_summary_fileList.sort()

		final_date = self._set_target_date(self.date)

		for mad_summary_file in mad_summary_fileList:
			file_name = str(mad_summary_file).split("/")[-1]

			# if '10_2_days' not in file_name:
			# 	continue
			checker = str(threshold) + "_" + str(day_range) + "_days"
			if checker not in file_name:
				continue
			print(f"MAD Report File : {file_name}")

			self.threshold = file_name.split("_")[2]
			self.day_range = file_name.split("_")[3]

			df_mad_summary = pd.read_csv(mad_summary_file, on_bad_lines="skip")
			if df_mad_summary.empty:
				df_mad_summary = self._set_market_superset(df_mad_summary)
				df_mad_summary = self._column_rename(df_mad_summary)
				df_mad_summary = df_mad_summary.assign(
					kpi_name=["No Anomalies Detected"]
				)
			else:
				self._save_summary_dump(df_mad_summary, file_name)
				df_mad_summary = self._set_market_superset(df_mad_summary)
				df_mad_summary = self._column_rename(df_mad_summary)
			df_mad_summary["report_date"] = final_date
			df_mad_summary["threshold"] = int(self.threshold)
			df_mad_summary["day_range"] = int(self.day_range)
			df_mad_summary.fillna("", inplace=True)

			if checker == "10_2_days":
				prefix = "ade_report_mail_"
			elif checker == "50_1_days":
				prefix = "ade_report_one_day_mail_"
			elif checker == "50_10_days":
				prefix = "ade_report_emtc_nbiot_mail_"
			elif checker == "20_7_days":
				prefix = "ade_report_band_mail_"
			else:
				prefix = "TBD_"
			self._save_market_summary(df_mad_summary, prefix)
			# C:
			# Here no combination of many summaries tables but just reformat each table with superset of markets and some other changes.
