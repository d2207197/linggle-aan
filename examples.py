# import pickle
import v4
import noun_forms
import vf_to_vb
import os
from subprocess import Popen, PIPE

EXAMPLE_ROOT = ['/home/nlplab/joanne/NY/', 'examples/']
for path in EXAMPLE_ROOT:
	if os.path.exists(path):
		EXAMPLE_ROOT = path
		break
	else:
		EXAMPLE_ROOT = ''

def get_Examples(ngram):
	string = ngram
	ngram = ngram.split()
	flag=0
	lili = []
	for x in ngram:
		if flag==0:
			try:
				rep = EXAMPLE_ROOT + "noun_example_base/"+noun_forms.d2[x.lower()]
				f =open(rep)
				flag = 1
				rap = rep
			#	print 'nouns!!!!'
			except:
				pass
	if flag==1:
		p1 = Popen(["grep","-E","-m",'3', "[^a-zA-Z]"+string+"[^a-zA-Z]",rap], stdout=PIPE)
    		lili = p1.communicate()[0].split("\n")

 
#               ro = "cat "+rap+" | grep -E -m 3 \'[^a-zA-Z]"+string+"[^a-zA-Z]\' > /home/nlplab/joanne/NY/ex.txt"
#                print ro
                #os.system(ro)
                
		#f = open("/home/nlplab/joanne/NY/ex.txt")
                #lili = f.readlines()
                #os.system('rm /home/nlplab/joanne/NY/ex.txt')
	else:
		for x in ngram:
                	if flag==0:
				try:
					bf = vf_to_vb.d[x.lower()]
			#		print bf
					a = v4.li[bf][x.lower()]
			#		print a
					if a== 'VBD/VBN':
						a="VBDVBN"
					rep = EXAMPLE_ROOT + "example_base/"+bf+"/"+a
					f = open(rep)
					flag = 1
			#		print "verbs!!!!"
					rap = rep
				except KeyError:
					pass
		if flag==1:

			p1 = Popen(["grep","-E","-m",'3', "[^a-zA-Z]"+string+"[^a-zA-Z]",rap], stdout=PIPE)
			lili = p1.communicate()[0].split("\n")

#			ro = "cat "+rap+" | grep -E -m 3 \'[^a-zA-Z]"+string+"[^a-zA-Z]\' > /home/nlplab/joanne/NY/ex.txt"
#			print ro
			#os.system(ro)
			#f = open("/home/nlplab/joanne/NY/ex.txt")
			#lili = f.readlines()
			#os.system('rm /home/nlplab/joanne/NY/ex.txt')
	return lili	



if __name__ == '__main__':


	a = "include a person"
	print
	print get_Examples(a)

	b = "including your"
	print
	print get_Examples(b)
