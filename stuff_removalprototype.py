with open('./snacc/data/hangman/movies.txt') as  f:
	li=[]
	for line in f:
		if line!='\n':
			li.append(line)
f=open('./snacc/data/hangman/movies.txt','w')
for line in li:
	f.write(line)
print("Done")