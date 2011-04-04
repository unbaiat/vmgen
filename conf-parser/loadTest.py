import pickle, test

with open('conf.dump', 'rb') as f:
    entry = pickle.load(f)
    print entry
    print entry.get('hardware','cpu_no')
    print entry.get('bla', 'bla')
    print entry.get('hardware', 'bla')
