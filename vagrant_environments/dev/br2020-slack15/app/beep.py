# This has to be run as root
#print "\xA0"

def beep(frequency, amplitude, duration):
    sample = 8000
    half_period = int(sample/frequency/2)
    beep = chr(amplitude)*half_period+chr(0)*half_period
    beep *= int(duration*frequency)
    audio = file('/dev/audio', 'wb')
    audio.write(beep)
    audio.close()

beep(440, 63, 1)