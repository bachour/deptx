import json
import random
import string
import copy

try:
    from deptx.settings_production import MEDIA_ROOT
except:
    from deptx.settings import MEDIA_ROOT

RANDOM_FILES_PATH = MEDIA_ROOT + "GRINDING/"

# takes a json for a graph with randomizable content, randomizes all values in the graph, randomly chooses one set
# of critical values and makes at least one of them different from the others. adds question mark before all these values
# returns the resulting graph as a json object
def get_random_graph_old(graph):
    identifiers = {}
    identifier_main_att = {}
    identifier_super_main_att = {}
    duplicate_count = 0
    triplicate_count = 0
    
    #first collect all identifiers and assign random values to them from their respective source files
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '$' or graph[c][e][a][0] == '&':
                    values = graph[c][e][a].split()
                    file = values[0][1:]
                    if file[0] == '&':
                        file = file[1:]
                    id = values[1]
                    if not identifiers.has_key(id):
                        identifiers[id] = []
                        identifiers[id].append(get_random_from_file(RANDOM_FILES_PATH + file + ".txt", identifiers[id]))
                    elif len(identifiers[id]) == 1:
                        identifiers[id].append(get_random_from_file(RANDOM_FILES_PATH + file + ".txt", identifiers[id]))
                        duplicate_count += 1
                    else:
                        identifiers[id].append(identifiers[id][random.randint(0,1)])
                        triplicate_count += 1
                        if graph[c][e][a][0] == '&':
                            print "WARNING: main attribute for identifier that has more than 2 occurences: ", id
                        
                    # if this is the main attribute, store its value
                    if graph[c][e][a][0] == '&' and not graph[c][e][a][1] == '&':
                        if identifier_main_att.has_key(id) or identifier_super_main_att.has_key(id):
                            print "WARNING: multiple main attributes detected for identifier: ", id
                        identifier_main_att[id] = identifiers[id][-1]
                    # if this is a super main attribute, store it's value
                    elif graph[c][e][a][0] == '&' and graph[c][e][a][1] == '&':
                        if identifier_main_att.has_key(id)  or identifier_super_main_att.has_key(id):
                            print "WARNING: multiple super main attributes detected for identifier: ", id
                        identifier_super_main_att[id] = identifiers[id][-1]
                        
    #make duplicate_count a random number between 0 and duplicate_count
    duplicate_count = duplicate_count - len(identifier_super_main_att) #ignore supermain attributes. they can't be inconsistencies
    duplicate_count = duplicate_count - random.randint(0,duplicate_count) # we want a random number between 1 and duplicate_count + 1 for no inconsistency case  
                     
    #choose duplicate_countTH duplicated identifier, and add ?'s to it's value 
    #since duplicate count can go 1 above the last possible value, then           
    for i in identifiers:
        #first deal with super main attributes
        if identifier_super_main_att.has_key(i):
            selected = identifier_super_main_att[i]
            for j in range(len(identifiers[i])):
                identifiers[i][j] = selected
        #now deal with the rest
        elif len(identifiers[i]) >= 2:
            if (duplicate_count == 0):
                #print 'selected ',i, ': ', identifiers[i]
                for j in range(len(identifiers[i])):
                    identifiers[i][j] = '?' + identifiers[i][j]
            else:
                #choose one of the values and place it everywhere
                if (identifier_main_att.has_key(i)):
                    #main attrbute found, use it
                    selected = identifier_main_att[i]
                else: #otherwise just choose at random
                    selected = identifiers[i][random.randint(0, len(identifiers[i])-1)]
                    
                for j in range(len(identifiers[i])):
                    identifiers[i][j] = selected
            duplicate_count -= 1
    
    #replace every element in the graph with an element from the randomly generated list
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '$' or graph[c][e][a][0] == '&':
                    values = graph[c][e][a].split()
                    id = values[1]
                    graph[c][e][a] = identifiers[id].pop(0)
        
    return graph


# searches the graph for ? attribute, creates 2 lists of node, attribute pairs corresponding to the sets of attribtue values that should
# be consistent but arent. then returns the two lists, as well as the modified graph (without the question marks) as a json object
def get_inconsistencies(graph):
    
    criticals = {}
    
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '?':
                    if not criticals.has_key(graph[c][e][a]):
                        criticals[graph[c][e][a]] = []
                    criticals[graph[c][e][a]].append({"node":e,"attribute":a})
                    graph[c][e][a] = graph[c][e][a][1:]
                    
    lists = []
    for a in criticals:
        lists.append(criticals[a])
        
    return lists, graph

# internal use function:
# returns a random line from file that is not found in the list not_in
# returns None if no such line exists
def get_random_from_file(file, not_in):
    afile = open(file, 'U')
    lines = []
    
    line = None
    
    for line in afile.readlines():
        line = filter(lambda x: x in string.printable, line).strip()
        if line in not_in or len(line) < 1:
            continue
        lines.append(line)
           
    return lines[random.randint(0, len(lines)-1)].strip()

# test graphs
def test_graph(grph, trials):
    all_inconsistencies = []
    for i in range(trials):
        d_graph = duplicate_graph(grph)
        r_graph = get_random_graph(d_graph)
        print r_graph
        lists, graph = get_inconsistencies(r_graph)
        all_inconsistencies.append(lists)
        
        
    
    return all_inconsistencies
        

def get_random_graph(graph):
    identifiers = {}
    identifier_main_att = {}
    identifier_super_main_att = {}
    sub_identifiers = {}
    duplicate_count = 0
    triplicate_count = 0
    
    #first collect all identifiers and assign random values to them from their respective source files
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '$' or graph[c][e][a][0] == '&':
                    values = graph[c][e][a].split()
                    file = values[0][1:]
                    if file[0] == '&':
                        file = file[1:]
                    id = values[1]
                    if not identifiers.has_key(id):
                        identifiers[id] = []
                        identifiers[id].append(get_random_from_file(RANDOM_FILES_PATH + file + ".txt", identifiers[id]))
                    elif len(identifiers[id]) == 1:
                        identifiers[id].append(get_random_from_file(RANDOM_FILES_PATH + file + ".txt", identifiers[id]))
                        duplicate_count += 1
                    else:
                        identifiers[id].append(identifiers[id][random.randint(0,1)])
                        triplicate_count += 1
                        if graph[c][e][a][0] == '&':
                            print "WARNING: main attribute for identifier that has more than 2 occurences: ", id
                        
                    # if this is the main attribute, store its value
                    if graph[c][e][a][0] == '&' and not graph[c][e][a][1] == '&':
                        if identifier_main_att.has_key(id) or identifier_super_main_att.has_key(id):
                            print "WARNING: multiple main attributes detected for identifier: ", id
                        identifier_main_att[id] = identifiers[id][-1]
                    # if this is a super main attribute, store it's value
                    elif graph[c][e][a][0] == '&' and graph[c][e][a][1] == '&':
                        if identifier_main_att.has_key(id)  or identifier_super_main_att.has_key(id):
                            print "WARNING: multiple super main attributes detected for identifier: ", id
                        identifier_super_main_att[id] = identifiers[id][-1]
                elif graph[c][e][a][0] == '#':
                    values = graph[c][e][a][1:].split()
                    # get the id of the main attribute and the sub id of the sub-attrubte
                    id = values[0].strip()
                    sub_id = values[1].strip()
                    # create a place holder for the sub attribute which will be filled later
                    if not id in sub_identifiers:
                        sub_identifiers[id] = {}
                        sub_identifiers[id][sub_id] = ""
                        duplicate_count += 1
                    else:
                        if not sub_id in sub_identifiers[id]:
                            sub_identifiers[id][sub_id] = ""
                            duplicate_count += 1
    
    
    for i in sub_identifiers:
        for j in sub_identifiers[i]:
            # get the list of available attributes for this sub identifier from the the main identifier's value
            sub_identifiers[i][j] = get_sub_identifier_list(identifiers[i][0], j)
        # remove the list of sub-attributes from the main attribute value
        identifiers[i][0] = identifiers[i][0][0:identifiers[i][0].index('{')].strip()
        if identifier_super_main_att.has_key(i):
            identifier_super_main_att[i] = identifier_super_main_att[i][0:identifier_super_main_att[i].index('{')].strip()
                              
    #ignore supermain attributes. they can't be inconsistencies
    for sma in identifier_super_main_att:
        if sma in sub_identifiers:
            duplicate_count = duplicate_count - len(sub_identifiers[sma])
        else:
            duplicate_count = duplicate_count - 1
            
    #make duplicate_count a random number between 0 and duplicate_count
    duplicate_count = duplicate_count - random.randint(0,duplicate_count) # we want a random number between 1 and duplicate_count + 1 for no inconsistency case  
             
    #choose duplicate_countTH duplicated identifier, and add ?'s to it's value 
    #since duplicate count can go 1 above the last possible value, then           
    for i in identifiers:
        #first deal with super main attributes
        if identifier_super_main_att.has_key(i):
            selected = identifier_super_main_att[i]
            for j in range(len(identifiers[i])):
                identifiers[i][j] = selected
            if i in sub_identifiers:
                for j in sub_identifiers[i]:
                    sub_identifiers[i][j] = get_sub_identifier_value(sub_identifiers[i][j], True)
        #now deal with the rest
        elif len(identifiers[i]) >= 2:
            if (duplicate_count == 0):
                #print 'selected ',i, ': ', identifiers[i]
                for j in range(len(identifiers[i])):
                    identifiers[i][j] = '?' + identifiers[i][j]
            else:
                #choose one of the values and place it everywhere
                if (identifier_main_att.has_key(i)):
                    #main attrbute found, use it
                    selected = identifier_main_att[i]
                else: #otherwise just choose at random
                    selected = identifiers[i][random.randint(0, len(identifiers[i])-1)]
                    
                for j in range(len(identifiers[i])):
                    identifiers[i][j] = selected
            duplicate_count -= 1    
        elif i in sub_identifiers:
            for j in sub_identifiers[i]:
                if (duplicate_count == 0):
                    identifiers[i][0] = '?' + identifiers[i][0]
                    sub_identifiers[i][j] = '?' + get_sub_identifier_value(sub_identifiers[i][j], False)
                else:
                    sub_identifiers[i][j] = get_sub_identifier_value(sub_identifiers[i][j], True)
                duplicate_count -= 1
                
    #replace all sub-enabled attributes with simple attributes
    for i in identifiers:
        for j in range(len(identifiers[i])):
            if '{' in identifiers[i][j]:
                identifiers[i][j] = identifiers[i][j][0:identifiers[i][j].index('{')].strip()
     
    #replace every element in the graph with an element from the randomly generated list
    for c in graph: #node class
        if c == 'prefix':
            continue
        for e in graph[c]: #individual elements
            for a in graph[c][e]:
                if graph[c][e][a][0] == '$' or graph[c][e][a][0] == '&':
                    values = graph[c][e][a].split()
                    id = values[1]
                    graph[c][e][a] = identifiers[id].pop(0)
                if graph[c][e][a][0] == '#':
                    values = graph[c][e][a].split()
                    id = values[0][1:]
                    sub_id = values[1]
                    graph[c][e][a] = sub_identifiers[id][sub_id]
        
    return graph


def get_sub_identifier_list(str, sub_id):
    while not str.startswith(sub_id):
        str = str[str.index('{')+1:].strip();
    
    str = str[str.index('|')+1:str.index('}')].strip();
    return str;

def get_sub_identifier_value(str, consistent):
    lists = str.split('|')
    if consistent:
        return get_random_from_string(lists[0])
    else:
        return get_random_from_string(lists[1])
    
def get_random_from_string(str):
    list = str.split(';')
    return list[random.randint(0,len(list)-1)].strip()

# function to duplicate graph
def duplicate_graph(graph):
    d_graph = {}
    #print(graph)
    if type(graph) is dict or type(graph) is type([]):
        for i in graph:
            d_graph[i] = duplicate_graph(graph[i])
        
    else:
        d_graph = copy.deepcopy(graph)
        #print d_graph
    
    return d_graph
    
#RANDOM_FILES_PATH = '/Users/khaled/Dropbox/Dept.X/MEDIA/GRINDING/'
#grph = json.load(open("/Users/khaled/Documents/amptest.json",'r'))
#RANDOM_FILES_PATH = 'C:\\Users\\kqb.CS\\Documents\\grinding_script_tests\\random_files\\'
#grph = json.load(open("C:\\Users\\kqb.CS\\Documents\\grinding_script_tests\\orphan.json",'r'))

#test_graph(grph,100)
#gph = get_fancy_random_graph(grph)
#print gph