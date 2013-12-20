import glob
import yaml
import json

stacks = set()

for file in glob.glob("./e_*"):
    with open(file, "r") as f:
        try: 
            doc = json.load(f)
        except:
            pass
        if doc is None:
            continue
        stk = "\n".join(doc.get('stack', ''))
        stacks.add(stk)

with open("err", "w") as f:
    yaml.safe_dump([['-' * 30] + i.split("\n") for i in stacks], f, default_flow_style=False)
