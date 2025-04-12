import jidouteki
import argparse

parser = argparse.ArgumentParser(description="Run self-tests on parsers.")
parser.add_argument("keys", type=str, nargs="*", help="The keys of parsers to test. By default, tests all parsers.")
parser.add_argument("-d", "--directory", type=str, help="The directory parsers are stored in.", default="./parsers")
args = parser.parse_args()

jdtk = jidouteki.Jidouteki(proxy=None)

providers = jdtk.load_directory(args.directory)
    
for provider in providers:
    if len(args.keys) > 0:
        if provider.meta.key not in args.keys:
            continue
        
    print(provider.meta.display_name)
    status = provider.test.all()
    
    stack = [(status, 0)]
    while len(stack) > 0:
        d, i = stack.pop()
        if isinstance(d, dict):
            for item in d.items():
                stack.append((item, i))
        else:
            key, val = d
            if isinstance(val, dict):
                print("\t"*i, key + ":")
                for item in val.items():
                    stack.append((item, i+1))
            else:
                print("\t"*i, key + ":", val)
    print()