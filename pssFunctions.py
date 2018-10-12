# -*- coding: utf-8 -*-
import sys, os, re, itertools

from string import ascii_lowercase

from PyQt5.QtGui import (QValidator, QRegExpValidator, QPixmap)

from PyQt5.QtCore import (QThread, pyqtSignal, QRegExp, Qt)

from PyQt5.QtWidgets import (QTreeWidgetItem, QMainWindow, QApplication,
	QTableWidgetItem, QHeaderView, QSplashScreen, QProgressBar)


""" sorts string by case, not by letter """
def case_sort(string, length = 2):
	lists = [string[i:i + 2] for i in range(0, len(string), 2)]

	for lst in lists:
		lists[lists.index(lst)] = "".join(
			sorted(list(lst), key = lambda L: (L.lower(), L)))

	return "".join(lists)

# verifies that each letter type in the inputs occurs only twice, otherwise it won"t solve
def validate_letters(first_string, second_string):
	isvalid = True
	# interate thru all lowercase letters
	for string in [first_string, second_string]:
		for letter in ascii_lowercase:
			# if the letter is in the input, make sure it only occurs twice
			if string.lower().count(letter) > 0 and string.lower().count(letter) != 2:
				isvalid = False
			else:
				pass

	return isvalid

""" validates string inputs """
def validate(state, first_string, second_string):
	if (len(first_string) == len(second_string) and first_string.lower() == second_string.lower() and \
	len(first_string)% 2 == 0) and  validate_letters(first_string, second_string):

		if state == QValidator.Acceptable:
			state = QValidator.Acceptable

	elif ((len(first_string)%2 == 0) or (len(second_string)%2 == 0)) and ((len(first_string) == 0 or len(second_string) == 0)):
		if state == QValidator.Acceptable:
			state = QValidator.Intermediate

	else:
		state = QValidator.Invalid

	return state


class visualThread(QThread):

	thread_signal = pyqtSignal(list)

	def __init__(self, view, solved):
		QThread.__init__(self)
		self.view = view
		self.solved = solved

	def __del__(self):
		self.wait()

	def run(self):
		for y in range(len(self.solved.axis[0])):
			for x in range(len(self.solved.axis[0])):
				self.thread_signal.emit([x, y, str(case_sort(self.solved.solved_array[x][y][::-1]))])
				QApplication.processEvents()

class solveThread(QThread):
	thread_signal = pyqtSignal("PyQt_PyObject")

	def __init__(self, f1, f2, button):
		QThread.__init__(self)
		self.f1, self.f2 = f1, f2
		self.button = button
		self.button.setEnabled(False)
		self.button.setText("Solving. . .")

	def __del__(self):
		self.wait()

	def run(self):
		solved = SolveSquare(self.f1, self.f2)
		self.button.setEnabled(True)
		self.button.setText("Solve!")
		self.thread_signal.emit(solved)


class TreeWidgetItem(QTreeWidgetItem):
    """
    Recreates the TreeWidgetItem so that the column which displays percents can be sorted
    numerically.
    """
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        return self.natural_sort_key(key1) < self.natural_sort_key(key2)


    @staticmethod
    def natural_sort_key(key):
        regex = "(\d*\.\d+|\d+)"
        parts = re.split(regex, key)
        return tuple((e if i % 2 == 0 else float(e)) for i, e in enumerate(parts))

class SolveSquare:

	def __init__(self, f1_genes, f2_genes):
		self.f1_genes, self.f2_genes = f1_genes, f2_genes
		self.break_down()
		self.get_genotype()
		self.format_genotype()
		self.count_outcomes()

	def break_down(self):
		"""
		This method breaks down the two inputs (F1 & F2) so that they can be used to solve the
		square. They"re broken into lists, then then every two elements in the list are grouped
		together in list. These >1 # lists are then used to make permutations of all the characters
		of all the lists (e.g. of ["T", "t"], ["b, "b"] and ["R", "r"]). The permutations of each
		Fillial are then assigned to axis so that the pss_core QTableView can make headers, and
		so that the get_genotype can partially solve the square
		"""
		f1, f2 = iter(list(self.f1_genes)), iter(list(self.f2_genes))

		f1_sorted = [[x, next(f1)] for x in f1]
		f2_sorted = [[x, next(f2)] for x in f2]

		x_axis_alleles = ["".join(x) for x in itertools.product(*f1_sorted)]
		y_axis_alleles = ["".join(x) for x in itertools.product(*f2_sorted)]

		self.axis = [x_axis_alleles, y_axis_alleles]

	def get_genotype(self):
		# Every item in the x axis is added to every item in the y axis to give unformated outcomes
		self.genotype = []
		for item in self.axis[0]:
			self.genotype.append([item + x for x in self.axis[1]])

	def format_genotype(self):
		# Goes through the unformated outcomes and then sorts them by char and case for proper nomeclature
		self.solved_array = [[("".join(sorted(list(sub_item), key=lambda L: (L.lower(), L)))) for sub_item in item] for item in self.genotype]

	def count_outcomes(self):
		# Once everything is solved and formatted, this simple counter method counts the number of each outcome and the number of total outcomes
		# This will be used in pss_core to display outcome data/percents
		self.counter = {}
		self.total_outcomes = 0

		for set in self.solved_array:
			for item in set:
				self.total_outcomes += 1

				if item in self.counter:
					self.counter[item] += 1
				else:
					self.counter[item] = 1
