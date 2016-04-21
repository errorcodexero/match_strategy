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

#These should be constants
low_balls_per_match=5
high_balls_per_match=2.5

def best_move(partner_scoring,tower_strength,time_left):
	tower_strength-=partner_scoring*time_left/MATCH_LEN

	low_balls_per_second=low_balls_per_match/MATCH_LEN
	low_balls_scorable=low_balls_per_second*time_left+2
	if low_balls_scorable<tower_strength:
		#this just try to get points
		if time_left>20: return 'high'
		return 'climb'
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

def show_table():
	for strength in strengths:
		print '%d\t'%strength,
		for time_left in times:
			sys.stdout.write(pad_to_width(4,best_move(partner_scoring,strength,time_left)[0]))
		print
	print '\t',
	for time_left in times:
		sys.stdout.write(pad_to_width(4,time_left))
	print

def show_html(times,strengths,partner_scoring):
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

#[int]->[int]->
def show_plot(times,strengths,partner_scoring):
	import matplotlib.pyplot as plt
	from numpy.random import rand
	import numpy
	import numpy as np

	#Z = rand(6, 10)
	#Z = numpy.array([[0,1],[2,2]])

	def move_to_int(x):
		if x=='high': return 0
		if x=='low': return 1
		if x=='climb': return 2

	Z=numpy.array(map(
		lambda tower_strength: map(lambda time_left: move_to_int(best_move(partner_scoring,tower_strength,time_left)),times),
		strengths
		))
	#plt.subplot(2, 1, 1)
	plt.subplot(1, 1, 1)
	c = plt.pcolor(np.array(times),np.array(strengths),Z)
	plt.gca().invert_xaxis()
	#print c
	#x=np.linspace(0,2*np.pi,100)
	x=np.linspace(0,135,100)
	y1=np.array(map(lambda x: x*(low_balls_per_match+partner_scoring)/MATCH_LEN,x))
	y2=np.array(map(lambda x: x*(high_balls_per_match+partner_scoring)/MATCH_LEN,x))
	#print x
	#y1=np.sin(x)
	#print y1
	plt.plot(x,y1,label='On pace w/ low goals')
	plt.plot(x,y2,label='On pace w/ high goals')

	#when too far behind
	y3=np.array(map(lambda y: y+2,y1))
	plt.plot(x,y3,label='Too far behind; don\'t capture')

	#capture relatively likely
	y4=np.array(map(lambda x: x*(high_balls_per_match*.5+partner_scoring)/MATCH_LEN,x))
	plt.plot(x,y4,label='Have margin for error')

	plt.title(
		'Partner scoring: %d balls\n'%partner_scoring+
		'Fill: Blue=high goals, Red=Climb, Light green=low goals'
		)

	plt.xlabel('Time remaining in match (seconds)')
	plt.ylabel('Tower strength remaining')
	plt.legend()

	#plt.subplot(2, 1, 2)
	#c = plt.pcolor(Z, edgecolors='k', linewidths=4)
	#plt.title('thick edges')

	#plt.show()
	plt.savefig('w_%d.png'%partner_scoring)

def main():
	from optparse import OptionParser

	p=OptionParser()
	p.add_option('--partners',type=float,default=5)
	options,args=p.parse_args()

	partner_scoring=options.partners
	strengths=list(reversed(range(-2,11)))
	times=list(reversed(range(0,136,1))) #originally was 5-second intervals
	#print strengths
	#print times
	#show_html(times,strengths,partner_scoring)
	show_plot(times,strengths,partner_scoring)

if __name__=='__main__':
	main()
