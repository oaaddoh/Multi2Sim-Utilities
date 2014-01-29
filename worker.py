import csv
import numpy as np
import matplotlib.pyplot as plt

	
def parser(i, o):
	
	#compute the needed parameters for a particular compute unit
	#create dictionary to hold variables for each CU, all file handlers are also stored here
	global c_units
	c_units = {} 
	k = 0
	while k < 32:
		params = []
		key = k #cu ID
		c_units[key] = [] #list  format is [CU name, 
		c_units[key].append('CU %s' % k)
		c_units[key].append(0) #temp cycle for computation
		c_units[key].append(0) #idle cycles, updated during computation
		c_units[key].append(0) #current cycle in CU
		c_units[key].append(0) #diff variable for computing idle cycles
		filename = o + '_cu_%s' % k #build filename
		c_units[key].append(filename) #store filename here
		c_units[key].append('outfile_cu_%s' % k) #store file handler here
		(c_units[key][6]) = open(filename, "wb") #open file to write CU* specific output to
		c_units[key].append(csv.writer((c_units[key][6]), quoting=False)) #store csv writer here
		c_units[key].append(0) #store wg id here
		c_units[key].append(0) #store wf id here
		c_units[key].append(0) #store uop ID in CU
		c_units[key].append(0) #store uop ID in WF
		c_units[key].append("") #store assembly instruction here

		k += 1

	#print c_units

	with open(i, "rb") as infile:#, open(o, "wb") as outfile:
		#TODO: add conditonal opening of files based on CU IDs chosen at the command line
		#also conditionally declare variables
		#we also need an option in the command line that asks to parse and generate all statistics. This will avoid very verbose commands
		reader = csv.reader(infile)
		#writer = csv.writer(outfile, quoting=False)
		for i, line in enumerate(reader):
			desc = line[0].split()
			if desc[0] == "si.new_inst": #TODO: make this use the option read from command line asking to parse fetch stage information.
				cu_id = int((desc[2].split('='))[1]) #use cu id as key for c_units dictionary
				(c_units[cu_id])[8] = ((desc[5].split('='))[1]) #wg id
				(c_units[cu_id])[9] = ((desc[6].split('='))[1]) #wf id
				(c_units[cu_id])[10] = ((desc[1].split('='))[1]) #UOP ID in CU
				(c_units[cu_id])[11] = ((desc[7].split('='))[1]) #UOP ID in WF
				(c_units[cu_id])[12] = ((desc[9].split('='))[1]) #ASM instr


				(c_units[cu_id])[3] = (desc[3].split('='))[1] #current cycle in CU
				if int(str((c_units[cu_id])[3])) - int(str((c_units[cu_id])[1])) > 1:
					(c_units[cu_id])[4] = (int((c_units[cu_id])[3]) - int((c_units[cu_id])[1])) #calcute diff: current cycle - previous cycle
					(c_units[cu_id])[2] = (c_units[cu_id])[2] + (c_units[cu_id])[4] - 1 #calculate idle cycles: idle cycles + diff - 1
					#new_line = desc[0] + ', CU_id: ' + str(cu_id) + ', CU_cycle: ' + (c_units[cu_id])[3] + ', diff: ' + str((c_units[cu_id])[4]) + ', idle_cycles: ' + str((c_units[cu_id])[2]) + ', WG ID : ' + (c_units[cu_id])[8] + ', WF ID: ' + (c_units[cu_id])[9] + ', UOP ID in CU: ' + (c_units[cu_id])[10] + ', UOP ID in WF: ' + (c_units[cu_id])[11] + ', asm_trim: ' + (c_units[cu_id])[12]
					(c_units[cu_id])[7].writerow([ desc[0], ' CU_id', str(cu_id), ' CU_cycle', (c_units[cu_id])[3], ' diff', str((c_units[cu_id])[4]), ' idle_cycles', str((c_units[cu_id])[2]), ' WG ID', (c_units[cu_id])[8], ' WF ID' + (c_units[cu_id])[9], ' UOP ID in CU', (c_units[cu_id])[10], ' UOP ID in WF', (c_units[cu_id])[11], ' asm_trim', (c_units[cu_id])[12] ])
				(c_units[cu_id])[1] = (c_units[cu_id])[3] #store current cycle to be used as prev cycle in next iteration

		#compute idle cycle statistics for all CUs

		summary = open("summary", "wb") #open file to write CU* specific output to
                writer = csv.writer(summary, quoting=False) #store csv writer here


		k = 0
		while k < 32:
			if c_units[k][3] == 0:
				writer.writerow([ 'Compute unit', k, ' Unused' ])
			else:
				p_idle = float(c_units[k][2])/float(c_units[k][3]) * 100
				writer.writerow([ 'Compute unit', k, ' Idle cycles is', c_units[k][2], ' Total cycles', c_units[k][3], ' Percent idle', p_idle ])
				#print 'Compute unit :', k, ', Idle cycles is: ', c_units[k][2], ', Total cycles: ', c_units[k][3], ',Percent idle :', p_idle
			k += 1

		data = np.genfromtxt('summary',delimiter=',', dtype = float)
