import json

from report_maker.loader import Loader
from report_maker.mad_postprocessor import MADPostProcessor


class ReportMaker:
	def __init__(self, date, tech, data_type, band, time_frame, algorithm):
		self.date = date
		self.tech = tech
		self.band = band
		self.data_type = data_type
		self.time_frame = time_frame
		self.algorithm = algorithm

		with open("report_maker/config.json", "r") as cfg_file:
			self.config = json.load(cfg_file)

	def _make_result_report(self, threshold, day_range, ade_report_mail_path):
		print(f"Start Make Report (threshold: {threshold} | day_range: {day_range})...")
		mad_postprocessor = MADPostProcessor(
			self.date,
			self.tech,
			self.mad_result_path,
			ade_report_mail_path,
			self.param_path,
			self.data_type,
		)
		mad_postprocessor.report_market_summary(
			threshold=threshold, day_range=day_range
		)
		print("...Make Report done.")

	def _load_top_offender_mad(self):
		print("Start Load & Save Top Offender...")
		self.top_offender_loader = Loader(
			self.date,
			self.tech,
			self.mad_result_path,
			self.param_path,
			self.report_top_offender_path,
			self.data_type,
			self.band,
			self.config,
		)
		(
			self.df_top_offender,
			self.dict_market_site,
			self.dict_market_top_offender,
			self.dict_maket_top_KPI,
			self.final_date,
		) = self.top_offender_loader.load_top_offender()

		if self.data_type != "USM_EMTC_NBIOT" and self.data_type != "BAND":
			self.top_offender_oneday_loader = Loader(
				self.date,
				self.tech,
				self.mad_result_path,
				self.param_path,
				self.report_top_offender_one_day_path,
				self.data_type,
				self.band,
				self.config,
			)
			self.top_offender_oneday_loader.report_top_offender()  # This is for saving oneday case. Multiple-day case already saved in the previous .load_top_offender()
		print("...Load & Save Top Offender done")

	def run(self):
		print("*** Execute Report ***")

		if self.tech == "LTE":
			self.mad_result_path = f"{self.config['MAD_RESULT_PATH']}/{self.time_frame}/{self.tech}/{self.data_type}"
			self.param_path = self.config[self.tech]["REPORT_DUMP"]
			self.ade_report_mail_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/ade_report_mail/"
			self.report_top_offender_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/ade_report_top_offender_mail/"
		else:
			self.mad_result_path = f"{self.config['MAD_RESULT_PATH']}/{self.time_frame}/{self.tech}/{self.data_type}/{self.band}"
			self.param_path = self.config[self.tech]["REPORT_DUMP"]
			self.ade_report_mail_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/{self.band}/ade_report_mail/"
			self.report_top_offender_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/{self.band}/ade_report_top_offender_mail/"

		self._make_result_report(
			self.config[self.tech][self.data_type]["THRESHOLD"],
			self.config[self.tech][self.data_type]["DAY_RANGE"],
			self.ade_report_mail_path,
		)  # multi-day, ex. >=2
		if (
			self.config[self.tech][self.data_type]["CRITICAL"] == True
		):  # single-day case.
			if self.tech == "LTE":
				self.ade_report_mail_one_day_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/ade_report_one_day_mail/"
				self.report_top_offender_one_day_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/ade_report_top_offender_mail/"
			else:
				self.ade_report_mail_one_day_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/{self.band}/ade_report_one_day_mail/"
				self.report_top_offender_one_day_path = f"{self.config['REPORT_PATH']}/{self.algorithm}/{self.time_frame}/{self.tech}/{self.data_type}/{self.band}/ade_report_top_offender_mail/"

			self._make_result_report(
				self.config["THRESHOLD_ONE_DAY"],
				self.config["DAY_RANGE_ONE_DAY"],
				self.ade_report_mail_one_day_path,
			)

		self._load_top_offender_mad()
