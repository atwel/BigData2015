""" Networks Lab for Social Dynamics package

It also uses the awesome open-source libraries that are IPython, Pandas, NetworkX and Matplotlib.

It is designed to be run using an IPython notebook (version 1.1.0 and greater) and therefore implements 
the database using Pandas which has been integrated into the Notebooks platform. 

Development of this lab was supported with a curriculum development grant from the Department of Sociology
at the University of Michigan.

"""

import pandas as pd
import networkx as nx
import random
import IPython as ip
import math
import urllib2




class Graph(object):
	""" This is the only class unique to the module. It holds key variables
	and other objects (like the facebook connection and the pandas 
	database. The name parameter is so that multiple databases and
	networks can be worked on simultaneously.
	"""

	def __init__(self, name="data1"):
		""" This initializing function mostly creates fields to be filled
		in later. It could fill everything in but that is saved so that the
		lab user can get a better feel for what it going on.
		"""

		# Basic objects
		self.graph_name = name
		self.friend_db = False
		self.my_ID = False
		self.mynet = nx.Graph()
		self.contexts_list = {}
		self.defined_colors = []
		self.me = False
		self.old_positions=[]



	def random_sample(self,count=200):
		""" Creating a random sampling of the whole network to make
		adding personal knowledge more tractable. The only way this
		can be undone is to reload your data from Facebook.
		"""
 
		total = len(list(self.friend_db.columns.values))
		for sap in random.sample(list(self.friend_db.columns.values),(total-count)):
			if sap != self.my_ID:
				del self.friend_db[int(sap)]
				self.mynet.remove_node(int(sap))

		print ("Your network now has a random subset of "
			+str(count)+" nodes from your whole network")


	def define_colors(self, attribute, dictionary):
		""" This method allows the user to color friends' nodes
		based on the given attribute.
		"""

		self.defined_colors = []
		my_dict = {}

		# Letting the user pick the colors
		for i in dictionary.keys():
			my_dict[i] = raw_input("\nWhat color should nodes be"
				+"for people with value " + str(dictionary[i])+"?")
			clear_screen()

		# creating a list with the appropriate colors 
		for person in self.mynet.nodes():
			if person == self.my_ID:
				self.defined_colors.append("blue")
			else:
				key = self.friend_db[person][attribute]
			try:
				self.defined_colors.append(my_dict[key])
			except:
				self.defined_colors.append("white")


	def count_components(self, withme=False):
		""" This method returns the number of components in
		the network without the ego.It does this by removing 
		the ego in a copy of the network."""

		if withme:
			print ("If you're in the network, it"
				+" has to have a single component!")
		else:
			bu = nx.Graph()
			bu.add_nodes_from(self.mynet.nodes())
			bu.add_edges_from(self.mynet.edges())
			bu.remove_node(self.my_ID)
			print ("Your network has "
				+ str(nx.number_connected_components(bu)) 
				+" components")

	def density(self):
		return nx.density(self.mynet)

	def draw_network(self,file_name="Network_visualization.html",
		colors=[], strong=False, weight=False, withme=False):
		""" This function writes the network to an html file 
		so that users can explore the network move thoroughly.
		"""
		base_file = open("D3JS.html", "r")
		my_file = open(file_name, "w")
		for line in base_file:
			my_file.write(line)
			if "var nodes=[" in line:
				if not withme:
					strong=False
					if colors == []:
						colors = self.defined_colors
						if colors != []:
							backup_colors = {}
							nodes = list(self.mynet.nodes())
							for i in range(len(nodes)):
								backup_colors[nodes[i]]=self.defined_colors[i]
							index = list(self.mynet.nodes()
								).index(self.my_ID)
							self.defined_colors.pop(index)
						else:
							backup_colors = []
					else:
						backup_colors = {}
						nodes = list(self.mynet.nodes())
						for i in range(len(nodes)):
							backup_colors[nodes[i]] = self.defined_colors[i]
						index = list(self.mynet.nodes()).index(self.my_ID)
						self.defined_colors.pop(index)

					backup_net = nx.Graph(self.mynet)
					self.mynet.remove_node(self.my_ID)


				# This defaults the coloring scheme to what the user has
				# previously defined (if anything) if no color 
				# argument is passed in
				if colors == []:
					colors = list(self.defined_colors)
					if colors == []:
						for i in self.mynet.nodes():
							if i == self.my_ID:
								colors.append("blue")   
							else:
								colors.append("aqua")


				# A dictionary for renumbering the node ids
				rewrite = {}
				# also for the renumbering operation. 
				count = 0
				# We use the count of mutual friends as data 
				mutuals = {}
				# We use the member list from the network instead
				# of the database because it colors nodes in the order 
				# of this list and the imported color list is in that order
				nodes = self.mynet.nodes()

				# In both the loop for nodes and links, we do n-1
				# first and the last one manually because of the
				# the need to insert the right characters for
				# the .json format.
				giant_string = "\n"
				for j in range(len(nodes)):
					# i is the usual id number
					i = nodes[j]  
					# renumbering business
					rewrite[i]=count 
					# A Pandas series object is just like a
					# python dictionary, but isn't...Cast it!
					my_dct = dict(self.friend_db[int(i)]) 

					mutuals[i]=len(my_dct["mutuals"])
						
					# The next 3 lines create the bulk of the text
					giant_string += ("{\"color\":" + "\""
						+str(colors[count])+ "\"" + ",\"id\":"+"\""
						+str(rewrite[i]) + "\"" + ",\"name\":"+"\""
						+str(my_dct["name"]) + "\"" +",\"value\":"
						+str(mutuals[i]) + ", \"desc\":\"Name:"
						+str(my_dct["name"]) + "<br>Known from:"
						+str(my_dct["known from"]) + "<br>Gender:"
						+str(my_dct["gender"]) + "<br>Race:\"},\n")

					count +=1

				my_file.write(giant_string[:-2]+"];\n")

			# Part 2: adding the edges       
			if "var links=[" in line:

				count = 0
				edges = self.mynet.edges()

				giant_string = "\n"
				for i in range(len(edges)):
					j = edges[i] # this is a tuple of source and target pairs
					giant_string += ("{\"source\":"
						+str(rewrite[j[0]])+", \"target\":"
						+str(rewrite[j[1]])+", \"n1\":\""
						+str(self.friend_db[j[0]]["name"])
						+"\", \"n2\":\""
						+str(self.friend_db[j[1]]["name"])+"\"")


					if strong:
						try:
							strg = self.mynet[j[0]][j[1]]["strong"]
							if not (strg==strg) or strg==-1:
								giant_string +=",\"strong\":"+str(0)
							else:
								giant_string +=",\"strong\":"+str(strg)
						except:
							giant_string +=",\"strong\":"+str(0)
					else:
						giant_string +=",\"strong\":"+str(0)

					giant_string+="},\n"

					count +=1
				my_file.write(giant_string[:-2]+"];\n")

		my_file.close()
		base_file.close()

		#restoring the full network
		if not withme:
			self.mynet = nx.Graph(backup_net)
			if backup_colors == []:
				self.defined_colors = []
			else:
				clrs = []
				for i in self.mynet.nodes():
					clrs.append(backup_colors[i])
  				self.defined_colors = clrs


	def load_data(self,file_name="1"):
		""" This method loads existing data into a graph object.
		"""

		self.contexts_list = {}

		# Loading in data other than the Database    
		other = open("./"+str(file_name)+"_general_data.csv", "r+")
		for line in other:
			data = line.strip().split(";")
			if data[0] == "my_ID":
				if data[1] == 'False':
					self.my_ID = -1
				else:
					self.my_ID = int(data[1])
					self.mynet.add_node(self.my_ID)
			if data[0] == "contexts_list":
				self.contexts_list = {}
				if data[1] != "":
					new_data = data[1].split(",")
					for i in new_data:
						if i != "":
							j = i.split(":")
							self.contexts_list[int(j[0])] = j[1]
			if data[0] == "defined_colors":
				self.defined_colors = [i for i in data[1].split(",")]


		# loading in the database          
		self.friend_db = pd.read_csv("./"+str(file_name)
			+"_friend_data.csv", header=0, index_col=0)    
		new_names = []
		for i in list(self.friend_db.columns.values):
			new_names.append(int(i))
			if self.my_ID != i:
				# adding network ties
				self.mynet.add_node(int(i))
				self.mynet.add_edge(int(i), self.my_ID)

		self.friend_db.columns = new_names

		attrs=list(self.friend_db.index.values)

		# adding the mutual ties connections 
		#and converting to ints from strings)
		for i in list(self.friend_db.columns.values):

			q = self.friend_db[int(i)]["known from"]
			if q==q:
				self.friend_db[int(i)]["known from"] = int(q)

			r = self.friend_db[int(i)][attrs[6]]
			if r==r:
				self.friend_db[int(i)][attrs[6]] = int(r)

			p = self.friend_db[int(i)][attrs[7]]
			if p==p:
				self.friend_db[int(i)][attrs[7]] = int(p)
				
			s = self.friend_db[int(i)][attrs[8]]
			if s==s:
				self.friend_db[int(i)][attrs[8]] = int(s)

			if type(self.friend_db[int(i)]["mutuals"]) == str:
				mut_str = self.friend_db[int(i)]["mutuals"][1:-1].split(",")
				mutuals = []
				for j in mut_str:
					try:
						mutuals.append(int(j))
					except:
						if j != "":
							mutuals.append(long(j))
						else:
							pass

			self.friend_db[int(i)]["mutuals"] = mutuals
			for j in mutuals:
				if int(j) in new_names:
					try:
						edge = self.mynet[int(j)][int(i)]
					except:
						self.mynet.add_edge(int(j), int(i))

			val = self.friend_db[int(i)]["strong tie"]
			if val != "" and (val==val):
				self.mynet[int(i)][self.my_ID]["strong"] = int(val)

		for edge in self.mynet.edges():
			try:
				self.mynet[int(edge[0])][int(edge[1])]["strong"]
			except:
				self.mynet[int(edge[0])][int(edge[1])]["strong"]=0
		
		bu = nx.Graph()
		bu.add_nodes_from(self.mynet.nodes())
		bu.add_edges_from(self.mynet.edges())
		bu.remove_node(self.my_ID)
		for n in bu.nodes():
			if nx.is_isolate(bu, n):
				bu.remove_node(n)  
		self.no_ego_net = bu

		print "Data successfully loaded"


	def avg_path_length(self, withme=False):
		if withme:
			return nx.average_shortest_path_length(self.mynet)
		else:
			return nx.average_shortest_path_length(self.no_ego_net)


	def diameter(self, withme=False):

		if withme:
			print "If you're in the network, it has to be diameter 2"
		else:
			print "Your network has a diameter of "+ str(nx.diameter(self.no_ego_net))


	def degree_centrality(self, withme=True, node=None, average=False):

		if node==None:
			if withme:
				my_dict = nx.degree_centrality(self.mynet)
				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]
				if average:
					return sum(new)/float(len(new))
				else:
					return new
	 		else:
				my_dict = nx.degree_centrality(self.no_ego_net)

				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]
				if average:
					return sum(new)/float(len(new))
				else:
					return new
				return new
	
		else:
			if withme:
				my_dict = nx.degree_centrality(self.mynet)
				try:
					return my_dict[node]
				except:
					try:
						return my_dict [self.name_to_id(node)]
					except:
						print "Invalid node name"
			else:
				my_dict = nx.degree_centrality(self.no_ego_net)
				try:
					return my_dict[node]
				except:
					try:
						return my_dict[self.name_to_id(node)]
					except:
						print "Invalid node name"


	def betweenness_centrality(self, withme=False, node=None,average=False):
		if node==None:
			if withme:
				my_dict = nx.betweenness_centrality(self.mynet)
				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]
				if average:
					return sum(new)/float(len(new))
				else:
					return new
			else:
				my_dict = nx.betweenness_centrality(self.no_ego_net)

				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]
				if average:
					return sum(new)/float(len(new))
				else:
					return new

		else:
			if withme:
				my_dict = nx.betweenness_centrality(self.mynet)
				try:
					return my_dict[node]
				except:
					try:
						return my_dict[self.name_to_id(node)]
					except:
						print "Invalid node name"
			else:
				my_dict = nx.betweenness_centrality(self.no_ego_net)
				try:
					return my_dict[node]
				except:
					try:
						return my_dict[self.name_to_id(node)]
					except:
						print "Invalid node name"


	def closeness_centrality(self, withme=False, node=None, average=False):
		if node==None:
			if withme:
				my_dict = nx.closeness_centrality(self.mynet)
				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]
				if average:
					return sum(new)/float(len(new))
				else:
					return new
			else:
				my_dict = nx.closeness_centrality(self.no_ego_net)

				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]
				if average:
					return sum(new)/float(len(new))
				else:
					return new
		else:
			if withme:
				my_dict = nx.closeness_centrality(self.mynet)
				try:
					return my_dict[node]
				except:
					try:
						return my_dict[self.name_to_id(node)]
					except:
						print "Invalid node name"
			else:
				my_dict = nx.closeness_centrality(self.no_ego_net)
				try:
					return my_dict[node]
				except:
					try:
						return my_dict[self.name_to_id(node)]
					except:
						print "Invalid node name"

	def eigenvector_centrality(self, iterations, withme=False, node=None):
		my_dict = nx.eigenvector_centrality(self.mynet,
			max_iter = iterations)

		if node==None:
			if withme:
				my_dict =nx.eigenvector_centrality(self.mynet,
					max_iter = iterations)
				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]
				return new
			else:
				bu = nx.Graph()
				bu.add_nodes_from(self.mynet.nodes())
				bu.add_edges_from(self.mynet.edges())
				bu.remove_node(self.my_ID)
				my_dict = nx.eigenvector_centrality(bu,
					max_iter = iterations)

				new = {}
				for i in my_dict:
					new[self.id_to_name(i)] = my_dict[i]

				return new

		else:
			try:
				my_dict = nx.eigenvector_centrality(self.mynet,
					max_iter = iterations)
				return my_dict[node]
			except:
				try:
					return my_dict[self.name_to_id(node)]
				except:
					print "Invalid node name"


	def degree(self, node):
		try:
			return self.mynet.degree(node)
		except:
			print "Invalid node name."


	def average_degree(self, withme=False):
		if withme:
			vals = list(self.mynet.degree(self.mynet.nodes()).values())
			return sum(vals)/float(len(vals))
		else:
			vals = list(self.mynet.degree(self.no_ego_net.nodes()).values())
			return sum(vals)/float(len(vals))
			


	def clustering(self, group=0):
		""" This method calculates the clustering coefficients for the
		specified group (context number). The default group is the whole
		network minus the ego because it skews everything so much.
		"""

		node_list = []
		if group==-1:
			for i in self.mynet.nodes():
				if i != self.my_ID:
					node_list.append(i)
		elif group==0: 
			node_list = self.mynet.nodes()
		else:
			for i in self.mynet.nodes():
				if self.friend_db[int(i)]["known from"] == group:
					node_list.append(i)

		clustering = nx.clustering(self.mynet, node_list)

		try:
			g_name = self.contexts_list[group]
		except:
			if group == -1:
				g_name = "Whole Graph (without you)"
			if group == 0:
				g_name = "Whole Graph"

		print "Clustering coefficient for people in the group " + g_name

		return clustering


	def clustering_by_attribute_summary(self, attribute):
		""" This allows the user to group people by an attribute
		and look at clustering within those categories.
		"""
		if attribute == "mutuals" or attribute == "id":
			print "Sorry, "+attribute+ " is not a sortable attribute"
		else:    
			node_dict = {}
			for i in list(self.friend_db.columns.values):
				val  = self.friend_db[int(i)][attribute]
				try:
					node_dict[val].append(int(i))
				except:
					node_dict[val] = [int(i)]

			cluster_dict = {}
			for i in node_dict:
				nodes = node_dict[i]
				cluster_coef = nx.clustering(self.mynet, nodes)
				rewrite = {}
				for r in cluster_coef:
					rewrite[self.id_to_name(r)] = cluster_coef[r]
				cluster_dict[i] = cluster_coef
				tot = sum(rewrite.values())/float(len(rewrite.values()))
				print ("Average clustering coef. for friends with attribute value "
					+str(i)+" is: "+ str(tot))

			return cluster_dict      


	def clustering_by_attribute(self, attribute):
		""" This allows the user to group people by an attribute 
		and look at clustering within those categories.
		"""
		if attribute == "mutuals" or attribute == "id":
			print "Sorry, "+attribute+ " is not a sortable attribute"
		else:    
			node_dict = {}
			for i in list(self.friend_db.columns.values):
				val  = self.friend_db[int(i)][attribute]
				try:
					node_dict[val].append(int(i))
				except:
					node_dict[val] = [int(i)]

			cluster_dict = {}
			for i in node_dict:
				nodes = node_dict[i]
				cluster_coef = nx.clustering(self.mynet, nodes)
				rewrite = {}
				for r in cluster_coef:
					rewrite[self.id_to_name(r)] = cluster_coef[r]
				cluster_dict[i] = cluster_coef
				print ("Clustering coef. for friends with attribute value "
					+str(i)+" is: "+ str(rewrite))

			return cluster_dict


	def associativity_by_attribute(self, attribute):
		""" This allows the user to see the probability of alters
		sharing at attribute.
		"""

		if attribute =="id" or attribute =="mutuals":
			print "Sorry, "+ attribute+ " is not a sortable attribute."

		else:
			trans_dict = {}
			for i in list(self.friend_db.columns.values):
				val = self.friend_db[i][attribute]
				mutuals = list(self.friend_db[i]["mutuals"])
				hit = 0
				total = 0
				for j in mutuals:
					if self.friend_db[int(j)][attribute] == val:
						hit +=1
					total +=1
				if (i != self.my_ID):
					if (self.friend_db[self.my_ID][attribute] == val):
						hit +=1
					total += 1

				if total != 0:
					coef = hit/float(total)
				else:
					coef = 0

				try:
					trans_dict[val].append(coef)
				except:
					trans_dict[val] = [coef]

			avg_dict = {}
			for i in trans_dict:
				val = trans_dict[i]
				avg = sum(val)/float(len(val))
				avg_dict[i] = avg
				print "Associativity avg for people with value "+str(i) + " is: " +str(avg)

			return avg_dict
                
                     
	def get_average_clustering(self, a_dictionary):
		""" This method accepts a dictionary or a dictionary of 
		dictionaries and finds the average values sorted by keys.
		"""
        
		try:
			for i in a_dictionary:
				my_list = []
				sub_dict = a_dictionary[i]
				for j in sub_dict:
					my_list.append(sub_dict[j])
				avg= sum(my_list)/float(len(my_list))
				print ("Avg. clustering for attribute value "
					+str(i)+ " is " +str(avg))
            
		except:
			my_list = []
			for i in a_dictionary:
				my_list.append(a_dictionary[i])
			avg = sum(my_list)/float(len(my_list))  
		print "Average clustering for group is "+str(avg)

 
	def attribute_by_attribute(self, attribute_one, 
		group_number, attribute_two):
		""" This method allows the user to see the prevalences of a 
		particular attribute within a group. This is no doubt a way to do
		this using Pandas functionality, but that is for a later iteration.
		"""

		indices = list(self.friend_db.index.values)
		if (attribute_one not in indices or attribute_two not in indices):
			print "Invalid inputs. Make sure the dictionary and spelling are correct."

		else:
			vals = {}
			count = 0
			for i in list(self.friend_db.columns.values):
				if (self.friend_db[i][str(attribute_one)] == group_number):
					which = self.friend_db[i][str(attribute_two)]
					try:
						vals[which] += 1
						count +=1
					except:
						vals[which] = 1
						count +=1

			print "For friends in group "+str(group_number)+" for attribute "+str(attribute_one)+","
			print "they breakdown into the following percentages for attribute "+str(attribute_two)
			print "(Sample size = "+str(count)+")"

			for j in vals:
				try:
					number = vals[j]/float(count)    
				except:
					number = 0

				print str(j)+" : "+str(number)


	def attribute_breakdown(self, attribute):
		""" This method finds the percentage within categories of an attribute"""

		if attribute not in list(self.friend_db.index.values):
			print "Not a valid attribute"

		vals = {}
		count = 0
		for i in list(self.friend_db.columns.values):
			which = self.friend_db[i][str(attribute)]
			try:
				vals[which] += 1
				count +=1
			except:
				vals[which] = 1
				count +=1

		print "Your friend breakdown into the following percentages for attribute "+str(attribute)
		print "(Sample size = "+str(count)+")"
            
		for j in vals:
			try:
				number = vals[j]/float(count)    
			except:
				number = 0

			print str(j)+" : "+str(number)
			
	def ids_to_names(self):
		""" Returns a dictionary links IDs to names. """
		my_dict = {}
		for i in list(self.friend_db.columns.values):
			my_dict[int(i)] = self.friend_db[int(i)]["name"]
		return my_dict
        
     
     	def name_to_id(self, name):
     		"""Returns the ID number associated with the name ."""

		for id in self.friend_db:
			name1 = str(self.friend_db[int(id)]["name"])
			if name1 == name:
				return id
			print "Not a valid name"


	def id_to_name(self, id):
		"""Returns the name associated with the ID number."""
		try:
			name = str(self.friend_db[int(id)]["name"])
			return name
		except:
			print "Not a valid ID"
			return id
    
    

        
        



	def ids_to_names(self):
		""" Returns a dictionary links IDs to names. """
		my_dict = {}
		for i in list(self.friend_db.columns.values):
			my_dict[int(i)] = self.friend_db[int(i)]["name"]
        
		return my_dict


	def view_mutual_friends(self, name):
		""" This allows the user to see mutual friends of the specified friend """
		id_ = 0
		for i in list(self.friend_db.columns.values):
			if self.friend_db[i]["name"] == str(name):
				id_ = i
		if id_ == 0:
			print "Name not found. Please try again."
		else:
			print "You have the follow mutual friends:"
			mutuals = self.friend_db[id]["mutuals"]
			for i in mutuals:
				print self.friend_db[i]["name"]

  
	def view_friend_info(self, name):
		""" This allows the user to see a friend's attributes """
		id_ = 0
		for i in list(self.friend_db.columns.values):
			if self.friend_db[i]["name"] == str(name):
				id_ = i
		if id_ == 0:
			print "Name not found. Please try again."
		else:
			print "ID#: "+str(id)
			for attr in list(self.friend_db.index.values):
				print str(attr) + ": "+ str(self.friend_db[id][attr])


		def view_people_from(self, group):
			"""This method allows the user to see who the user knows
			from the various social contexts.
			"""

			if group not in self.contexts_list:
				print "Incorrect group name"
			else:
				my_list = []
				for i in self.friend_db.columns.values:
					if self.friend_db[i]["known from"] == group:
						my_list.append(self.friend_db[i]["name"])
				print ("You have included the following people in the" 
					+" group named "+str(self.contexts_list[group])+":")
				for i in my_list:
					print i


	def test_Strong_Triadic_Closure(self):
		""" This method has the user test the principle of strong 
		triadic closure; there is a good chance that friends with
		whom the ego has strong ties are also friends. This 
		algorithm will not work if the user hasn't already defined
		which ties are strong.
		"""
		comps = []
		edges = nx.get_edge_attributes(self.mynet, "strong")
		if edges != {}:
			for e in edges:
				if edges[e] == 1:
					comps.append(e)
			hit = []
			for i in comps:
				for j in comps:
					if i!=j:
						for k in i:
							if k != self.my_ID:
								notme1 = k
						for l in j:
							if l != self.my_ID:
								notme2 = l
						try:    
							self.mynet[notme1][notme2]
							hit.append(1)
						except:
							hit.append(0)

			try:
				val = sum(hit)/float(len(hit))
			except:
				val = 0
			print "Count of triads inspected: "+str(len(hit))
			print val
		else:
			print ("ERROR: You must first enter information about"
				+" strong ties [Command define_strong_ties()].")


	def test_Strong_Triadic_Closure_within_group(self, group):
		""" This method has the user test the principle of strong
		triadic closure within groups; there is a good chance that
		friends with whom the ego has strong ties are also friends
		(within groups). This algorithm will not work if the user
		hasn't already defined which ties are strong. The group
		value is the one associated with social contexts.
		"""

		comps = []
		edges = nx.get_edge_attributes(self.mynet, "strong")
		if edges != {}:
			for e in edges:
				if edges[e] == 1 and (self.friend_db[e[0]]["known from"]
					==group or self.friend_db[e[1]]["known from"]==group):
					# check above makes sure they're in the right group
					comps.append(e)

			hit = []
			for i in comps:
				for j in comps:
					if i!=j:
						for k in i:
							if k != self.my_ID:
								notme1 = k
						for l in j:
							if l != self.my_ID:
								notme2 = l
						try:    
							self.mynet[notme1][notme2]
							hit.append(1)
						except:
							hit.append(0)

 			try:
				val = sum(hit)/float(len(hit))
			except:
				val = 0
			print "Count of triads inspected: "+str(len(hit))
			print val
		else:
			print ("ERROR: You must first enter information"
				+ " about your tie strengths.")


def download_files():
	"""A utility function to make it easier to get all the files 
	for the lab into the Wakari file system. There might be
	a better way to do this, but it isn't clear in the Wakari docs.
	"""
	stem = "https://raw.githubusercontent.com/atwel/BigData2015/master/"
	for f_name in range(1,6):
		for end in ["_friend_data.csv","_general_data.csv"]:
			name = str(f_name) +end
			file_=urllib2.urlopen(stem+name)
			new_file = open(name, "wb")
			for line in file_:
				new_file.write(line)
			new_file.close()
	name = "network_drawing.html"
	f = open(name,"wb")
	for line in urllib2.urlopen(stem+name):
		f.write(line)
	f.close()
