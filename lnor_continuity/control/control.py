import math

def num_strip(conn):
    low_tes = ["0","1","2","3","4","5"]
    high_tes = ["6","7","8","9"]
    low_led = ["0","1","2"]
    high_led = ["3","4","5"]
    low_q = ["0","1"]
    high_q = ["2","3"]

    if "TES" in conn:
        low_int = low_tes
        high_int = high_tes
    elif "SQ" in conn:
        while conn[-1] in high_tes or conn[-1] in low_tes:
            conn = conn[:-1]
        conn = conn[:-1]
        return conn
    elif "LED" in conn:
        low_int = low_led
        high_int = high_led
    elif "QD" in conn or "QG" in conn:
        low_int = low_q
        high_int = high_q
    elif "QR" in conn:
        conn = conn[:-1]
        if conn[-1] == "B":
            conn = conn + "OT"
        else:
            conn = conn + "OP"
        return conn
    else:
        return conn   
    
    for i in range(len(conn)):
        if conn[i] in low_int:
            if i+1<len(conn):
                conn = conn[:-2] + "BOT"
            else:
                conn= conn[:-1] + "TOP"
            break
        elif conn[i] in high_int:
            conn = conn[:-1] + "BOT"
            break

    return conn
    
                
def get_type(conn):
    conn = conn.split(",")
    conn1 = conn[0].strip()
    conn2 = conn[1].strip()

    if "QD" in conn1 and "QD" in conn2:
        if conn1[-1] == conn2[-1]:
            conn1=conn1[:-1]+"SAME"
            conn2=conn2[:-1]+"SAME"
            return frozenset([conn1,conn2])

    conn1 = num_strip(conn1)
    conn2 = num_strip(conn2)
    return frozenset([conn1,conn2])
            
def add_val(val1,val2):
    val1 = val1.split(",")
    val2 = val2.split(",")
    for val in val1:
        val.strip('\n')
    for val in val2:
        val.strip('\n')
        
    final_vals = []
    for i in range(0,len(val1)-1,2):
        for j in range(0,len(val2)-1,2):
            final_vals.append(int(val1[i])+int(val2[j]))

    final_tols = []
    for i in range(1,len(val1),2):
        for j in range(1,len(val2),2):
            final_tols.append(int(math.sqrt(int(val1[i])**2+int(val2[j])**2)))

            
    final_s = ""
    for i in range(len(final_vals)):
        final_s += str(final_vals[i])+","+str(final_tols[i])+","

    return final_s[:-1]+"\n"

conn_name = raw_input("Enter the file name specifying connections to check: ")
val_name = raw_input("Enter the file name specifying expected values to check: ")
out_name = raw_input("Enter a file name for the control file being created: ")

name_map = {}
name_f = open("channel_naming.csv","r")
for line in name_f:
    line=line.split(",")
    name_map[line[1].strip()] = line[0].strip()
name_f.close()

connections = []
connect_f = open("connections/"+conn_name,"r")
for line in connect_f:
    connections.append(line)
connect_f.close()


values = {}
values_f = open("expected/"+val_name,"r")
for line in values_f:
    line=line.split(",")
    l0 = line[0].strip()
    l1 = line[1].strip()

    val_s = ""
    for i in range(2,len(line)):
        val_s += line[i]+","
    val_s = val_s[:-1]
    values[frozenset([l0,l1])] = val_s
values_f.close()

gnd_top = []
gnd_bot = []
for conn in connections:
    conn_split = conn.split(",")
    if "GND_TOP" in conn_split[0] and "GND" not in conn_split[1]:
        gnd_top.append(conn_split[1].strip())
    if "GND_TOP" in conn_split[1] and "GND" not in conn_split[0]:
        gnd_top.append(conn_split[0].strip())
    if "GND_BOT" in conn_split[0] and "GND" not in conn_split[1]:
        gnd_bot.append(conn_split[1].strip())
    if "GND_BOT" in conn_split[1] and "GND" not in conn_split[0]:
        gnd_bot.append(conn_split[0].strip())

outpairs = []
        
outf = open("output/"+out_name,"w+")
for conn in connections:
    conn_stripped = get_type(conn)
    if conn_stripped in values:
        conn_vals = values[conn_stripped]

    conn_split = conn.split(",")
    conn1 = conn_split[0].strip()
    conn2 = conn_split[1].strip()
    
    for el in [conn1,conn2]:
        if el in gnd_top:
            for gnd_conn in gnd_top:
                gnd_val = values[get_type("AGND_TOP,"+gnd_conn)]
                full_val = add_val(gnd_val,conn_vals)
                if el != gnd_conn:
                    outf.write(name_map[el]+","+name_map[gnd_conn]+","+full_val)
                    outpairs.append(name_map[el]+","+name_map[gnd_conn])
            for gnd_conn in gnd_bot:
                gnd_val = values[get_type("AGND_BOT,"+gnd_conn)]
                gnd_val = add_val(gnd_val,values[get_type("AGND_TOP,AGND_BOT")])
                full_val = add_val(gnd_val, conn_vals)
                if el != gnd_conn:
                    outf.write(name_map[el]+","+name_map[gnd_conn]+","+full_val)
                    outpairs.append(name_map[el]+","+name_map[gnd_conn])
                
        if el in gnd_bot:
            for gnd_conn in gnd_bot:
                gnd_val = values[get_type("AGND_BOT,"+gnd_conn)]
                full_val = add_val(gnd_val,conn_vals)
                if el != gnd_conn:
                    outf.write(name_map[el]+","+name_map[gnd_conn]+","+full_val)
                    outpairs.append(name_map[el]+","+name_map[gnd_conn])
            for gnd_conn in gnd_top:
                gnd_val = values[get_type("AGND_TOP,"+gnd_conn)]
                gnd_val = add_val(gnd_val,values[get_type("AGND_TOP,AGND_BOT")])
                full_val = add_val(gnd_val, conn_vals)
                if el != gnd_conn:
                    outf.write(name_map[el]+","+name_map[gnd_conn]+","+full_val)
                    outpairs.append(name_map[el]+","+name_map[gnd_conn])
                
    outf.write(name_map[conn1]+","+name_map[conn2]+","+conn_vals)
    outpairs.append(name_map[conn1]+","+name_map[conn2])
        
outf.close()

dmm_val = raw_input("Create file for transfer to DMM? (y/n) ")
if dmm_val == "y":
    outf_dmm = open("dmm/"+out_name,"w+")
    for line in outpairs:
        outf_dmm.write(line+"\n")
    outf_dmm.close()
