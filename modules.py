import json
import time
from collections import deque

with open("mrt_graph.json") as f:
    graph = json.load(f)

explored_paths = []

def get_node(graph=graph,name=None,code=None):
    if name:
        for node in graph:
            if node['name'] == name:
                return node
        return None
    
    if code:
        for node in graph:
            if code in node['codes']:
                return node
        return None

def get_line(graph=graph,code=''):
    return [node for node in graph if code in node['lines']]
    
def get_lines(graph=graph,codes=set()):
    return [node for node in graph if set(codes) & set(node['lines'])]

def find_fewest_stations_path_bfs(graph=graph,start_code='',end_code='',start_name='',end_name='',path=[]):
    if start_code:
        start_node = get_node(graph=graph,code=start_code)
    if end_code:
        end_node = get_node(graph=graph,code=end_code)
    if start_name:
        start_node = get_node(graph=graph,name=start_name)
    if end_name:
        end_node = get_node(graph=graph,name=end_name)

    if start_node and end_node:
        pass
    else:
        return None

    path = path + [start_node]
    
    explored_paths.append(path)

    if start_node == end_node:
        return path

    neighbours = [get_node(graph=graph,code=neighbour_code) for neighbour_code in start_node['neighbours']]
    queue = deque(path + [n] for n in neighbours if n)
    fewest = []
    while True:
        p = queue.popleft()
        if fewest and len(p)>len(fewest):
            return fewest
        explored_paths.append(p)
        if p[-1] == end_node:
            if not fewest:
                fewest = p
            elif len(p) <= len(fewest):
                if calc_transfers(p) < calc_transfers(fewest):
                    fewest = p
        neighbours = [get_node(graph=graph,code=neighbour_code) for neighbour_code in p[-1]['neighbours']]
        queue.extend(p + [n] for n in neighbours if n and n not in p)

def find_fewest_stations_path_dfs(graph=graph,start_code='',end_code='',start_name='',end_name='',path=[]):
    if start_code:
        start_node = get_node(graph=graph,code=start_code)
    if end_code:
        end_node = get_node(graph=graph,code=end_code)
    if start_name:
        start_node = get_node(graph=graph,name=start_name)
    if end_name:
        end_node = get_node(graph=graph,name=end_name)

    if start_node and end_node:
        pass
    else:
        return None

    path = path + [start_node]
    
    explored_paths.append(path)

    if start_node == end_node:
        return path
    
    shortest = None
    neighbours = [get_node(graph=graph,code=neighbour_code) for neighbour_code in start_node['neighbours']]
    for node in neighbours:
        if node in graph:
            if node not in path:
                new_path = find_fewest_stations_path_dfs(graph=graph,start_name=node['name'],end_name=end_name,path=path)
                if new_path:
                    if not shortest or len(new_path) < len(shortest):
                        shortest = new_path

    return shortest

def get_interchanges(graph=graph,include_only_lines=[],include_lines=[],exclude_lines=[]):
    include_only_lines = set(include_only_lines)
    include_lines = set(include_lines)
    exclude_lines = set(exclude_lines)
    
    interchanges = [node for node in graph if len(node['lines'])>1]
    
    if not (include_only_lines or include_lines or exclude_lines):
        return interchanges

    if include_only_lines:
        return [node for node in interchanges if set(node['lines']) >= include_only_lines]

    if include_lines:
        return [node for node in interchanges if set(node['lines']) & include_lines and not set(node['lines']) & exclude_lines]
    
    if exclude_lines:
        return [node for node in interchanges if not set(node['lines']) & exclude_lines]

def find_fewest_transfers(line_1,line_2,graph=graph,plan=[],plans=[]):
    interchange_nodes = get_interchanges(graph=graph)
    line_codes = set(a for node in graph for a in node['lines'])
    line_connectivity = {a:set(b for node in interchange_nodes if a in node['lines'] for b in node['lines'] if b != a) for a in line_codes}

    def sub_function(line_1,line_2,plan=[],plans=[]):
        plan = plan + [line_1]
        if line_1 == line_2:
            return plan,[plan]
        
        fewest = []
        adjacent_lines = line_connectivity[line_1]
        for line in adjacent_lines:
            if line not in plan:
                new_plan,new_plans = sub_function(line,line_2,plan=plan,plans=plans)
                if new_plan:
                    if not fewest or len(new_plan)<len(fewest):
                        fewest = new_plan
                        plans = new_plans
                    if len(new_plan)==len(fewest) and new_plan not in plans:
                        plans.append(new_plan)
                
        return fewest,plans
    
    return sub_function(line_1,line_2)[1]

def find_fewest_transfers_path(graph=graph,start_code='',end_code='',start_name='',end_name='',path=[],exclude_lines=[]):
    if start_code:
        start_node = get_node(graph=graph,code=start_code)
    if end_code:
        end_node = get_node(graph=graph,code=end_code)
    if start_name:
        start_node = get_node(graph=graph,name=start_name)
    if end_name:
        end_node = get_node(graph=graph,name=end_name)

    start_line_codes = set(start_node['lines']) - set(exclude_lines)
    target_line_codes = set(end_node['lines']) - set(exclude_lines)

    common_line = set(start_line_codes) & set(target_line_codes)
    
    # If common line exist between starting and destination stations: no transfer needed
    if common_line:
        shortest = []
        for line_code in common_line:
            line_1_code = get_line(graph=graph,code=line_code)
            new_path = find_fewest_stations_path_bfs(graph=line_1_code,start_name=start_node['name'],end_name=end_node['name'],path=path)
            if not shortest or len(new_path)<len(shortest):
                shortest = new_path
        return shortest
    
    # If no common line between starting and destination station: find least number of transfers
    else:
        fewest_transfer_plans = []
        for line_1_code in start_node['lines']:
            for line_2_code in end_node['lines']:
                transfer_plans = find_fewest_transfers(line_1_code,line_2_code,graph=graph)
                if not fewest_transfer_plans:
                    fewest_transfer_plans = transfer_plans
                elif len(transfer_plans[0])<len(fewest_transfer_plans[0]):
                    fewest_transfer_plans = transfer_plans
                elif len(transfer_plans[0])==len(fewest_transfer_plans[0]):
                    fewest_transfer_plans.extend(transfer_plans)

        shortest = []
        for plan in fewest_transfer_plans:
            interchanges = get_interchanges(graph=graph,include_only_lines=plan)
            for trf_stn in interchanges:
                partial_path = find_fewest_stations_path_bfs(graph=get_line(graph=graph,code=plan[0]),start_name=start_node['name'],end_name=trf_stn['name'])
                path = find_fewest_transfers_path(graph=graph,start_name=trf_stn['name'],end_name=end_node['name'],path=partial_path[:-1])
                if not shortest or len(path)<len(shortest):
                    shortest = path
                
        return shortest

def calc_transfers(path):
    if len(path) < 2:
        return 0

    current_line = set(path[0]['lines'])
    transfers = 0
    for node in path:
        current_line = current_line & set(node['lines'])
        if not current_line:
            current_line = set(node['lines'])
            transfers += 1
    
    return transfers

def path_to_string(path):
    return '-->'.join([node['name'] for node in path])

def save_explored_paths():
    with open('paths.txt','w') as f:
        f.write('['+ ']\n['.join(path_to_string(path) for path in explored_paths) +']')