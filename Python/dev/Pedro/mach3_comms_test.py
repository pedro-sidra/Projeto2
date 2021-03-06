from proj2.GCodeGenerator.GCodeGenerator import *
import time


# Teste de comunicacao com o Mach3!

# Ideia: este programa escreve um cod. G com uma coordenada,
# espera o Mach3 executar esse codigo e chegar ate a coordenada,
# e entao escreve outro codigo G para voltar pra posicao inicial

def waitForOK():
    receivedOk = False
    while not receivedOk:
        with open('fromMach3.txt', 'r') as fFromMach3:
            text = fFromMach3.readline()
            print('text ' + text)
            time.sleep(0.3)
        if text == 'ok\n':
            receivedOk = True
            open('fromMach3.txt', 'w').close()


def sendOK():
    with open('toMach3.txt', 'w') as fToMach3:
        fToMach3.write('ok')


def clearOK():
    open('toMach3.txt', 'w').close()


def waitForMach3():
    sendOK()
    waitForOK()
    clearOK()


# Comunicacao feita com arquivos de texto (aham...)
def sendGcodeAndWaitForMach3():
    # gerador de codigo G (clauser <3)
    gc = GCodeGenerator(5)

    # se der problema de acesso:if os.access("myfile", os.R_OK):
    open('fromMach3.txt', 'w').close()
    clearOK()

    # Limpa o arquivo, manda um ok, e espera o Mach3 dar um ok
    gc.cleanFile()
    gc.getInitialCode()
    gc.moveLinear(Point(100, 100, 0), feed_rate=500)
    gc.insertNewLine()

    waitForMach3()

    # Manda um movimento, e espera o Mach3 dar um ok
    gc.cleanFile()
    gc.moveLinear(Point(0, 0, 0), feed_rate=500)
    gc.insertNewLine()

    waitForMach3()

    # Manda outro movimento, espera o mach3 dar ok
    gc.cleanFile()
    gc.moveLinear(Point(100, 100, 0), feed_rate=1000)
    gc.insertNewLine()

    waitForMach3()


def main():
    sendGcodeAndWaitForMach3()


if __name__ == "__main__":
    main()
