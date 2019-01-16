function resistance_test(ch1, ch2_list)
    resistor = "11156,11254"
    channel.close(resistor)
    channel.close("111"..ch1)
    for i = 1, #ch2_list do
    	channel.close("112"..ch2_list[i])
    end

    buf = dmm.makebuffer(1)

    delay(0.3)
    dmm.measure(buf)

    for i=1,#ch2_list do
    	channel.open("112"..ch2_list[i])
    end
    channel.open("111"..ch1)
    channel.open(resistor)

    val = tonumber(buf[1])

    val = 1/val
    val = val - 1/res_cal
    val = 1/val

    print(val.." Ohm")
end
    
--measure resistance between two channels
function single_test(ch1,ch2)
    pair = "111"..ch1..",112"..ch2
    buf = dmm.makebuffer(1)

    channel.close(pair)

    delay(0.3)
    dmm.measure(buf)

    channel.open(pair)

    print(buf[1].." Ohm")
end

reset()
dmm.func = "twowireohms"
dmm.autodelay = 0

--calibrate resistor
channel.close("11156,11254")
delay(wait_val)
res_buf = dmm.makebuffer(1)
dmm.measure(res_buf)
res_cal = tonumber(res_buf[1])
channel.open("11156,11254")