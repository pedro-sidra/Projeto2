# Melhorias Pendentes

Coisas que ficaram de Projeto 2

## Melhorias na Chapa Fenolite

Tem que ficar mais fácil de tirar

Tem que ser mais repetitível

* Porcas de encaixe nos trilhos
* Borboletas para apertar

## Melhorias nos Post-its

Tem que ficar fixo e ser repetível

* Chapas de MDF com fixação por parafuso borboleta


## Melhorias a discutir

* Iluminação para controle da imagem
* Backlighting

## Alternativa de Apalpador

* Analógico possui 3 graus de liberdade :)

## Comunicação Mach3-Python

* Investigar a alternativa de MODBUS-TCP

## Visão Computacional

* Melhorar o algoritmo de detecção por cor (there must be a better way)
* Não precisar calibrar a cor toda vez

# Requisitos Mínimos

O sistema tem que ser capaz de, no mínimo:

* Realizar usinagem com 4 eixos
    1. Ter um sistema eletromecanico funcional para o eixo A
    2. Comunicar-se com o Mach3
    3. Receber código G com 4 eixos e usinar

* Referenciar automaticamente ferramentas.
* Permitir troca de ferramentas durante operação.
* Interagir com o usuário para troca de ferramentas 

* Referenciar automaticamente a peça em (x,y,z, R), mesmo quando o quarto eixo está ausente

* Referenciar automaticamente o eixo A
    * Apenas para peças com seção transversal retangular ou circular
    * Com interação com o usuário se necessário

# Requisitos Desejáveis

Esses fatores são possivelmente realizáveis, porém não são obrigatórios

* Realizar referenciamento do eixo A para prismas arbitrários
* Realizar toda operação sem interação algum com um ser humano


