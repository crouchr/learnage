#!/usr/bin/python

# print Flexible Netflow Section payload as ASCII
#def decodeSection(payload):
#    #print "len is " + `len(payload)`
#        
#    r=""
#    for i in range(0,len(payload),2):
#        a = payload[i] + payload[i+1]  
#        ch = int(a,16)  # ch is a number
#        #print "i=" + `i` + " " + `ch`
#        b = chr(ch)   
#        if b.isalnum():
#            r = r + b
#            #print "printable : " + b
#        else:
#            r = r + "."
#            #print "result is " + r   
#    return r


# Do this with a regex !!!!
def isValidHex(a):
    if a[0] == 'a' or a[0] == 'b' or a[0] == 'c' or a[0]=='d' or a[0]=='e' or a[0]=='f' or a[0]=='0' or a[0]=='1' or a[0]=='2' or a[0]=='3' or a[0]=='4' or a[0]=='5' or a[0]=='6' or a[0]=='7' or a[0]=='8' or a[0]=='9':
        if a[1] == 'a' or a[1] == 'b' or a[1] == 'c' or a[1]=='d' or a[1]=='e' or a[1]=='f' or a[1]=='0' or a[1]=='1' or a[1]=='2' or a[1]=='3' or a[1]=='4' or a[1]=='5' or a[1]=='6' or a[1]=='7' or a[1]=='8' or a[1]=='9':
            return True
    return False
            
def decodeSection(payload):
    #print "len is " + `len(payload)`
        
    r=""
    for i in range(0,len(payload),2):
        a = payload[i] + payload[i+1]  
        # Check that a = a valid hex number
        if isValidHex(a) == False:
            return "DecodingError"
        #print "a is " + a + " integer value of a is " + `int(a)`
        ch = int(a,16)  # ch is a number
        #print "i=" + `i` + " " + `ch`
        b = chr(ch)   
        if b.isalnum():
            r = r + b
            #print "printable : " + b
        else:
            r = r + "."
            #print "result is " + r   
    return r

        
        
        
        
print "This one works OK"        
rawPayload="110a0ce9e9a9588d842c27445018fda056f60000504f4e47206875622e31373030392e6e65740d0a0000000000000000"
print "decodes to " + decodeSection(rawPayload)

print "This one fails"        
rawPayload="^QX0ce9e9a9590b842c28685018fc7c5678^P"
print "decodes to " + decodeSection(rawPayload)

                                                                                                                                                    