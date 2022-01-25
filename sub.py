overallContainer,timing,scanningExceptions = settypes(pd.DataFrame(
	columns = data_types.keys()
)), pd.DataFrame(
	columns = ['ProjectName','ToolName','Time (s)']
), pd.DataFrame(
	columns = ["Time", "App","Proj","Exception"]
)

extra_logging, break_time = False, 2 * 60 * 60

#ut.timeout(break_time) #Seconds, 2 hours, 60 minutes per hour, 60 seconds per minute
def scan_abstraction(app, proj_name):
	"""
	Wrapping the scan in a nested method to add a timeout
	Added this when a project took too long
	"""
	return app.scan(proj_name,True)

#Creating the base vulnerability set from information.json
mapped_vuln = retrieve_vuln_info(vuln_base_information_file)

disp_msg("Starting the full scann")
for app_itr, app in enumerate(applications):
	disp_msg(f"Starting to scan with the app: {app.name()}")
	#Determining the name of the tool, all metrics are mashed under one name
	name = app.name() if app in scanners else metrics_name

	if prepare is not None:
		full_libraries = prepare
	else:
		full_libraries = re("*.json")
	for LibraryValue in progressBar(full_libraries):
		if prepare is None:
			with open(LibraryValue,'r') as reader:
				dictionary = json.load(reader)
		else:
			dictionary = LibraryValue

		append = []
		for proj_itr, (proj_name,proj_value) in enumerate(dictionary.items()):

			#Downloading the url and information
			disp_msg(f"Checking for:> {proj_name}")
			total_app_number = (proj_itr+1) + (len(dictionary.keys()) * app_itr)
			total_app_len = (len(dictionary.keys()) * len(applications))
			disp_msg(f"Currently at application {total_app_number}: {percent(total_app_number,total_app_len)}%")
			cloned = False
			cloner_url = None
			if not os.path.exists(proj_name):
				cloned, cloner_url = True, "git clone --depth 1"
				if tag := safe_get_check(proj_value,'tag'):
					cloner_url = f"{cloner_url} --branch '{tag}'"

				exey(f"{cloner_url} {proj_value['url']}")
				if commit := safe_get_check(proj_value,'commit'):
					exey(f"cd {proj_name} && git reset --hard {commit} && cd ../")
					cloner_url += f" && cd {proj_name}/ && git reset --hard {commit}"

			try:
				#Creating a shadow copy for the current project
				vulns, successfully_scanned = None if mapped_vuln is None else mapped_vuln(proj_name), True

				try:
					#Wrapping the scan in a light timeout to ensure all the projects will be scanned timely
					#But only the scan, mapping the results is fine
					disp_msg(f"Scanning the project {proj_name} with the application {name}")
					(app_results,app_timing) = scan_abstraction(app, proj_name)
					disp_msg(f"Finished scanning the project {proj_name} with the application {name}")
				except Exception as e:
					disp_msg(f"Out of time :> {e}")
					successfully_scanned, app_timing, now = False, break_time, timr.now()

					scanningExceptions = scanningExceptions.append(
						pd.DataFrame(
							[{
								"Time": now.strftime('%Y-%m-%dT%H:%M:%S') + ('.%04d' % (now.microsecond / 10000)),
								"App": f"{name}",
								"Proj": f"{proj_name}",
								"Exception": f"Time out at {break_time} seconds"
							}],
							columns = ["Time","App","Proj","Exception"]
						)
					)
					pass

				#Appending the current time results into the time dataframe
				timing = timing.append(pd.DataFrame(
					[{
						'ProjectName':proj_name,
						'ToolName':app.name(),
						'Time (s)':app_timing,
					}]
				), ignore_index=True)
				disp(f"Set the timing information")

				disp_msg(f"Successfully scanned: {successfully_scanned}")
				if successfully_scanned:
					#Mapping the raw results of the scan to common model and setting the types
					app_set_types = settypes(app.mapp(app_results,proj_name,columns=data_types.keys(),gen=gen,time_taken=app_timing))

					#Saving the partial information to a csv file
					app_set_types.to_csv(f"{app.name()}_{proj_name}_FULLYSCAN.csv")
				else:
					# Setting the results to a hollow dataset if there is a timeout
					app_set_types = pd.DataFrame([gen()],columns=data_types.keys())

				app_set_types['projecttype'] = "OverScan"
				app_set_types['projecturl'] = cloner_url

				#If this is the first fileset scanner (metric), loop through the results first to add them to the overall, otherwise loop through the core dataset
				if app_itr == 0:
					lyst_one,lyst_two = app_set_types, overallContainer
				else:
					lyst_one,lyst_two = overallContainer, app_set_types

				disp_msg(f"Starting to loop through the overall container dataset")
				total_rows = len(lyst_one.index)
				#Looping through the lyst one dataset
				for lyst_one_itr, lyst_one_data in enumerate(lyst_one.itertuples(index=False)):
					if extra_logging:
						disp(f"Examining the row {lyst_one_itr}/{total_rows}: {rnd(lyst_one_itr/total_rows)}")

					#Safe grabber from the first lyst
					def get_from_lyst_one(attribute):
						if hasattr(lyst_one_data, attribute):
							return getattr(lyst_one_data, attribute)
						else:
							return np.NaN

					#Checking if the current file has metrics associated with it, and grabbing the metrics
					matched_results = lyst_two[(lyst_two['qual_name'] == get_from_lyst_one('qual_name')) & (get_from_lyst_one('tool_name') == metrics_name)]
					len_matched_results = len(matched_results.index)

					if True:
						disp(f"There are {len_matched_results} matched results")
					if app_itr > 0: #If theres a match, loop through
						for matched_itr,matched_data in enumerate(matched_results.itertuples(index=False)):
							if extra_logging:
								disp(f"Examining the matched row {matched_itr}/{len_matched_results}: {rnd(matched_itr/len_matched_results)}")

							#Safe grabber from the first lyst
							def get_from_lyst_two(attribute):
								if hasattr(matched_data, attribute):
									return getattr(matched_data, attribute)
								else:
									return np.NaN

							temp_dyct = {} #Zipping the results together, i.e. if the current vuln has information keep them, otherwise grab the metric values
							for col in data_types.keys():
								ut.zypped_val = ut.zyp(get_from_lyst_one(col),get_from_lyst_two(col))
								temp_dyct[col] = ut.zypped_val if col != "Line" else ut.to_int(ut.zypped_val,return_val = np.NaN)

							#If the current item is an identified vulnerability
							if bool(temp_dyct['IsVuln']):
								#Checking the True/False Positives and Negatives
								if vulns is not None:
									if vulns(temp_dyct['qual_name'].replace('.py','').replace('/','.') + ":" + str(temp_dyct['Line']),temp_dyct['cryptolationID']):
										temp_dyct['TP'] = 1
										temp_dyct['TN'] = 0
									else:
										temp_dyct['TP'] = 0
										temp_dyct['TN'] = 1
								else:
									temp_dyct['TP'] = 0
									temp_dyct['TN'] = 0


								#Adding the source code around the identified vulnerability
								temp_dyct['tool_name'] = name
								temp_dyct['context'] = ut.retrieve_context(
									str(temp_dyct['qual_name']).replace('.','/',(str(temp_dyct['qual_name']).count(".")-1)),
									temp_dyct['Line'] - (1 if app.name("bandit") else 0)
								,retrieve_context)
							else:
								temp_dyct['TP'] = 0
								temp_dyct['TN'] = 0

							#Setting the False Metrics
							temp_dyct['FP'] = 0
							temp_dyct['FN'] = 0

							#Tacking the current dataset into the appending list, appends onto the overall container
							append += [
								pd.DataFrame(
									[temp_dyct],columns=data_types.keys()
								)
							]

					else:
						#Setting up the base information as more of a True Negative or a Metric dataset
						temp_dyct = {}
						for col in data_types.keys():
							temp_dyct[col] = get_from_lyst_one(col)

						temp_dyct['tool_name'] = name

						if bool(temp_dyct['IsVuln']):
							if vulns is not None:
								if vulns(temp_dyct['qual_name'].replace('.py','').replace('/','.') + ":" + str(temp_dyct['Line']),temp_dyct['cryptolationID']):
									temp_dyct['TP'] = 1
									temp_dyct['TN'] = 0
								else:
									temp_dyct['TP'] = 0
									temp_dyct['TN'] = 1
							else:
								temp_dyct['TP'] = 0
								temp_dyct['TN'] = 0

						else:
							temp_dyct['TP'] = 0
							temp_dyct['TN'] = 0

						temp_dyct['FP'] = 0
						temp_dyct['FN'] = 0

						#Tacking the current dataset into the appending list, appends onto the overall container
						append += [
							pd.DataFrame(
								[temp_dyct],columns=data_types.keys()
							)
						]


				if app in scanners:
					if True:
						disp(f"Determine any extra or undertermined values")
					if vulns is not None:
						#Iterating through undiscovered or extra discovered vulnerabilites
						for vul_set in vulns.core:

							len_vul_set = len(vul_set['items'])
							if extra_logging:
								disp(f"There are {len_vul_set} {vul_set['name']} alerts, setting it as {'FP' if bool(vul_set['FP']) else 'FN'}")

							for vuln_itr, vuln in enumerate(vul_set['items']):
								if extra_logging:
									disp(f"Examining the {vul_set['name']} row {vuln_itr}/{len_vul_set}: {rnd(vuln_itr/len_vul_set)}")

								#Prepping the qual_name to a more real value
								file_name, line = vuln['location'].split(":")
								file_name = file_name.replace('.','/') + ".py"

								#Tacking the current dataset into the appending list, appends onto the overall container
								append += [
									pd.DataFrame(
										[gen(
											projectname = proj_name,
											qual_name = file_name,
											tool_name = app.name(),
											IsVuln = 1,
											Name = ut.to_int(vuln['rule'],return_self=True),
											cryptolationID = ut.to_int(vuln['rule'],return_self=True),
											Message = f"{vul_set['name']} issue with rule {vuln['rule']}",
											Line = ut.to_int(line,return_self=True),
											context = ut.retrieve_context(
												file_name,
												line
											,retrieve_context),
											TP = 0,
											TN = 0,
											FP = ut.to_int(vul_set['FP'],return_self=True),
											FN = ut.to_int(vul_set['FN'],return_self=True),
											METRIC_FILE = lyst_one[(lyst_one['qual_name'] == file_name) & (lyst_one['tool_name'] == metrics_name)]
										)],columns=data_types.keys()
									)
								]

			except Exception as e:
				disp_msg(f"Exception :> {e}")
				now = timr.now()
				scanningExceptions = scanningExceptions.append(
					pd.DataFrame(
						[{
							"Time": now.strftime('%Y-%m-%dT%H:%M:%S') + ('.%04d' % (now.microsecond / 10000)),
							"App": f"{name}",
							"Proj": f"{proj_name}",
							"Exception": f"{e}"
						}],
						columns = ["Time","App","Proj","Exception"]
					)
				)
				pass

			#Deleting the url and information
			if cloned and os.path.exists(proj_name):
				exey(f"yes|rm -r {proj_name}")
				disp_msg(f"Waiting between scanning projects to ensure GitHub Doesn't get angry")
				wait_for(5)

	disp(f"Setting the dataframe types")
	#Setting the dataframe
	if app_itr > 0 and app in metrics:
		overallContainer = settypes(pd.DataFrame(
			columns = data_types.keys()
		))

	disp_msg(f"Appending all of the results onto the overall container")
	#Appending all of the information
	for appending_itr,appending in enumerate(append):
		overallContainer = overallContainer.append(appending,ignore_index=False)
	overallContainer = settypes(overallContainer)
disp_msg(f"Done Scanning with Everything")