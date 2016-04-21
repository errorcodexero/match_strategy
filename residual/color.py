#!/usr/bin/env python

import sys

#int,int->(int,int)
def climb_outcome(tower_strength,time_left):
	if time_left>15: return (tower_strength<=0,15)
	return (tower_strength<=0,0)

MATCH_LEN=135.0

def low_outcome(tower_strength,time_left):
	balls_per_match=10
	balls_per_second=balls_per_match/MATCH_LEN
	balls_scored=time_left*balls_per_second
	return (balls_scored>=tower_strength,balls_scored*2)

def high_outcome(tower_strength,time_left):
	balls_per_match=5
	balls_per_second=balls_per_match/MATCH_LEN
	balls_scored=time_left*balls_per_second
	return (balls_scored>=tower_strength,balls_scored*5)

#any(a),sortable(b) => (a->b)->[a]->a
def argmax(f,a):
	return sorted(zip(map(f,a),a))[-1][1]

def best_move1(tower_strength,time_left):
	return argmax(
		lambda (name,x): x(tower_strength,time_left),
		[
			('climb',climb_outcome),
			('low',low_outcome),
			('high',high_outcome)
			]
		)[0]

def best_move(partner_scoring,tower_strength,time_left):
	tower_strength-=partner_scoring*time_left/MATCH_LEN

	low_balls_per_match=5
	low_balls_per_second=low_balls_per_match/MATCH_LEN
	low_balls_scorable=low_balls_per_second*time_left+2
	if low_balls_scorable<tower_strength:
		#this just try to get points
		if time_left>20: return 'high'
		return 'climb'
	high_balls_per_match=2.5
	high_balls_per_second=high_balls_per_match/MATCH_LEN
	sure_high_balls_scorable=high_balls_per_second*.5*time_left
	if sure_high_balls_scorable>=tower_strength:
		if time_left>20: return 'high'
		if tower_strength<=0: return 'climb'
		return 'high'
	return 'low'

#str->int->str
def pad_to_width(width,s):
	s=str(s)
	while len(s)<width:
		s+=' '
	return s

def tag(name,contents):
	return '<%s>%s</%s>'%(name,contents,name)

def tr(s): return tag('tr',s)
def td(s): return tag('td',s)
def th(s): return tag('th',s)
def h2(s): return tag('h2',s)

if __name__=='__main__':
	from optparse import OptionParser

	p=OptionParser()
	p.add_option('--partners',type=float,default=5)
	options,args=p.parse_args()

	partner_scoring=options.partners
	strengths=list(reversed(range(-2,11)))
	times=list(reversed(range(0,140,5)))
	#print strengths
	#print times
	if 0:
		for strength in strengths:
			print '%d\t'%strength,
			for time_left in times:
				sys.stdout.write(pad_to_width(4,best_move(partner_scoring,strength,time_left)[0]))
			print
		print '\t',
		for time_left in times:
			sys.stdout.write(pad_to_width(4,time_left))
		print

	color={
		'low': 'red',
		'high': 'yellow',
		'climb':'green'
		}

	def get_td(move):
		return '<td bgcolor=%s></td>'%color[move]

	used=[0]
	def head():
		if used[0]: return ''
		used[0]=1
		return '<td rowspan=%s>Tower strength remaining</td>'%len(strengths)

	print tag(
		'table border',
		tr('<td colspan=2 rowspan=2></td>'+'<th colspan=%s>Time left in match</th>'%(len(times)))+
		tr(''.join(map(lambda x: tag('th',x),times)))+
		''.join(
			map(
				lambda tower_strength: tr(
					head()+th(tower_strength)+''.join(map(
						lambda time_left: get_td(best_move(partner_scoring,tower_strength,time_left)),
						times
						)
					)),
				strengths
				)
			)
		)
	print h2('Legend')
	print tag('table border',''.join(map(
		lambda move: tr(th(move)+get_td(move)),
		color
		)))

	#print high_outcome(130,
	#need to have go back to different places & actually do a search
