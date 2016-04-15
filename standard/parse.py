#!/usr/bin/env python

import sys

#28.33
#6.71

def mean(a): return (0.0+sum(a))/len(a)

#any(a),any(b) => [(a,b)]->(a->b)
def pairs_to_map(a):
	r={}
	for k,v in a:
		r[k]=v
	return r

def firsts(a):
	return map(lambda x:x[0],a)

def seconds(a):
	return map(lambda x:x[1],a)

def transpose(a):
	width=max(map(len,a))
	r=[]
	for i in range(width): r.append([])
	for i in range(width):
		for elem in a:
			r[i].append(elem[i])
	#print 'r:',r
	#for i,elem in enumerate(a):
	#	print i
	#	r[i].append(elem)
	return r

def parse_csv(filename):
	m=map(lambda x: x.split(','),file(filename).read().splitlines())

	#for original version:
	#labels=m[2]
	#data=m[3:]

	#for 2nd version after CV talking with Luke
	labels=m[0]
	data=m[1:]

	#Ignore the lines that don't start with a match # so that ignore second table that's down below in newer version
	data=filter(lambda x: x[0]!='',data)

	#print 'labels:',labels

	info=map(lambda x: pairs_to_map(zip(labels,x)),data)
	return info

defense_types=['Portcullis', 'Cheval', 'Moat', 'Ramparts', 'Drawbridge', 'Sally Port', 'Rock Wall', 'Rough Terrain', 'Low Bar']

#str->int
def int1(x):
	if x=='': return 0
	return int(x)

#any(a),any(b) => (a->b) -> [b]
def values(m):
	r=[]
	for key in m:
		r.append(m[key])
	return r

#int->(float(ball time),float(defense time),bool(challenge),bool(climb),(str->float)(defenses crossed per match))
def alternate_data_source(team_number):
	#This uses data from the 'baseline' directory to serve its purposes

	#rr=(balls_per_match,def_per_match,(climb_per_match+challenge_per_match)>.5,climb_per_match>.5,defense_averages)
	def parse_line(s):
		sp=s.split()
		return int(sp[0]),float(sp[1]),float(sp[2])
	data=map(parse_line,file('../baseline/out.txt').read().splitlines())
	f=filter(lambda x: x[0]==team_number,data)
	assert len(f)<=1
	if len(f)==0:
		print 'Error: Non-existant team: %d'%team_number
		sys.exit(1)

	assert len(f)==1
	def_per_match=f[0][1]
	balls_per_match=f[0][2]
	climb_or_challenge=1 #If have no idea, assume that can challenge
	climb=0

	def1=parse_csv('video_data.csv')
	def process_line(s):
		team=int(s['Team'])
		r={}
		def get_name(d):
			if d=='Cheval': return 'Cheval-de-frise'
			if d=='Ramparts': return 'Rampart'
			return d
		for d in defense_types:
			found=s['Pre-Event '+get_name(d)]
			#print found
			r[d]=int1(found)

		#If all -1 that means no data available, so put in None
		v=set(values(r))
		if list(v)==[-1]:
			r=None

		return team,r
	def_info=pairs_to_map(map(process_line,def1))

	def defense_averages():
		if def_info.has_key(team_number):
			d1=def_info[team_number]
			if d1: return d1
		return pairs_to_map(map(lambda x: (x,0),defense_types))

	print '%d:'%team_number,'Using alternate data source',f[0]

	#todo: deduplicate next line
	game_length=2*60+15

	times=game_length/max(1,(balls_per_match+def_per_match))
	
	return (times,times,climb_or_challenge,climb,defense_averages())

#str->int->(float(ball time),float(defense time),bool(challenge),bool(climb),(str->float)(defenses crossed per match))
def run(filename,team_number):
	info=parse_csv(filename)

	#If there is no scouter recorded, assume the rest of the columns are junk!
	#info=filter(lambda x: x['Scouter'],info)

	#basic teleop ones, anyway
	#cross_columns=['Portcullis Teleop Crossings', 'Cheval Teleop Crossings', 'Moat Teleop Crossings', 'Ramparts Teleop Crossings', 'Drawbridge Teleop Crossings', 'Sally Port Teleop Crossings', 'Rock Wall Teleop Crossings', 'Rough Terrain Teleop Crossings', 'Low Bar Teleop Crossings']

	auto_crossings=map(lambda a: '%s Auto Crossings'%a,defense_types)
	#teleop_unscored=map(lambda a: '%s Unscored Crossings'%a,defense_types)
	teleop_unscored=map(lambda a: '%s Teleop Crossings'%a,defense_types)
	#teleop_scored=map(lambda a: '%s Scored Crossings'%a,defense_types)
	def teleop_scored_name(s):
		if s=='Moat': return 'Moat Scored Crosings'
		return '%s Scored Crossings'%s
	teleop_scored=map(teleop_scored_name,defense_types)
	teleop_crossings=teleop_unscored+teleop_scored
	cross_columns=auto_crossings+teleop_unscored+teleop_scored

	def int_or_none(x):
		if x=='': return None
		return int(x)

	data_types={
		'Team':int_or_none,
		'Teleop High Goals':int1,
		'Teleop Low Goals':int1,
		'Climb Flag':bool,
		'Challenge Flag':bool,
		'Auto High Goals':int1,
		'Auto Low Goals':int1,
		'Low Bar Available':int
		}

	for col in cross_columns:
		data_types[col]=int1 #could make this allow blanks, etc.

	for d in defense_types:
		data_types[d+' Available']=bool

	for row in info:
		for key in row:
			if data_types.has_key(key):
				row[key]=data_types[key](row[key])

	#for a in info: print a
	relevant=filter(lambda x: x['Team']==team_number and x['Low Bar Available']==1,info)
	
	if len(relevant)<2:
		return alternate_data_source(team_number)

	#for a in relevant: print a
	def get_col(name):
		if name=='Moat Scored Crossings': name='Moat Scored Crosings'
		#print 'col ',name,':',map(lambda x: x[name],relevant)
		return map(lambda x: x[name],relevant)
	highs=get_col('Teleop High Goals')+get_col('Auto High Goals')
	lows=get_col('Teleop Low Goals')+get_col('Auto Low Goals')
	#print (highs)
	#print (lows)
	approx_rounds=len(relevant)+.001
	balls_per_match=sum(highs+lows)/approx_rounds

	def_per_match=sum(map(lambda x: sum(get_col(x)),cross_columns))/approx_rounds

	#print cross_columns
	#print transpose(map(lambda x: get_col(x),cross_columns))
	def_by_match=map(sum,transpose(map(get_col,cross_columns)))
	#print 'defb:',def_by_match

	#start of trying to do fancier stuff
	by_match=zip(map(lambda x: x[0]+x[1],zip(highs,lows)),def_by_match)
	print 'Team',team_number,
	print mean(firsts(by_match)),mean(seconds(by_match))
	print 'by_match:',by_match

	#time per defense = average of average time in matches weighted by how many defenses did
	by_match_ball=[] #(time used each,weight)
	by_match_def=[]
	match_time=60*2+15+0.0
	for balls,defenses in by_match:
		s=balls+defenses+0.01
		t=match_time/s
		if balls:
			by_match_ball.append((t,balls/s))
		if defenses:
			by_match_def.append((t,defenses/s))
	def weighted_average(x):
		num=sum(map(lambda y: y[0]*y[1],x))
		denom=sum(seconds(x))
		if denom==0: return 60 #very application specific
		return num/denom

	def mean1(a):
		if len(a): return (0.0+sum(a))/len(a)
		return 0

	climb_per_match=mean1(get_col('Climb Flag'))
	challenge_per_match=mean1(get_col('Challenge Flag'))

	def defense_average(name):
		#print 'calc for',name,type(name)
		x=name+' Available'
		#print 'x:',x
		#print get_col(x)
		denom=sum(get_col(x))
		num=sum(get_col(name+' Scored Crossings')+get_col(name+' Teleop Crossings'))
		if denom==0: return 0
		return (0.0+num)/denom

	defense_averages=pairs_to_map(map(lambda x: (x,defense_average(x)),defense_types))

	#print 'by match ball:',by_match_ball
	#print 'by match def:',by_match_def

	#balls_per_match=match_time/weighted_average(by_match_ball)
	#def_per_match=match_time/weighted_average(by_match_def)

	#return balls_per_match,def_per_match,(climb_per_match+challenge_per_match)>.5,climb_per_match>.5,defense_averages
	#rr=(balls_per_match,def_per_match,(climb_per_match+challenge_per_match)>.5,climb_per_match>.5,defense_averages)
	rr=(weighted_average(by_match_ball),weighted_average(by_match_def),(climb_per_match+challenge_per_match)>.5,climb_per_match>.5,defense_averages)
	print 'rr:',rr
	return rr

#str->(int(match#)->(str(color)->[int(team#)]))
def parse_match_schedule(filename):
	info=parse_csv(filename)
	r={}
	def add_entry(match,alliance,team):
		if not r.has_key(match): r[match]={}
		match_info=r[match];
		if not match_info.has_key(alliance): match_info[alliance]=[]
		alliance_info=match_info[alliance]
		alliance_info.append(team)
	for line in info:
		add_entry(int(line['Match']),line['Alliance'],int(line['Team']))
	return r

if __name__=='__main__':
	from optparse import OptionParser
	p=OptionParser()
	p.add_option('--team',type=int,default=1425)
	options,args=p.parse_args()
	assert len(args)==0
	team_number=options.team
	filename="StrongholdScoutingWorkbookDEMO.csv"
	balls_per_match,def_per_match,challenge,climb,defenses=run(filename,team_number)
	print 'ball time:',balls_per_match
	print 'defenses time:',def_per_match
	print 'challenge:',challenge
	print 'climb:',climb
	print 'def:',defenses
