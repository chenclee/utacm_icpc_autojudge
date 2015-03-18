from sys import stdin

T = int (stdin.readline().rstrip())
for casenum in range(T) :
	N = int (stdin.readline().rstrip())
	correct = 0
	for questionnum in range(N) :
		line = stdin.readline().rstrip().split(' = ')
		left = eval(line[0])
		right = int(line[1])
		if (left == right) :
			correct += 1

	score = int(round((correct * 100.0) / N))
	print (str(score) + "%")
	
