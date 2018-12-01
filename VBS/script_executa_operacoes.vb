' ----------------------------FAZENDO HOME--------------------------------------
If GetUserLED(1200) Then
MsgBox "Doing Home"
DoButton( 24 )
DoButton( 23 )
DoButton( 22 )
DoButton( 25 )

DoOEMButton(133)
DoOEMButton(134)
DoOEMButton(135)
x = getOEMDRO(83)
While x <>0
	x = getOEMDRO(83)
Wend
While IsMoving()
Wend

Sleep(1000)
End If


' -------------------------FAZENDO FERRAMENTA-----------------------------------------
If GetUserLED(1201) Then
MsgBox "Doing Tool"

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
Zmax = 120    ' Até onde pode descer rápido pra tocar na probe
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

MsgBox("Referenced Tool")
x = getuserDRO(1001)
MsgBox(x)
Sleep(1000)
End If


' ---------------------------FAZENDO XY---------------------------------------
If GetUserLED(1202) Then
MsgBox("Doing X-Y")

Dim compok 'verifica se a String lida no arquivo é "ok"
Dim compexit 'verifica se a String lida no arquivo é "exit"
compok = 1
compexit = 1

While compexit <> 0
	Open "C:\Users\Pedro\Documents\Code\Projeto2\toMach3.txt" For Input As #1 ' abre arquivo.
	Line Input #1, TextLine ' lê a linha e coloca na variavel TextLine. 
	Close #1 ' fecha o arquivo
	
	compok = StrComp("ok",TextLine)
	compexit = StrComp("exit",TextLine)
	
	If compok = 0 Then 'se a string for "ok"
	
		LoadFile("C:\Users\Pedro\Documents\Code\Projeto2\out.tap") 'carrega o código G

		While IsLoading()
		Wend
		
		RunFile() 'Executa
		sleep(500)
		DoOEMButton(1000) 'Pressiona o botão Cycle Start
		 
		While isMoving() 'Trava a execução enquanto a CNC estiver executando instruções
			Sleep 100
		Wend
		DoOEMButton(169) 'Pressiona o botão close file
		
		sleep(500)
		
		Open "C:\Users\Pedro\Documents\Code\Projeto2\fromMach3.txt" For Output As #1 ' Open file.
		Print #1, "ok" ' escreve a string para o arquivo
		Close
	
	End If 
	Sleep(1000)

Wend
MsgBox "Done XY"
MsgBox("Doing Piece Z")
'--------------------------APALPANDO---------------------------
'-------------------
CurrentFeed = GetOemDRO(818) 'guarda o valor do feedrate atual
DoSpinStop() 
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
Open "C:\Users\Pedro\Documents\Code\Projeto2\fromMach3.txt" For Output As #1 ' Open file.
Print #1, "ok" ' escreve a string para o arquivo
Close
MsgBox("Done piece Z")
EspessuraProbe = +0.5
DistApalpBase = -62.3539
offset = -5
Zzero = GetUserDRO(1001) + GetUserDRO(1002) +  EspessuraProbe - DistApalpBase + offset
Code "G0 X20 Y20 Z" & Zzero 'manda pra zero pra ver se deu boa
Code "G92 Z0" 'zerou

Sleep(1000)
End If 