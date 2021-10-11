import glob, os
os.chdir("demo2/")
for file in glob.glob("*.py"):
    print(file)