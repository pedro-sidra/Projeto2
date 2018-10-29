from GCodeGenerator import *
import numpy as np
import time
import cv2

# Teste de comunicacao com o Mach3!

# Ideia: este programa escreve um cod. G com uma coordenada,
# espera o Mach3 executar esse codigo e chegar ate a coordenada,
# e entao escreve outro codigo G para voltar pra posicao inicial

def waitForOK():
    receivedOk = False
    while not receivedOk:
        with open('fromMach3.txt','r') as fFromMach3:
            text = fFromMach3.readline()
            print('text ' + text)
            time.sleep(0.3)
        if text == 'ok\n':
            receivedOk=True
            open('fromMach3.txt','w').close()

# Comunicacao feita com arquivos de texto (aham...)
def main():
    
    # gerador de codigo G (clauser <3)
    gc = GCodeGenerator(5)
    # se der problema de acesso:if os.access("myfile", os.R_OK):
    open('fromMach3.txt','w').close()
    open('toMach3.txt','w').close()

    # Limpa o arquivo, e espera o Mach3 dar um ok
    gc.cleanFile()
    gc.getInitialCode()
    gc.moveLinear(Point(2,2,2), feed_rate=500)
    waitForOK()
    
    # Manda um movimento, e espera o Mach3 dar um ok
    gc.cleanFile()
    gc.getInitialCode()
    gc.moveLinear(Point(0,0,0), feed_rate=500)
    waitForOK()

    # Manda outro movimento, espera o mach3 dar ok
    gc.cleanFile()
    gc.getInitialCode()

    gc.moveLinear(Point(1,1,1),feed_rate = 1000)
    waitForOK()


if __name__ == "__main__":
    main()
