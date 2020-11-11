# -*- coding: utf-8 -*-
"""
	Project:
		Mask Match
		
	Authors:
		Ram Bala, Rohit Jacob ( Project Stanley [https://projectstanley.org/] )
		
	Invokation:
		from mask_match import donor_optimizer

	Description:
		This module matches donors to recipients using Google Optimization using Glop

	Example Invokation:
		$ python mask_match.py
"""

from __future__ import print_function
from ortools.linear_solver import pywraplp

import warnings
warnings.filterwarnings("ignore")
# Examples:
# donors_cap = [5,1,1,1,2]
# recipients_cap = [5,5]
# dist_dict = {'d0_r0':125, 'd0_r1':435, ...}


def donor_optimizer(donors_cap, recipients_cap, dist_dict):
	'''
	Variables:
		- donors_cap = [5,1,1,1,2]
		- recipients_cap = [5,5]

		- dist_dict = {'d0_r0':125, 'd0_r1':435, ...}
	'''
	# Creating dictionary for validation in the end
	donor_dict = {i:{"Capacity":x} for i,x in enumerate(donors_cap)}
	recipient_dict = {j:{"Capacity":x} for j,x in enumerate(recipients_cap)}
	# --
	solver = pywraplp.Solver('ProjectMask',
			pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
	# --
	# Creating the optimization variables
	optimization_variables = []
	for i,d in enumerate(donors_cap):
		donors_per_recipients = []
		for j,r in enumerate(recipients_cap):
			# Create the variables and let them take on any non-negative value.
			donors_per_recipients.append(solver.NumVar(0, solver.infinity(), 'x'+str(i)+str(j)))
		optimization_variables.append(donors_per_recipients)
	print("- Created optimization variables")
	# --
	# Constaint 1: sum(optimization_variables[all][j]) <=recipients_cap[j])
	for j,r in enumerate(recipients_cap):
		constraint1 = solver.Constraint(0, r)
		for i,d in enumerate(donors_cap):
			constraint1.SetCoefficient(optimization_variables[i][j], 1)
	print("- Applied Constraint: sum(optimization_variables[all][j]) <= recipients_cap[j])")
	# --
	# Constaint 2: sum(optimization_variables[i][all]) == donors_cap[i])
	for i,d in enumerate(donors_cap):
		constraint2 = solver.Constraint(d, d)
		for j,r in enumerate(recipients_cap):
			constraint2.SetCoefficient(optimization_variables[i][j], 1)
	print("- Applied Constraint: sum(optimization_variables[i][all]) == donors_cap[i])")
	# --
	# Objective function: min(sum(d * optimization_variables[all][all]))
	objective = solver.Objective()
	for i,d in enumerate(donors_cap):
		for j,r in enumerate(recipients_cap):
			objective.SetCoefficient(optimization_variables[i][j], dist_dict['d'+str(i)+'_r'+str(j)])
	#Set to find minimum
	objective.SetMinimization()
	# --
	print("- Objective Set: min(d * sum(optimization_variables[all][all]))")
	print("- Solver doing what solver does best!")
	status = solver.Solve()
	output_list = list()
	if status == solver.OPTIMAL:
		print("- Status: Found Optimal Solution")
		for i,d in enumerate(donors_cap):
			for j,r in enumerate(recipients_cap):
				value_to_donate = optimization_variables[i][j].solution_value()
				if value_to_donate > 0:
					output_list.append({'donor_id':i,'recipient_id':j,'donation_amount':value_to_donate})
	elif status == solver.FEASIBLE:
		print('- Status: A potentially suboptimal solution was found.')
		for i,d in enumerate(donors_cap):
			for j,r in enumerate(recipients_cap):
				value_to_donate = optimization_variables[i][j].solution_value()
				if value_to_donate > 0:
					output_list.append({'donor_id':i,'recipient_id':j,'donation_amount':value_to_donate})
	else:
		print('- Status: The solver could not solve the problem. Please check your data')
	return output_list
