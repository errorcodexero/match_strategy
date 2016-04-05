import os,sys
import commands

#To use, give arguments that are the team numbers whose pictures should be fetched

def find_team_pictures(team_number):
	status,output=commands.getstatusoutput('wget http://www.thebluealliance.com/team/%d -O - | grep imgur'%team_number)
	#assert status==0
	l=output.splitlines()
	out=[]
	for x in l:
		out.extend(filter(lambda y: 'http' in y and 'jpg' in y and 'background-image' not in y,x.split('"')))
	for i,url in enumerate(set(out)):
		r=os.system('wget %s -O %d_%d.jpg'%(url,team_number,i))
		assert (r==0)

if __name__=='__main__':
	map(lambda x: find_team_pictures(int(x)),sys.argv[1:])
