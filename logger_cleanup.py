# this script will remove API information from the log file before Github upload

file = open("weatherEE_Log.txt", "r")
lines = file.readlines()
file.close()

file = open("weatherEE_Log.txt", "w+")

http = "http"
for line in lines:
    spl = line.split(" ")
    if spl[5] != "503" and not spl[5].startswith("http") and not spl[5].startswith("findfont"):
        file.write(line)

file.close()
