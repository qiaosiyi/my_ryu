

def dijkstra(graph,n):
	dis=[0]*n  # len(dis) = n
	flag=[False]*n
	pre=[0]*n
	flag[0]=True
	start=0
	k=0
	listpro=[]
	for i in range(n):
		listpro.append([i])#from point k likely
	print listpro

	print
	print "=========================================================================="
	print "\tdis[",k,"]=",
	for i in range(n):#   0->(n-1)
		dis[i]=graph[k][i]
		print dis[i],
	print
	print

	for j in range(n-1):
		mini=99

		print "j=",j,":mini=99:"

		for i in range(n):
			print "\ti=",i,":","dis[i]=",dis[i],"mini=",mini,"flag[i]=",flag[i]

			if dis[i]<mini and not flag[i]:
				print "\t\tdis[",i,"]<mini and not flag[",i,"]"
				mini=dis[i]
				print "\t\tmini=dis[",i,"]=",dis[i],"dis=",dis
				print "\t\tpre=",pre
				k=i
				print "\t\tk=",i
				# listpro[i].append(i)

		if k==0:#
			print "\tk==0 return"
			return
		flag[k]=True
		print
		print "\tflag[",k,"]=True"
		for i in range(n):
			print "\ti=",i,"dis[i]=",dis[i],"dis[k]=",dis[k],"graph[k][i]=",graph[k][i]
			if dis[i]>dis[k]+graph[k][i]:
				print "\t\tdis[",i,"]>dis[",k,"]+graph[",k,"][",i,"]"
				dis[i]=dis[k]+graph[k][i]
				print "\t\tdis[",i,"]=",dis[i],dis
				pre[i]=k
				print "\t\tpre[",i,"]=",k,pre
				print
				#del listpro[i][len(listpro[i])-1]
				# if pre[k] != 0:
				# 	listpro[i].append(k)
				# 	listpro[i].append(i)

	for i in range(n):
		listpro[i].append(pre[i])

	for i in range(n):
		
		for j in range(n):
			if listpro[j][-1] != 0:
				listpro[j].append(listpro[listpro[j][-1]][1])



	return dis,pre,listpro

if __name__=='__main__':
	n=7
	graph=[
			[0,1,1 ,99,99,99,99],
			[1,0,99,1,1,99,99],
			[1,99,0,1,99,99,99],
			[99,1,1,0,1,99,99],
			[99,1,99,1,0,1,1],
			[99,99,99,99,1,0,1],
			[99,99,99,99,1,1,0]
			]
	dis,pre,listpro=dijkstra(graph,n)
	print(dis)
	print(pre)
	print(listpro)
