from modules import *

names = [node['name'] for node in get_interchanges(graph=graph,include_only_lines=['EW','DT','BP'])]
print(names)