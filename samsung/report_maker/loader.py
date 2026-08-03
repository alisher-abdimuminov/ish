import copy
from datetime import datetime
from pathlib import Path

import pandas as pd


class Loader:
	def __init__(
		self,
		date,
		tech,
		mad_result_path,
		param_path,
		report_top_offender_path,
		data_type,
		band,
		config,
		**kwargs,
	):
		self.date = date
		self.tech = tech
		self.mad_result_path = Path(mad_result_path)
		self.param_path = Path(param_path)
		self.report_top_offender_path = Path(report_top_offender_path)
		if data_type == "PM":
			self.data_type = "USM"
		else:
			self.data_type = data_type
		self.band = band
		self.config = config

	def _str_enb_id(self, x):
		enb_id = x[0]
		enb_id_str = "ENB_" + str(enb_id)
		return enb_id_str

	def _report_top_offender(self, df_all, id, prefix):
		df_all_top_offender = copy.deepcopy(df_all)

		df_all_top_offender["direction_abs_num_change"] = df_all_top_offender[
			"num_change"
		].abs()
		df_all_top_offender = (
			df_all_top_offender.sort_values("direction_abs_num_change", ascending=False)
			.drop_duplicates(["sub_market", id, "kpi_name"])
			.sort_index()
		)
		df_all_top_offender = df_all_top_offender.reset_index(drop=True)
		df_all_top_offender = df_all_top_offender.drop(
			["direction_abs_num_change"], axis=1
		)

		report_date = (datetime.strptime(self.date, "%Y%m%d")).strftime(
			"%Y/%m/%d %H:%M:%S"
		)
		df_all_top_offender["report_date"] = report_date

		self._save_report_top_offender(df_all_top_offender, prefix)

	def _save_report_top_offender(self, df_all_top_offender, prefix):
		processed_path = self.report_top_offender_path / "processed"
		collected_path = self.report_top_offender_path / "collected"

		processed_path.mkdir(exist_ok=True, parents=True)
		collected_path.mkdir(exist_ok=True, parents=True)

		if self.tech == "LTE":
			ade_report_top_offender_filename = (
				prefix
				+ self.tech
				+ "_"
				+ self.data_type
				+ "_"
				+ str(self.date)
				+ ".csv"
			)
		else:
			ade_report_top_offender_filename = (
				prefix
				+ self.tech
				+ "_"
				+ self.data_type
				+ "_"
				+ self.band
				+ "_"
				+ str(self.date)
				+ ".csv"
			)

		top_offender_processed_file = processed_path / ade_report_top_offender_filename

		if Path.is_file(top_offender_processed_file):
			print(f"MAD Report already processed: {top_offender_processed_file}")
		else:
			top_offender_file = collected_path / ade_report_top_offender_filename
			df_all_top_offender.to_csv(
				top_offender_file, index=None, header=True, na_rep=""
			)
			print(f"Save Top Offender Report : {top_offender_file}")

	def _remain_top_offender_only(self, df_top_offender):
		top_offender_indexNames = df_top_offender[
			(df_top_offender["top_offenders"] != "Top-Offender")
		].index
		# This is no longer necessary in the new version where the top_offender intermediate files are already filtered.

		df_top_offender.drop(top_offender_indexNames, inplace=True)
		df_top_offender = df_top_offender.reset_index(drop=True)

		return df_top_offender

	def _get_top_offender_path(self):
		return self.mad_result_path / str(self.date) / "df_top_offender"

	def load_top_offender(self):
		top_offender_path = self._get_top_offender_path()  # mad_result...
		print(f"MAD Top Offender Result Path : {top_offender_path}")

		top_offender_fileList = [x for x in top_offender_path.glob("*.csv")]
		top_offender_fileList.sort()  # file format ...2025_07_25_110_kpi_name_TopOffender.csv

		df_site = pd.DataFrame()
		df_all = pd.DataFrame()
		print("Start Save Top Offender...")
		if len(top_offender_fileList) <= 0:
			df_all = pd.DataFrame()
			dict_market_site = {}
			dict_market_top_offender = {}
			dict_market_top_KPI = {}
			final_date = self.date
			return (
				df_all,
				dict_market_site,
				dict_market_top_offender,
				dict_market_top_KPI,
				final_date,
			)
		else:
			for top_offender_file in top_offender_fileList:
				if "TopOffender" in str(top_offender_file):
					df_top_offender = pd.read_csv(
						top_offender_file, on_bad_lines="skip"
					)  # C: so far, df_top_offender includes both offender sites and non-offender sites.

					# self._save_top_offender(top_offender_file, df_top_offender) # C: The above two sentences read one top-offender file from mad_result folder to dump folder. For what useage?
					# C: df_site below includes all sites both offender and non-offender, while df_all includes only top offenders?

					df_site = pd.concat([df_site, df_top_offender], axis=0).reset_index(
						drop=True
					)

					df_top_offender = self._remain_top_offender_only(
						df_top_offender
					)  # C: df_top_offender here means df with only top-offenders. In other files, df_top_offender may also include non-offenders.

					df_all = pd.concat([df_all, df_top_offender], axis=0).reset_index(
						drop=True
					)
				else:
					continue

			try:
				if self.tech == "LTE":
					id = "enb_id"
				else:
					if (
						self.data_type == "GNB"
						or self.data_type == "GNB_QCI"
						or self.data_type == "NG"
					):
						id = "gnb_id"
					else:
						id = "du_id"

				### Add report top offender mail ### This part seems all we need for reporting my emails? All the rest saved to dump etc, are for GUI?
				prefix = "ade_report_top_offender_"
				self._report_top_offender(df_all, id, prefix)
				######

				# The group of code is added to make the original working without big change
				dict_market_site = {}
				dict_market_top_offender = {}
				dict_market_top_KPI = {}
				final_date = self.date
				####################################
			except Exception as e:
				print("Error occurred during load market-top_offender dict")
				dict_market_site = {}
				dict_market_top_offender = {}
				dict_market_top_KPI = {}
				final_date = self.date

			return (
				df_all,
				dict_market_site,
				dict_market_top_offender,
				dict_market_top_KPI,
				final_date,
			)

	def report_top_offender(self):  # for one day case
		##### oneday #####
		top_offender_path = self._get_top_offender_path()
		top_offender_oneday_path = top_offender_path / "top_offender_oneday"
		top_offender_oneday_fileList = [
			x for x in top_offender_oneday_path.glob("*.csv")
		]
		top_offender_oneday_fileList.sort()

		df_oneday = pd.DataFrame()
		if len(top_offender_oneday_fileList) > 0:
			for top_offender_oneday_file in top_offender_oneday_fileList:
				if "oneday_TopOffender" in str(top_offender_oneday_file):
					df_top_offender_oneday = pd.read_csv(
						top_offender_oneday_file, on_bad_lines="skip"
					)
					df_top_offender_oneday = self._remain_top_offender_only(
						df_top_offender_oneday
					)
					df_oneday = pd.concat(
						[df_oneday, df_top_offender_oneday], axis=0
					).reset_index(drop=True)
				else:
					continue

			try:
				if self.tech == "LTE":
					id = "enb_id"
				else:
					if (
						self.data_type == "GNB"
						or self.data_type == "GNB_QCI"
						or self.data_type == "NG"
					):
						id = "gnb_id"
					else:
						id = "du_id"

				prefix = "ade_report_top_offender_one_day_"
				self._report_top_offender(df_oneday, id, prefix)

			except Exception as e:
				print("Error occurred during make 1 day top offender")

		else:
			print("no 1 day top offender")
