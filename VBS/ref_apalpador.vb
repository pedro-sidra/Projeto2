'Script para testar o referenciamento do eixo Z de uma máquina CNC
'Estrutura do script:
'1) Assume-se máquina no home e uma probe posicionada sob a ferramenta
'2) Desce o eixo Z (Z--) até tocar na probe, guardando esse valor como Zfer
'3) Sobe o eixo Z (Z++) até Z=0 novamente
'4) Desloca a máquina 50 mm em X e 50 mm em Y (Posição arbitrária para a peça)*
'5) Para por algum tempo para alguém girar o apalpador manualmente**
'6) Desce o eixo Z até receber sinal do botão***, guarda valor como Zapalp
'7) Sobe 10 mm por segurança e para, pra recolher o apalpador
'8) Calcula novo zero pela eq: Zzero = Zfer + Zapalp + EspessuraProbe - DistApalpBase
'9) Manda pro novo zero pra ver se ficou bom\
'10) Reza pra máquina parar
'11) ???
'3) Profit!
'
'Depois esses valores vem da visão computacional
'Depois vai ser com o servo
'O sinal é recebido pelo Mach3 como se fosse o mesmo da probe
'
'------------------
'
'------------------
CurrentFeed = GetOemDRO(818) 'guarda o valor do feedrate atual
DoSpinStop() 
'----------------------------------------------------
'PARAMETROS PRA MEDIR E SETAR NA HORA DO TESTE
'----------------------------------------------------
DistApalpBase = -62.3539
Zmax = 108.5    'Até aonde dá pra descer rápido pra tocar na probe
ZOffset = 10.00 'quanto subir por segurança, dá pra mudar se precisar
'-----------------------------------------------------
'Apalpador:
'-----------------------------------------------------
If GetOemLed(825) <> 0 Then 'verifica se a probe ja ta no terra
    MsgBox "(Erro: apalpador aterrado)" 'Mostra mensagem de erro
Else 
    Code "G0 X50 Y50" 'manda pra cima da peça arbitraria
    Code "G4 P5" 'para por 5 segundos pra poder girar o apalpador
    Code "F300" 'feedrate pra descer
    Code "G31Z-" & Zmax 'desce até tocar o apalpador
    While IsMoving()
    Wend
    Zapalp = GetDro(2) 'armazena o valor medido pelo apalpador
    Code "G0 Z" & (Zapalp+ZOffset) 'sobe ZOffset [mm] pra recolher apalpador
    Code "G4 P5" 'para + 5 segundos pra recolher
    While IsMoving()
    Wend
End If
    
'-----------------------------------------------------
'Fim do script!
'-----------------------------------------------------