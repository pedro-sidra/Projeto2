EspessuraProbe = +0.5
DistApalpBase = -62.3539
offset = 0
Zzero = GetUserDRO(1001) + GetUserDRO(1002) +  EspessuraProbe - DistApalpBase + offset
Code "G0 Z" & Zzero 'manda pra zero pra ver se deu boa
Code "G92 Z0" 'zerou
