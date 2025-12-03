print("Hello From Python in Docker!")

import sys
import pkg_resources

# Print Python version
print("Python version:")
print(sys.version)
print()

# Print installed packages
print("Installed packages:")
for dist in pkg_resources.working_set:
    print(f"{dist.project_name}=={dist.version}")

