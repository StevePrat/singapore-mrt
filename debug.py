from modules import *

path = find_fewest_transfers_path(start_name='Little India',end_name='Toa Payoh')
print(path_to_string(path))
save_explored_paths()