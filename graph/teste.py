import graphviz

graph = graphviz.Digraph(comment='The Round Table')

graph.node('A', 'King Arthur')
graph.node('B', 'Sir Bedevere the Wise')
graph.node('L', 'Sir Lancelot the Brave')

#graph.edges(['AB', 'AL'])
#graph.edge('B', 'L', constraint='true')

#print(graph.source)

graph.render(filename='graph', format="svg")