#!/usr/bin/env python

import os
import sys

#TODO:
# -Try out w/ the newer version of CV's spreadsheet
# -Decide how want to keep track of source code
# -Run a longer version of the top thing
# -Improve the estimation of robot capabilities
#   -Ball/defense tradeoff
#   -Take autonomous defense crossing into account, 2x?
# -Make odds of winning depend on the opposing alliance

#end-game options:
#-do nothing special
#-climb
#-challenge
#makes for 9 combinations of endgame
#odds of time takes to challenge: 75%: time to cross a defense*1.5, 25%=impossible (time greater than match length)
#odds of time takes to climb: 80% impossible (infinite), 20%: 2x 2x time to cross a defense

main_options=['standard cycle','abbrev cycle','double-defense cycle','cross defenses','feed balls','score balls','play defense','cross & feed']
endgame_options=['none','challenge','climb']
combos=[]
for a in main_options:
	for b in main_options:
		for c in main_options:
			for a1 in endgame_options:
				for b1 in endgame_options:
					for c1 in endgame_options:
						combos.append(tuple(sorted((a,b,c)))+(a1,b1,c1))
combos=sorted(set(combos))
#for a in sorted(combos):
#	print a

#alliance: [(int(time to score ball),int(time to cross defense),int(time to collect))]

alliance_ex=[
	(5,5,5,1,1),
	(10,10,10,1,1),
	(15,15,15,1,1)
	]

import random

#kind of silly not to use a library for this
def normal_pdf(z_score):
	data=[
		(-3,.0013),
		(-2,.0228),
		(-1.7,.0446),
		(-1.5,.0668),
		(-1.3,.0968),
		(-1.2,.1151),
		(-1.1,.1357),
		(-1,.1587),
		(-.9,.1841),
		(-.8,.2119),
		(-.75,.2420),
		(-.6,.2743),
		(-.5,.3085),
		(-.4,.3446),
		(-.3,.3821),
		(-.25,.4013),
		(-.2,.4207),
		(-.1,.4602),
		(-.05,.4801),
		(0,0.5)
		]
	if z_score<=0:
		for score,value in data:
			if score>=z_score: return value
		raise 'fail:%s'%z_score
	return 1-normal_pdf(-z_score)
	
def win_px(score,defense_played):
	#Updated based on The Blue Alliance's average score for week 4.
	mean=77.59

	#best case scenario for defense
	#mean*=(3-defense_played)/3

	#maybe a more realistic model of defense?
	#18% is estimate of portion of scoring that's based on balls
	mean*=(3-defense_played*.18)/3
	
	stddev=25 #Also based on TBA

	#def won(): return random.gauss(mean,stddev)<score
	#n=100
	#wins=sum(map(lambda x: won(),range(n)))
	#return (0.0+wins)/n
	
	z_score=(score-mean)/stddev
	return normal_pdf(z_score)

game_length=2*60+15 #seconds

#bool->[[int]]->(str,str,str)->(float,float)
def value(eliminations_mode,alliance,strategy):
	balls_scored=0
	defenses_crossed=0
	feeds_per_game=0
	scores_per_game=0 #of fed balls
	defense_played=0
	climbed=0
	challenged=0
	for robot,normal_strat,end_strat in zip(alliance,strategy,strategy[3:]):
		def end_length():
			if end_strat=='none': return 0
			if end_strat=='climb': return robot[1]*2
			if end_strat=='challenge': return robot[1]*1.5
			raise 'error'
		if end_strat=='challenge' and robot[3]: challenged+=1
		if end_strat=='climb' and robot[4]: climbed+=1

		normal_length=max(0,game_length-end_length())
		if normal_strat=='standard cycle':
			cycle_time=sum(robot[:3])
			cycles=normal_length/cycle_time
			balls_scored+=cycles
			defenses_crossed+=cycles
		elif normal_strat=='abbrev cycle':
			cycle_time=robot[0]+robot[1]*.5+robot[2]
			cycles=normal_length/cycle_time
			balls_scored+=cycles
		elif normal_strat=='double-defense cycle':
			cycle_time=robot[0]+robot[1]*2+robot[2]
			cycles=normal_length/cycle_time
			balls_scored+=cycles
			defenses_crossed+=2*cycles
		elif normal_strat=='cross defenses':
			cycle_time=robot[1]
			cycles=normal_length/cycle_time
			defenses_crossed+=cycles
		elif normal_strat=='feed balls':
			cycle_time=robot[2]
			cycles=normal_length/cycle_time
			feeds_per_game+=cycles
		elif normal_strat=='score balls':
			cycle_time=robot[0]
			cycles=normal_length/cycle_time
			scores_per_game+=cycles
		elif normal_strat=='play defense':
			defense_played+=1
		elif normal_strat=='cross & feed':
			cycle_time=robot[1]+robot[2]
			cycles=normal_length/cycle_time
			feeds_per_game+=cycles
			defenses_crossed+=cycles
		else:
			raise 'unknown strat: %s'%str(strat)
	#down here, convert into a # of rankings points
	#need to have an estiamte of enemy scores, will depend on defense; should have two modes: 'awesome defnese', where opposing score is lowered by 1/3 per bot, and a more realistic one
	balls_scored+=min(feeds_per_game,scores_per_game)
	defenses_crossed=min(10,defenses_crossed)
	POINTS_PER_BALL=4 #could change this for high/low scoring
	score=defenses_crossed*5+balls_scored*POINTS_PER_BALL+5*challenged+15*climbed
	breached=(defenses_crossed>=8)
	captured=((balls_scored>=8) and (challenged+climbed==3))
	ranking_points=breached+captured+2*win_px(score,defense_played)
	if eliminations:
		return (0,score+20*breached+25*captured)
	#Qualifications mode
	return (ranking_points,score)#,defenses_crossed,balls_scored,score)
	
#for a in sorted(combos):
#	print a,value(alliance_ex,a)

#for result,strat in sorted(zip(map(lambda x: value(alliance_ex,x),combos),combos)):
#	print "%.2f\t%d"%result,'\t',strat

from random import randint

def create_robot():
	return randint(5,30),randint(5,30),randint(5,30),randint(0,1),randint(0,4)==0
	
def create_alliance():
	return [create_robot(),create_robot(),create_robot()]

#any(a),cmp(b) => (a->b) -> [a] -> a
def argmax(f,inputs):
	v=sorted(zip(map(f,inputs),inputs))
	return v[-1][1]

#any(a),cmp(b) => (a->b) -> [a] -> a
def argmin(f,inputs):
	v=sorted(zip(map(f,inputs),inputs))
	return v[0][1]

def alliance_versions(a):
	return [
		a,
		(a[0],a[2],a[1]),
		(a[1],a[0],a[2]),
		(a[1],a[2],a[0]),
		(a[2],a[0],a[1]),
		(a[2],a[1],a[0])
		]

#bool->?->?
def best_strat(eliminations,alliance):
	def inner_value(strat):
		return max(map(lambda x: value(eliminations,x,strat),alliance_versions(alliance)))
	return argmax(lambda x: value(eliminations,alliance,x),combos)

def random_best(eliminations):
	bests=[]
	for i in range(1000):
		al=create_alliance()
		b=best_strat(eliminations,al)
		bests.append(b)
	
	for b in bests: print b

#str->str->str
def tag(name,contents):
	return '<%s>%s</%s>'%(name,contents,name.split()[0])

filename='StrongholdScoutingWorkbookDEMO.csv'

#[int]->[str]
def get_defense_data(opponents):
	import parse

	defense_info=map(lambda team: parse.run(filename,team)[-1],opponents)
	print defense_info
	by_category=[
		('Portcullis','Cheval'),
		('Moat','Ramparts'),
		('Drawbridge','Sally Port'),
		('Rock Wall','Rough Terrain')
		]
	print sorted(defense_info[0])
	def find_better(opts):
		m=map(
			lambda def_type: sum(map(lambda x: x[def_type],defense_info)),
			opts
			)
		if m[0]<m[1]: return (opts[0],m[1]-m[0])
		return (opts[1],m[0]-m[1])

	return map(find_better,by_category)
	#return ['rock wall','portculus','sally port']

verbose_strat={
	'standard cycle':'After scoring, go through a defense and pick up another ball then cross over an undamaged defense until four are damaged, then choose fastest defense. ',
	'abbrev cycle':'Fetch and score balls, but instead of crossing defenses to score points take whichever route is fastest.',
	'double-defense cycle':'For every two defenses crossed one boulder is scored (for the first four defenses crossed - 8 crossings total). If time allows, switch to another strategy after defenses are breached.',
	'cross defenses':'Focus single-mindedly on breaching defenses',
	'feed balls':'Run balls from the neutral zone to the enemies\' courtyard.',
	'score balls':'Robot takes balls already in the courtyard and scores them either in the high or low goal. ',
	'play defense':'Choose one of the following:'+tag('ul','<li>Neutral zone harassment<li>Courtyard defense<li>Shadowing defense'),
	'cross & feed':'Run balls from the neutral zone to the enemies\' courtyard, while also scoring a defensive crossing each cycle'
	}
	
#bool->[int]->[int]->void
def run_with_teams(eliminations,allied_teams,opponents):
	print 'allies:',allied_teams
	print 'opponents:',opponents

	import parse
	def get_data(team):
		p=parse.run(filename,team)
		print 'parsed for',team,':',p
		ball_time,defense_time,challenge,climb,defense_info=p
		
		return ball_time/2,defense_time,ball_time/2,challenge,climb
	alliance=map(get_data,allied_teams)
	print alliance
	unsorted_options=[]
	for a in main_options:
		for b in main_options:
			for c in main_options:
				for a1 in endgame_options:
					for b1 in endgame_options:
						for c1 in endgame_options:
							unsorted_options.append((a,b,c,a1,b1,c1))
	m=sorted(map(lambda x: (value(eliminations,alliance,x),x),unsorted_options))
	#for a in m[-20:]: print a

	td=lambda x: tag('td',x)
	th=lambda x: tag('th',x)
	tr=lambda x: tag('tr',x)

	dd=get_defense_data(opponents)
	def_table=tag('table border',
		tr(th('Category')+th('Defense')+th('How many fewer crossings per round'))+
		''.join(map(
			lambda (cat,(name,margin)): tr(td(cat)+td(name)+td('%.2f'%margin)),
			zip('ABCD',dd)
			))
		)

	def roundy(x):
		if type(x) is float:
			return '%.2f'%x
		if type(x) is str and verbose_strat.has_key(x):
			return tag('b',x)+': '+verbose_strat[x]
		if type(x) is str and x in endgame_options:
			return tag('b',x)+' (Subject to change)'
		return x

	def col(x):
		return tr(''.join(map(
			lambda x: td(roundy(x)),
			x[0]+x[1]
			)))

	table=tag('h2  style="text-align: center;"','Recommended Match Strategies')+tag('table border',
				tr(
					tag('th colspan=2','Expected result')+
					tag('th colspan=3','Teleop')+
					tag('th colspan=3','Endgame')
					)+
				tag('tr',
					''.join(map(th,[
						'Ranking points',
						'Score',
						allied_teams[0],
						allied_teams[1],
						allied_teams[2],
						allied_teams[0],
						allied_teams[1],
						allied_teams[2]
						]))
					)+
				''.join(map(col,reversed(m[-3:])))
				)
	t=tag(
		'html',
		tag('head',
			tag('title','Team 1425 Strategy Output')+
			'<link rel="stylesheet" type="text/css" href="style.css">'
			)+
		tag('body',
			tag('h1',"Team 1425 Strategy Output")+table
			)
		)
	f=open('out.html','w')
	print>>f,open('pre.html').read()
	print>>f,'<table><tr><td>'
	print>>f,tag(
		'h2 style="text-align: center;"',
		'Recommended Defenses when facing '+' '.join(map(str,opponents))
		),def_table
	print>>f,'</td><td>'
	print>>f,table
	print>>f,'</td></tr></table>'
	print>>f,open('post.html').read()
	f.close()
	os.system('firefox out.html')

if __name__=='__main__':
	from optparse import OptionParser
	p=OptionParser()
	p.add_option('--general',action='store_true')
	p.add_option('--match',type=int)
	p.add_option('--eliminations',action='store_true')
	options,args=p.parse_args()
	eliminations=options.eliminations

	if options.general:
		assert len(args)==0
		random_best(eliminations)
		sys.exit(0)

	if options.match:
		assert len(args)==0
		from parse import parse_match_schedule
		teams=parse_match_schedule(filename)[options.match]
		print teams
		if 1425 in teams['Red']:
			run_with_teams(eliminations,teams['Red'],teams['Blue'])
			sys.exit(0)
		run_with_teams(eliminations,teams['Blue'],teams['Red'])
		sys.exit(0)

	if len(args)!=6:
		print 'enter 6 team numbers'
		sys.exit(1)

	teams=map(int,args)
	print teams
	allied_teams=teams[0:3]
	opponents=teams[3:6]

	run_with_teams(eliminations,allied_teams,opponents)

