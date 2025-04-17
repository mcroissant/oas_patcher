from deepdiff import DeepDiff
import yaml

from oas_patch.file_utils import load_file


original = load_file('./tests/samples/compliance_set/add-a-license/openapi.yaml')
modified = load_file('./tests/samples/compliance_set/add-a-license/output.yaml')

diff = DeepDiff(original, modified, view='tree')

print(diff.affected_paths[0].up.path())
paths = diff.affected_paths[0].path(output_format='list')
print("$." + ".".join(paths))
obj = {}
obj[paths[len(paths) - 1]] = diff.affected_paths[0].t2
print(obj)