from modules import *

print(''.join('=' for i in range(40)))

start = input('Starting station: ')
if not get_node(name=start):
    print("Starting station cannot be found")
    print(''.join('=' for i in range(40)))
    exit()

end = input('Destination station: ')
if not get_node(name=end):
    print("Destination station cannot be found")
    print(''.join('=' for i in range(40)))
    exit()

search_type = input('Type "1" for shortest path search, type "2" for least transfers search: ')
try:
    search_type = int(search_type)
except:
    print("Please provide a valid input.")
    exit()

t1 = time.time()
if search_type == 1:
    path = find_fewest_stations_path_bfs(start_name=start,end_name=end)
elif search_type == 2:
    path = find_fewest_transfers_path(start_name=start,end_name=end)
else:
    print("Search type unknown.")
    exit()

t2 = time.time()

if search_type == 1:
    print('Fewest stations path:',path_to_string(path),sep='\n')
elif search_type == 2:
    print('Fewest transfers path:',path_to_string(path),sep='\n')
print('No. of stations:',len(path))
print('No. of transfers:',calc_transfers(path))
print('Search completed in',str(t2-t1),'seconds.')

save_explored_paths()

print(''.join('=' for i in range(40)))