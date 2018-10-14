# -*- coding: utf-8 -*-
from pssGraphics import Ui_MainWindow as graphics
from pssFunctions import *

# TODO
# Rewrite and format program for readilibty

# Last fix: 22/10/2017 1:01 PM EST


class Main(QMainWindow, graphics):

	def __init__(self):
		# basic UI setup and connections
		super(self.__class__, self).__init__()
		self.setupUi(self)

		self.f1_input.textChanged.connect(self.validate_input)
		self.f2_input.textChanged.connect(self.validate_input)

		# only allow alpha character input
		f1_input_validator = QRegExpValidator(QRegExp("[a-zA-Z]+"), self.f1_input)
		f2_input_validator = QRegExpValidator(QRegExp("[a-zA-Z]+"), self.f2_input)

		self.f1_input.setValidator(f1_input_validator)
		self.f2_input.setValidator(f2_input_validator)

		self.solve_punnett_square_button.clicked.connect(self.call_solve)

	def validate_input(self, *args, **kwargs):
		# visual display of validity for user, green is valid, red is invalid

		sender = self.sender()
		validator = sender.validator()

		try:
			state = validator.validate(sender.text(), 0)[0]
			state = validate(state, self.f1_input.text(), self.f2_input.text())

		except AttributeError:
			state = QValidator.Invalid

		if state == QValidator.Acceptable:
			color = "#c4df9b" # green
			self.solve_punnett_square_button.setEnabled(True)

		elif state == QValidator.Intermediate:
			color = "#fff79a" # yellow
			self.solve_punnett_square_button.setEnabled(False)

		else:
			color = "#f6989d" # red
			self.solve_punnett_square_button.setEnabled(False)

		self.f1_input.setStyleSheet("QLineEdit { background-color: %s }" % color)
		self.f2_input.setStyleSheet("QLineEdit { background-color: %s }" % color)

    # because fuck Qt
	# we don't update GUI thread from worker thread
	def update_view(self, data):
		self.punnett_square_view.setItem(data[0], data[1], QTableWidgetItem(data[2]))

	def show_solved(self, solved):
		# stylesheet of square
		self.punnett_square_view.setStyleSheet("QHeaderView::section{Background-color:rgb(0, 102, 0);}")

		# creates enough cells to be populated by the solved square
		self.punnett_square_view.setRowCount(len(solved.axis[0]))
		self.punnett_square_view.setColumnCount(len(solved.axis[1]))

		# give the rows and columns headers based on their genotye
		self.punnett_square_view.setHorizontalHeaderLabels(solved.axis[1])
		self.punnett_square_view.setVerticalHeaderLabels(solved.axis[0])

		# populate table with genotype outcomes to create punnett square
		self.vthread = visualThread(self.punnett_square_view, solved)
		self.vthread.thread_signal.connect(self.update_view)
		self.vthread.start()
		self.punnett_square_view.setEnabled(True)

		# min size is 150x150 for cells, but stretch if extra space, keeping all cells even
		header = self.punnett_square_view.horizontalHeader()
		header.setSectionResizeMode(QHeaderView.Stretch)

		header2 = self.punnett_square_view.verticalHeader()
		header2.setSectionResizeMode(QHeaderView.Stretch)

		# table that shows genotype occurance stats
		# clears old data, fills in new data
		self.data_view.clear()
		self.data_view.setStyleSheet("QHeaderView::section{Background-color:rgb(0, 102, 0);}")
		for k, v in solved.counter.items():
			child = TreeWidgetItem([sort_by_case(k[::-1]), str((v/solved.total_outcomes*100))])
			self.data_view.addTopLevelItem(child)

		self.data_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.data_view.header().setStretchLastSection(True)

		self.data_view.setEnabled(True)

		# label that displays the genetic cross
		self.cross_label.setText("Cross: {0} x {1}".format(sort_by_case(self.f1_genes), sort_by_case(self.f2_genes)))
		self.cross_label.setStyleSheet("color:rgb(0, 102, 0);")
		self.cross_label.setEnabled(True)


	def call_solve(self):
		# get the input text
		self.f1_genes, self.f2_genes = self.f1_input.text(), self.f2_input.text()

		# start solve thread, pass inputs as parameters, set signal to send results to display function
		self.solve_thread = solveThread(self.f1_genes, self.f2_genes, self.solve_punnett_square_button)
		self.solve_thread.thread_signal.connect(self.show_solved)

		self.solve_thread.start()

if __name__ == "__main__":
	import sys, time

	app = QApplication(sys.argv)

	# TODO: fetch pss_splash.png from any folder pssCore.py is started in
	splash_img = QPixmap("pss_splash.png")
	splash = QSplashScreen(splash_img, Qt.WindowStaysOnTopHint)
	splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

	load_bar = QProgressBar(splash)
	load_bar.setTextVisible(True)
	load_bar.setFormat("Loading. . .")
	load_bar.setAlignment(Qt.AlignCenter)
	load_bar.setMaximum(20)
	load_bar.setGeometry(0, splash_img.height() - 20, splash_img.width(), 20)

	splash.show()

	# increment load bar
	for load in range(1, 20):
		load_bar.setValue(load)
		t = time.time()
		while time.time() < t + 0.1:
			app.processEvents()

	root = Main()
	splash.finish(root)
	root.show()

	sys.exit(app.exec_())
