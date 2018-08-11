from bottle import route, run
import json
import math
import os


def retornaMaiorArquivo(diretorio):
    if os.path.exists(diretorio) and os.path.isdir(diretorio):
        maior_tamanho = 0
        maior_arquivo = ''
        for arquivo in os.listdir(diretorio):
            tamanho = os.stat(os.path.join(diretorio, arquivo)).st_size
            if tamanho > maior_tamanho:
                maior_tamanho = tamanho
                maior_arquivo = arquivo
        return os.path.join(diretorio, maior_arquivo)
    else:
        print('Caminho especificado não é um diretório ou não existe.')
        exit(1)

def carregarJsonMac():
    diretorio = 'mac_ssid'
    macs = retornaMaiorArquivo(diretorio)
    #Carregando Json Macs
    JsonMacs = open(macs, "r")
    dicMacs = {}
    
    for linha in JsonMacs:
        linha_Formato_Json = json.loads(linha)
        mac = linha_Formato_Json["mac"]
        conjunto_Macs = linha_Formato_Json["ssid"]
        #Formatando lista de entrada com conjunto de SSIDs

        separador = conjunto_Macs.find(",")
        #Verificar se o conjunto de SSID é Maior que 1:

        if separador != (-1):
            conjunto_Macs = conjunto_Macs.replace(" ", "")
            conjunto_Macs = (conjunto_Macs[1:-1]).split(",")
            
            #removendo Duplicadas
            conjunto_Macs = sorted(set(conjunto_Macs))
            if len(conjunto_Macs) > 1:
                dicMacs[mac] = conjunto_Macs
            else:
                continue
        else:
            continue
    JsonMacs.close()
    return dicMacs

def carregarJsonSSIDs():
    diretorio = 'ssid_mac'
    ssids = retornaMaiorArquivo(diretorio)
    #Carregando Json SSIDs
    JsonSSIDs = open(ssids, "r")
    dicSSIDs = {}
    for linha in JsonSSIDs:
        linha_Formato_Json = json.loads(linha)
        
        ssid = (linha_Formato_Json["ssid"]).replace(" ","")
        
        conjunto_SSID = linha_Formato_Json["mac"]
        conjunto_SSID = conjunto_SSID.replace(" ", "")
        conjunto_SSID = (conjunto_SSID[1:-1]).split(",")
        
        #removendo Duplicadas
        conjunto_SSID = sorted(set(conjunto_SSID))
        dicSSIDs[ssid] = conjunto_SSID

    JsonSSIDs.close()
    return dicSSIDs

def retornaFingerprint(mac,dicMacs,dicSSIDs):
    dicFingerprintAnalisada = {}
    dicFingerprintAnalisada[str(mac)] = dicMacs[str(mac)]
    listaMacs = dicMacs.keys()

    dicBase = {}
    dicBase["BD"] = dicSSIDs
    dicBase["QTD_MACS"] = len(dicMacs.keys())
    listaMac_Similaridades = []

    for i in listaMacs:
        dicMac_Similarodade = {}
        if mac == i:
            continue
        dicFingerprintIterada = {}
        dicFingerprintIterada[i] = dicMacs[i]
        similaridade = IDF(dicFingerprintAnalisada,dicFingerprintIterada,dicBase)
        
        #FALTA DEFINIR UMA CONDICONAL PARA VERIFICAR SE EXISTE RELACIOmacParameterNTO ENTRE AS FP.
       
        #dicMac_Similarodade[str(mac) + " - " + str(i)] = str(similaridade*100) + "%"
        dicMac_Similarodade[str(i)] = similaridade
        listaMac_Similaridades.append(dicMac_Similarodade)

    return listaMac_Similaridades

def calcular_Frequencia(ssid,dicionario_de_retorno):
    freq_SSID = dicionario_de_retorno["BD"] 
    qtdMacs = dicionario_de_retorno["QTD_MACS"] 
    return len(freq_SSID[ssid])/qtdMacs

def IDF(fingerprint1,fingerprint2,dic):
    fp_SSID1 = list(fingerprint1.values())[0]
    fp_SSID2 = list(fingerprint2.values())[0]
    
    intercessao = list(set(fp_SSID1) & set(fp_SSID2))

    if len(intercessao) > 0:
        metrica = 0
        metrica2 = 0
        metrica3 = 0
        for i in range(len(intercessao)):
            frequencia = calcular_Frequencia(intercessao[i],dic)
           
            metrica+= (math.log(frequencia))**2
        

        for i in range(len(fp_SSID1)):
            frequencia = calcular_Frequencia(fp_SSID1[i],dic)
            metrica2+= (math.log(frequencia))**2

        for i in range(len(fp_SSID2)):
            frequencia = calcular_Frequencia(fp_SSID2[i],dic)
            metrica3+= (math.log(frequencia))**2

        cosineIDF = metrica/(math.sqrt(metrica2)*math.sqrt(metrica3))
        
        return (round(cosineIDF,2))
    else:
        return (0)

@route('/getsimilaridades/<macParameter>', method='GET')
def getSimilaridades( macParameter="Mystery Recipe" ):
    dicSSID = carregarJsonSSIDs()
    dicMac = carregarJsonMac()
    listaMacs = dicMac.keys()
    dicRetornoAPI = {}
    if macParameter in listaMacs:
        resultadoAnalise = retornaFingerprint(macParameter,dicMac,dicSSID)
        dicRetornoAPI["status"] = "success"
        dicRetornoAPI["data"] = resultadoAnalise
        dicRetornoAPI["message"] = "Returns all Macs with similarity"
        return dicRetornoAPI
    else:
        dicRetornoAPI["status"] = "fail"
        dicRetornoAPI["data"]=0
        dicRetornoAPI["message"] = "Mac address not found"
        return dicRetornoAPI

run(debug=True)
