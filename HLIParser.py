#-*- coding: utf-8 -*-

# import sqlite3 as sqlite
# import re,json
# from nltk import pos_tag
# import pickle,socket
# import datetime
from flask import Response

beVerb 	 = ['be','is','was','are','were']
quantity = ['a', 'an', 'the']
goVerb   = ['go', 'goes', 'come', 'came', 'went', 'gone']
posTag 	 = {'noun':'$N','verb':'$V','adjective':'$A','adverb':'$R','delimiter':'$D','preposition':'$PP'} # 'pronoun', article
dirProp  = ['after', 'before', 'follow', 'with', 'for'] # 有順序，越前面越明確

test = ["which one is best, not more than or no more than?",\
"which one is popular provide with or provide to?", \
"which is better, stay at home or stay in home", \
"which is correct, go home or go to home?", \
"which one are popular be a man or become a man",\
"how to describe beach?", \
"how to describe well an apple?",\
"how to makeup the sea food?"] # $A US citizen



def diff(A, B):
	d = 0
	if len(A) == len(B):
		for i in range(len(A)):
			if A[i] != B[i]:
				d += 1
		return d
	else:
		return False

def patternMaker(parseResult):
	makupResult = ""
	makup = []

	# type: compare
	if parseResult['type'] == 'compare': # A or B


		A = parseResult['data'][0]
		B = parseResult['data'][1]

		# different lenght, [go to home] and [go home]
		if len(A) != len(B):


			target = A if len(A) > len(B) else B # long sent
			search = A if len(A) < len(B) else B # short sent

			for word in target:
				if word not in search:
					element = '?' + word
				else:
					element = word
				makup.append(element)
			makupResult = ' '.join(makup)

		# the same length
		else:
			if diff(A, B) == 1:						# difference = 1
				for i in range(len(A)):				# get difference
					if A[i] != B[i]:
						element = A[i] + '|' + B[i]
					else:
						element = A[i]
					makup.append(element)
				makupResult = ' '.join(makup)

	# type: modify
	elif parseResult['type'] == 'modify':
		P = parseResult['data'] # get phrase
		P.insert(0,'$A')
		makupResult = ' '.join(P)


	elif parseResult['type'] == 'fill':
		F = parseResult['data'][0] # get action, after or before
		POS = parseResult['data'][1]
		P = parseResult['data'][2] # get phrase

		if F == 'after':
			P.append(POS)
		else:
			P.insert(0, POS)

		makupResult = ' '.join(P)

	return makupResult

def parser(tokens):
	idx = {}
	parseResult = {'type':'','data':''}
	
	if len(tokens) == 2 and tokens[0].lower() == 'describe':
		tokens = ['how','to'] + tokens

	if tokens[0] == 'which':

		compare = ["",""];
		# find 'be' position
		idx['be'] = -1
		for t in tokens:
			if t in beVerb:					# be-verb found
				idx['be'] = tokens.index(t) # get the index of be-verb
				break

		# find 'or' position
		idx['or'] = tokens.index('or') if 'or' in tokens else False

		# find ',' position
		idx[','] = tokens.index(',') if ',' in tokens else -1

		# check must required token, e.g., "or" in the "which one is ..., A or B" sentence
		for x in idx:
			if x == False: return False

		# get A
		boundaryLeft = idx['be'] if idx['be'] > idx[','] else idx[',']
		# print boundaryLeft

		# get length of "the best" or "most popular"... (next version)
		modifyWordLength = 1

		compare[0] = tokens[boundaryLeft + modifyWordLength + 1 : idx['or']]
		compare[1] = tokens[idx['or'] + 1 :]

		print compare

		parseResult['type'] = 'compare'
		parseResult['data'] = compare



	elif tokens[0] == 'how':
		# print tokens
		idx['to'] = tokens.index('to') if 'to' in tokens else -1

		# get length of "describe" or "modify"... (next version)
		modifyWordLength = 1

		phrase = tokens[idx['to'] + modifyWordLength + 1:]

		# quant = ""
		for q in quantity:
			if q in phrase:						# the apple, an apple
				idx['qt'] = phrase.index(q) 	# get the index of quantity
				# quant = phrase[idx['qt']] 		# extract the phrase after "the","an","a"
				phrase = phrase[idx['qt']+1:] 	# extract the phrase after "the","an","a"
				break

		parseResult['type'] = 'modify'
		parseResult['data'] = phrase 			# ignore "the", "an" and "a"

	elif  tokens[0] == 'what':
		if len(tokens) < 5: return # min: what verb go with a (length = 5)


		# ok! What preposition should follow jealousy
		# ok! What preposition should I use before Christmas
		# ok! What preposition should be used with intention

		# what preposition to use with the verbs "talk" and "speak" --> talk|speak $PP



		pos = tokens[1]
		pos = pos[:-1] if pos[-1] == 's' else pos
		# get [pos]
		if pos in posTag:
			# fill = 'before' # default

			for direction in dirProp:
				if direction in tokens:					 # get direction
					idx['dir'] = tokens.index(direction) # get index of direction word
					phrase = tokens[idx['dir'] + 1:]
					parseResult['type'] = 'fill'
					parseResult['data'] = (direction, posTag[pos], phrase)
					break

	return patternMaker(parseResult)


	# return
def getParseResults(request, sent):
	tokens = sent.strip().replace('?','').lower().split()
	result = parser(tokens) if len(tokens) > 0 else ""
	return Response(result)

# def getParseResults(request, sent):

# 	result = ""
# 	for s in test:
# 		result += s + "<br/>"
# 		tokens = s.strip().replace('?','').lower().split()

# 		if len(tokens) == 0:
# 			result += ""
# 			# return HttpResponse()
# 		else:
# 			result += parser(tokens)
# 			# return HttpResponse(result)
# 		result += "<hr/>"

# 	return HttpResponse(result)
#
