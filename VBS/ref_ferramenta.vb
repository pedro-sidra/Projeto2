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

CurrentFeed = GetOemDRO(818) 'guarda o valor do feedrate atual
DoSpinStop()
'----------------------------------------------------
'PARAMETROS PRA MEDIR E SETAR NA HORA DO TESTE
'----------------------------------------------------
'EspessuraProbe = +0.2
Zmax = 108.5    ' Até onde pode descer rápido pra tocar na probe
'-----------------------------------------------------
'CODIGO DE FATO
'-----------------------------------------------------
'Ferramenta:
'-----------------------------------------------------
If GetOemLed(825) <> 0 Then 'verifica se a probe ja ta no terra
    MsgBox "(Erro: Probe aterrada)" 'Mostra mensagem de erro
Else
    Code "F300" 'feedrate pra descer 
    Code "G31Z-" & Zmax 'desce
    While IsMoving()
    Wend
    
    Zfer = GetDro(2) 'armazena o valor medido da ferramenta
    Code "G4 P2"
    Code "G0 Z0" 'manda subir de volta pro zero
    While IsMoving()
    Wend
	SetUserDRO(1001, Zfer)
    Code "G4 P2"
    
End If
'-----------------------------------------------------
'Fim do script!
'-----------------------------------------------------

