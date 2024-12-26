#optimized morse lookup table
def toMorse(text):
    morse = ""
    for x in text:
        match x:
            case 'a':
                morse += ".-"
            case 'b':
                morse += "-..."
            case 'c':
                morse += "-.-."
            case 'd':
                morse += "-.."
            case 'e':
                morse += "."
            case 'f':
                morse += "..-."
            case 'g':
                morse += "--."
            case 'h':
                morse += "...."
            case '1':
                morse += ".----"
            case '2':
                morse += "..---"
            case '3':
                morse += "...--"
            case '4':
                morse += "....-"
            case '5':
                morse += "....."
            case '6 ':
                morse += "-...."
            case '7':
                morse += "--..."
            case '8':
                morse += "---.."
        morse += "/"
    return morse

