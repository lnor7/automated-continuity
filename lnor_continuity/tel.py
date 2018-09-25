import telnetlib,time

HOST = "192.168.5.120"

tn = telnetlib.Telnet(HOST)

dmm_f = raw_input("File name for expected values file: ")
out_name = raw_input("File name for output: ")
tn.write("new_continuity()\n")
tn.write("main(\""+dmm_f+"\")\n")

file_check = tn.read_until("No such file",0.3)
if file_check == "No such file":
    print "File not found locally or on DMM"
    tn.close()
else:
    tel_out = tn.read_until("All done!")
    tn.close()

    tel_out = tel_out.split("\n")

    outf = open("output/raw/"+out_name,"w+")
    outlog = []
    out_flag = False
    for line in tel_out:
        if "output" in line:
            out_flag = True
        if out_flag:
            outf.write(line.strip("\M")+"\n")
        else:
            outlog.append(line.strip("\M")+"\n")
    outf.close()

    outf = open("output/summary/"+out_name,"w+")

    for line in outlog:
        outf.write(line)
    outf.close()
