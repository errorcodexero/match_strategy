#!/usr/bin/env python

from glob import glob
#from common_utils.util import print_lines

def print_lines(x):
	for a in x: print a

def pairs_to_map(x):
	r={}
	for (a,b) in x: r[a]=b
	return r

#str->[[str]]
def parse_file(filename):
	l=file(filename).read().splitlines()
	def split_line(s):
		return s.split(';')
	sp=map(split_line,l)

	types={
		'team':int,
		'auto Boulders Low':float,
		'auto Boulders High':float,
		'teleop Boulders Low':float,
		'teleop Boulders High':float,
		'best event':str
		}

	def parse_item((name,value)):
		if types.has_key(name):
			return name,types[name](value)
		if value=='': return name,0
		try:
			return name,float(value)
		except:
			print name,"\"%s\""%value
			raise

	if sp[0][0]=='team':
		event_name='championship preview'
		event_code=None
		labels=sp[0]
		data_area=sp[1:]
	else:
		event_name=sp[0][0]
		event_code=sp[0][1]
		labels=sp[2]
		data_area=sp[3:]

	data=[]
	for x in data_area:
		data.append(pairs_to_map(map(parse_item,zip(
			labels,
			x
			))))
	return {
		'event_name':event_name,
		'event_code':event_code,
		'data':data
		}

if __name__=='__main__':
	files=glob("data/*.csv")
	#print_lines(files)
	#f=files[0]
	f='data/4536_scouting_database_1.7.PNWDistrictChampionship.csv'
	#f='data/4536_scouting_database_1.7.championship preview.csv'
	p=parse_file(f)
	#print_lines(p['data'])

	tower_strengths=map(lambda x: (x['subtracted tower strength'],x['team']),p['data'])
	#print_lines(sorted(tower_strengths))

	residuals=[]
	import random
	import math

	robots=2
	sample_size=10000
	for i in range(sample_size):
		#choose two random teams
		sm=random.sample(set(tower_strengths),robots)
		residual=10-sm[0][0]-sm[1][0]
		residuals.append(residual)
	#print_lines(residuals)
	def bin(residuals):
		boxed={}
		for x in residuals:
			r=math.ceil(x)
			if not boxed.has_key(r): boxed[r]=0
			boxed[r]+=1
		#print boxed
		for k in range(int(min(boxed)),int(max(boxed)+1)):
			def get():
				if boxed.has_key(k): return boxed[k]
				return 0
			print k,'\t',get()
		print 'odds:',float(len(filter(lambda x: x<=0,residuals)))/len(residuals)
	print 'Tower strength remaining'
	bin(residuals)

	def_crosses=map(lambda x: x['cross defense count'],p['data'])
	def_residuals=[]
	for i in range(sample_size):
		sm=random.sample(set(def_crosses),robots)
		residual=8-sum(sm)
		def_residuals.append(residual)
	print 'Defenses left to breach'
	bin(def_residuals)

	pts=map(lambda x: x['total Points'],p['data'])
	pts_residuals=[]
	for i in range(sample_size):
		a1=random.sample(set(pts),robots)
		a2=random.sample(set(pts),3)
		residual=sum(a2)-sum(a1)
		pts_residuals.append(residual)
	print 'Points to score'
	bin(pts_residuals)
