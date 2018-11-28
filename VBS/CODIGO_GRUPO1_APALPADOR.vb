'Script para testar o referenciamento da altura de uma peça
'Estrutura do script:
'1) Assume-se máquina sobre a peça
'2) Sobe-se em Z para possibilitar uso da probe até uma altura Zsafe
'3) Atua-se no servo para rotacionar a probe de forma que fique para baixo
'2) Desce o eixo Z (Z--) até tocar na probe, guardando esse valor como Zpiece
'3) Sobe o eixo Z (Z++) até Zsafe novamente
'4) Salva altura da peça como Zpiece + (comprimento da probe)
'
'-------------------
'https://vdocuments.mx/reference-tables-for-normal-and-oem-codes.html
'-------------------
CurrentFeed = GetOemDRO(818) 'guarda o valor do feedrate atual
DoSpinStop() 
'-----------------------------------------------------
'PARAMETROS PRA MEDIR E SETAR NA HORA DO TESTE
'-----------------------------------------------------
'ComprimentoProbe = 200 
Zmax = 100
'-----------------------------------------------------
'Apalpador:
'-----------------------------------------------------
If GetOemLed(825) <> 0 Then 'verifica se a probe ja ta no terra
    Code "(Erro: Probe aterrada)" 'Mostra mensagem de erro
Else 
    'Desce e pega leitura de probe
    Code "F300" 'feedrate pra descer
    Code "G31Z-" & Zmax 'desce até tocar o apalpador
    While IsMoving()
    Wend
    Zpiece = GetDro(2) 'armazena o valor medido pelo apalpador
    SetUserDRO(1002, Zpiece)
    Code "G0 Z0" 'sobe até zero pra recolher apalpador
    


End If


'-----------------------------------------------------
'Fim do script!
'-----------------------------------------------------
