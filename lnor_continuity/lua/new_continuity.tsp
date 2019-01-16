--this is the script that's on the DMM

-- read csv file
function csv_read(line)
    data = {}
    entry = 1
    lastpos = 1
    pos = 1
    while pos < string.len(line) do
		c = string.sub(line,pos,pos)
	
    	if c=="," then
	    	data[entry] = string.sub(line,lastpos,pos-1)
	    	lastpos = pos+1
	    	entry = entry+1
		end
	
		pos = pos + 1
    end

    data[entry] = string.sub(line,lastpos)

    return data
end

--write to csv on USB and print to screen for telnet
function csv_write(outf, out)
	for i,line in pairs(out) do
		line_str = ""
		for j,val in pairs(line) do
			line_str = line_str..","..val
		end
		outf:write(string.sub(line_str,2).."\n")
		print(string.sub(line_str,2))
	end
end

-- check whether two channels are in the list of special measurements
function pair_match(ch1,ch2,expectations)
    for i=1,table.getn(expectations) do
    	if expectations[i][1] == ch1 then
	   		if expectations[i][2] == ch2 then
	      		return i
	   		end
		end
		if expectations[i][1] == ch2 then
			if expectations[i][2] == ch1 then
				return i
			end
		end
    end
end

--measure resistance between two channels
function single_test(ch1,ch2,wait_val)
    buf = dmm.makebuffer(1)
    ch_sig = "112"..ch2

    channel.close(ch_sig)

    delay(wait_val)
    dmm.measure(buf)

    channel.open(ch_sig)

    return tonumber(buf[1])
end

--measure LED in two directions
function led_test(ch1,ch2,wait_val)
	buf = dmm.makebuffer(2)
	ch_sig = "112"..ch2
	
	channel.close(ch_sig)

	delay(wait_val)
	dmm.measure(buf)--first measurement
	
	channel.open(ch_sig)
	
	--if O/C, try measuring the other way
	if buf[1] ~= 9.9e37 then 
		return 1,tonumber(buf[1])
	else
		channel.open("111"..ch1)
		channel.close("112"..ch1..",111"..ch2)
		delay(wait_val)
		dmm.measure(buf)
		channel.open("112"..ch1..",111"..ch2)
		channel.close("111"..ch1)
		return -1,tonumber(buf[2])--polarity -1
	end
end

--calculate resistance of device measured in parallel with 100M
function parallel(val,res_cal)
    val = 1/val
    val = val - 1/res_cal
    val = 1/val
    return val
end

function main(file_name)

--input file must be valid
if fs.is_file("/usb1/"..file_name) == false then
	print("No such file")
	return nil
end

reset() --clear previous multimeter settings
wait_val = 0.3 --delay between measurements, lets channels settle


--read channel naming scheme
channel_naming = io.open("/usb1/channel_naming.csv", "r")

n = 1
name_map = {}
channels = {}

while true do
	line = channel_naming:read("*l")
	if line == nil then
		break
	end
    channels[n] = string.sub(line, 1, 2)
    name_map[channels[n]] = string.sub(line,4)
    n = n + 1
end

io.close()

--read list of channel pairs that should be connected
expected_values = io.open("/usb1/"..file_name, "r")

n = 1
exps = {}

while true do
	line = expected_values:read("*l")
	if line == nil then
		break
	end
    exps[n] = csv_read(line)
    n = n + 1
end

io.close()

channel.close("10911")--backplane

--calibrate 100M resistor
dmm.func = "twowireohms"
dmm.autodelay = 0
channel.close("11156,11254")--100M
delay(wait_val)
res_buf = dmm.makebuffer(1)
dmm.measure(res_buf)
res_cal = tonumber(res_buf[1])

channel.open("11156,11254")

out = {}

--do the continuity checks
for i=1,table.getn(channels) do
	--start by measuring all disconnected channels in parallel with 100M
	channel.close("11156,11254")
	
    ch1 = channels[i]
    channel.close("111"..ch1) --close ch1

    res_list = {}
    
	--close all channels that are expected to be disconnected
    for j=i+1,table.getn(channels) do
    	ch2 = channels[j]
		match = pair_match(ch1,ch2,exps)--check if ch1 and ch2 are connected
    	if match ~= nil then
	   		res_list[ch2] = match --flag for resistance measurement later
		else
 	   		channel.close("112"..ch2)
		end
    end

    delay(wait_val)
    cont_buf = dmm.makebuffer(1)
    dmm.measure(cont_buf)--make parallel measurement

    channel.open("11201:112B2")--open all channels on row 2
	
	table.insert(out,{name_map[ch1],"parallel",cont_buf[1]})
	
	--if parallel resistance is low, check channels individually
	--40M is currently set as threshhold, prevents flagging outside of actual shorts
    if tonumber(cont_buf[1]) <= 0.4*res_cal then
        print("Possible short detected on "..name_map[ch1])
        print("Isolating short...")
        print()

		channel.close("11254")--100M still in parallel
       	for j=i+1,table.getn(channels) do
	    	ch2 = channels[j]
	    	if res_list[ch2] == nil then
	       		cont = single_test(ch1,ch2,wait_val)--check pair individually
				table.insert(out,{name_map[ch1],name_map[ch2],cont})
	       		if cont <= 0.4*res_cal then
	       	  		print("Short detected between "..name_map[ch1].." and "..name_map[ch2].." with value "..parallel(cont,res_cal))
	       		end
	    	end
		end
    	channel.open("11254")
    end
    
    channel.open("11156")--100M no longer in parallel
	
	--measure resistance on channels that are expected to be connected
    for ch2,match in pairs(res_list) do
		--two-way LED measurement when measuring LED
    	if string.find(name_map[ch1],"LED") ~= nil or string.find(name_map[ch2],"LED") ~= nil then
	   		pol,res = led_test(ch1,ch2,wait_val)
			if pol == 1 then
				table.insert(out,{name_map[ch1],name_map[ch2],res})
			else
				table.insert(out,{name_map[ch2],name_map[ch1],res})
			end
		--normal pair measurement otherwise		
		else
	   		res = single_test(ch1,ch2,wait_val)
			table.insert(out,{name_map[ch1],name_map[ch2],res})
		end
		
		--check resistance against expected value
		--currently not performed
		--[[
		matched = false
		exp = exps[match]
		for i=3,table.getn(exp),2 do
	   		if math.abs(tonumber(exp[i])-res) <= tonumber(exp[i+1]) then
	      		matched = true
	  		end
		end

		if matched == false then
	   		print("Unexpected resistance between "..name_map[ch1].." and "..name_map[ch2].." of "..res.." Ohms")
		end
		--]]
    end

	channel.open("111"..ch1)
    print("Finished checking "..name_map[ch1])
    print()

end
print("Preparing output file")

--backup on flash drive
outf = io.open("/usb1/output/"..math.floor(os.time())..".txt","w")

csv_write(outf,out)--print line by line to console, gets read by telnet
io.close()
print()
print("All done!")
end
