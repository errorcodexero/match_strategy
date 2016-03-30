#!/usr/bin/python
#sys.path.insert(0,'/home/tools/python/v2.4.5_centos5_vw8/lib/python2.4/site-packages')
import pyExcelerator

book=pyExcelerator.parse_xls('Team_2834_2016_Scouting_Database_v1_w4.xls')

#from team number to map of name to list of results
team_info={}

def add_info(team,name,point):
	if not team_info.has_key(team): team_info[team]={}
	info=team_info[team]
	if not info.has_key(name): info[name]=[]
	info[name].append(point)

for sheet in book:
	name=sheet[0]
	values=sheet[1]
	#print name,len(values)
	first=values.get((0,0))
	if first!=name or name=='Worldrank': continue
	#print name

	i=3
	while i<100:
		team_cell=values.get((i,1))
		if team_cell is None: break
		team=int(team_cell)
		#print 'team',team
		
		col=0
		while col<100:
			heading=values.get((2,col))
			#print heading
			if heading is not None and heading[:3]=='OPR' or heading in ['Goals','Defense']:
				#print '  ',heading,values.get(i,col)
				value=values.get((i,col))
				add_info(team,heading,value)
			col+=1
		i=i+1

#team->entity->value
team_averages={}

def mean(x): return sum(x)/len(x)

for team in team_info:
	this_team={}
	info=team_info[team]
	for prop in info:
		this_team[prop]=mean(info[prop])
	team_averages[team]=this_team

#print team_info
for team in team_averages:
	avg=team_averages[team]
	teleop=avg['OPR Teleop (no Tower)']
	challendge_scale=avg['OPR Tower']
	goal_total_pts=avg['Goals']
	defense_total_pts=avg['Defense']
	goal_pt_frac=(0.0+goal_total_pts)/(goal_total_pts+defense_total_pts)
	goal_pts=goal_pt_frac*teleop
	defense_pts=(1-goal_pt_frac)*teleop
	balls=goal_pts/3
	crossings=defense_pts/5

	#crossings=crossing_score/5
	#balls=ball_score/3 #just going to assume some number between 2 and 5 for now.
	#for now, assume that the portion of time spent doing activity is half way between 1/2 and portion of actions taken to make
	#goal_frac=goals/(goals+defense)
	print team,'%.1f'%crossings,'%.1f'%balls


