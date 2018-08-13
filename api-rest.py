from bottle import route, run, response, hook
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
        dicMac_Similaridade = {}
        if mac == i:
            continue
        dicFingerprintIterada = {}
        dicFingerprintIterada[i] = dicMacs[i]
        similaridade = IDF(dicFingerprintAnalisada,dicFingerprintIterada,dicBase)
        
        #FALTA DEFINIR UMA CONDICONAL PARA VERIFICAR SE EXISTE RELACIOmacParameterNTO ENTRE AS FP.
       
        #dicMac_Similaridade[str(mac) + " - " + str(i)] = str(similaridade*100) + "%"
        if(similaridade >= 0.5):
            dicMac_Similaridade["mac"] = str(i)
            dicMac_Similaridade["similaridade"] = similaridade
            listaMac_Similaridades.append(dicMac_Similaridade)

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

def getListOfMacs(dic):
    dicList = dic.keys()
    lista = []
    for i in dicList:
        dicTemp = {}
        dicTemp["mac"] = str(i)
        lista.append(dicTemp)
    return lista

def getListOfSSID(dic):
    dicList = dic.keys()
    lista = []
    for i in dicList:
        dicTemp = {}
        dicTemp["ssid"] = str(i)
        lista.append(dicTemp)
    return lista

@hook('after_request')
def enableCORSAfterRequestHook():
    print ('After request hook.')
    response.headers['Access-Control-Allow-Origin'] = '*'

@route('/getsimilaridades/<macParameter>', method=['GET', 'OPTIONS'])
def getSimilaridades( macParameter="Mystery Recipe" ):
    dicSSID = carregarJsonSSIDs()
    dicMac = carregarJsonMac()
    listaMacs = dicMac.keys()
    dicRetornoAPI = {}
    if macParameter in listaMacs:
        resultadoAnalise = retornaFingerprint(macParameter,dicMac,dicSSID)
        dicRetornoAPI["status"] = "success"
        dicRetornoAPI["data"] = resultadoAnalise
        dicRetornoAPI["message"] = "Return all Macs with similarity"
        return dicRetornoAPI
    else:
        dicRetornoAPI["status"] = "fail"
        dicRetornoAPI["data"]=0
        dicRetornoAPI["message"] = "Mac address not found"
        return dicRetornoAPI

@route('/getallmacs/', method=['GET', 'OPTIONS'])
def getAllMacs():
    dicMac = carregarJsonMac()
    response = getListOfMacs(dicMac)
    dicReturn = {}
    if(len(response) > 0):
        dicReturn["status"] = "success"
        dicReturn["data"] = response
        dicReturn["message"] = "Return all Macs"
    else:
        dicReturn["status"] = "fail"
        dicReturn["data"] = []
        dicReturn["message"] = "There arent macs"
    return dicReturn

@route('/getallssid/', method=['GET', 'OPTIONS'])
def getAllSSID():
    dicMac = carregarJsonSSIDs()
    response = getListOfSSID(dicMac)
    dicReturn = {}
    if(len(response) > 0):
        dicReturn["status"] = "success"
        dicReturn["data"] = response
        dicReturn["message"] = "Return all SSID"
    else:
        dicReturn["status"] = "fail"
        dicReturn["data"] = []
        dicReturn["message"] = "There arent SSID"
    return dicReturn

@route('/getfingerprint/<mac>', method=['GET', 'OPTIONS'])
def getFingerprint(mac="mac"):
    dicMac = carregarJsonMac()
    dicReturn = {}
    dicData = {}
    if(len(dicMac.keys()) > 0):
        fingerprint = dicMac[mac]
        dicData["mac"] = mac
        dicData["ssids"] = fingerprint
        dicReturn["status"] = "success"
        dicReturn["data"] = dicData
        dicReturn["message"] = "Return one fingerprint"
    else:
        dicReturn["status"] = "fail"
        dicReturn["data"] = []
        dicReturn["message"] = "There arent fingerprint for this mac"
    return dicReturn

@route('/getallmacsfromssid/<ssid>', method=['GET', 'OPTIONS'])
def getAllMacsFromSSID(ssid="ssid"):
    dicSSID = carregarJsonSSIDs()
    dicReturn = {}
    dicData = {}
    if(len(dicSSID.keys()) > 0):
        amount_macs = len(dicSSID[ssid])
        dicData["ssid"] = ssid
        dicData["macs"] = dicSSID[ssid]
        dicData["amount_macs"] = amount_macs
        dicReturn["status"] = "success"
        dicReturn["data"] = dicData
        dicReturn["message"] = "Return the amount of Macs of this ssid"
    else:
        dicReturn["status"] = "fail"
        dicReturn["data"] = []
        dicReturn["message"] = "There arent Macs for this ssid"
    return dicReturn

@route('/getpopularityfromallssid/', method=['GET', 'OPTIONS'])
def getPopularityFromAllSSID():
    dicSSID = carregarJsonSSIDs()
    dicReturn = {}
    temp = dicSSID.keys()
    lista = []
    if(len(temp) > 0):
        for ssid in temp:
            dicData = {}
            amount_macs = len(dicSSID[ssid])
            dicData["ssid"] = ssid
            dicData["macs"] = dicSSID[ssid]
            dicData["amount_macs"] = amount_macs
            lista.append(dicData)
        dicReturn["status"] = "success"
        dicReturn["data"] = lista
        dicReturn["message"] = "Return the amount of Macs of this ssid"
    else:
        dicReturn["status"] = "fail"
        dicReturn["data"] = []
        dicReturn["message"] = "There arent Macs for this ssid"
    return dicReturn


run(host="127.0.0.1", debug=True)
