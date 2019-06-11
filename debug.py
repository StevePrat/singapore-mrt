from modules_2 import graph,find_fewest_transfers_path,path_to_string,get_interchanges

plan = find_fewest_transfers_path(graph,start_name='Bukit Batok',end_name='Clementi')
print('Fewest transfers:',path_to_string(plan))
