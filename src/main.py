import re
import random
import csv
import math

# converte para minúsculo e pega as palavras por regex
def carregar_palavras(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        texto = f.read().lower()
    return re.findall(r'[a-záàâãéèêíïóôõöúçñ]+', texto)

# tira palavras repetidas sem usar set/dict (regra do pdf)
def palavras_unicas(lista):
    unicas = []
    for p in lista:
        if p not in unicas:
            unicas.append(p)
    return unicas

# Funções de Hash 

def h_soma(p): # H1: soma o valor ascii
    return sum(ord(c) for c in p)

def h_posicional(p): # H2: posicional (evita colisao em anagramas)
    return sum((i+1)*ord(c) for i, c in enumerate(p))

def h_polinomial(p, R=31): # H3: metodo polinomial (constante 31)
    h = 0
    for c in p:
        h = R*h + ord(c)
    return h

def h_xor(p): # H4: mistura os bits com shift
    h = 0
    for c in p:
        h ^= (h << 5) + (h >> 2) + ord(c)
    return h

def h_ruim(p): # Hash ruim proposital (pega só a 1a letra)
    return ord(p[0])



# Tabela Hash (encadeamento separado)
class Hash:
    def __init__(self, M, func):
        self.M = M
        self.func = func
        self.tabela = [[] for _ in range(M)]  # buckets vazios
        self.comp = 0  # contador de comparações

    # calcula o indice
    def idx(self, p):
        return self.func(p) % self.M

    def put(self, p):
        b = self.tabela[self.idx(p)]
        for x in b:
            self.comp += 1
            if x == p: # se ja tem, ignora
                return
        b.append(p)

    def contains(self, p):
        b = self.tabela[self.idx(p)]
        for x in b:
            self.comp += 1
            if x == p:
                return True
        return False

    # zera o contador antes de cada teste
    def reset(self):
        self.comp = 0

# Estrutura linear para baseline
class Linear:
    def __init__(self):
        self.dados = []
        self.comp = 0

    def put(self, p):
        if not self.contains(p):
            self.dados.append(p)

    def contains(self, p):
        for x in self.dados:
            self.comp += 1
            if x == p:
                return True
        return False

    def reset(self):
        self.comp = 0


#Métricas e Auxiliares

def max_bucket(tabela):
    return max(len(b) for b in tabela)

def histograma(tabela):
    return [len(b) for b in tabela]

def desvio_padrao(valores):
    media = sum(valores)/len(valores)
    var = sum((x-media)**2 for x in valores)/len(valores)
    return math.sqrt(var)

# gera palavras aleatorias para testar falha na busca
def gerar_falha(base, q=1000):
    out = []
    while len(out) < q:
        p = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(5))
        if p not in base:
            out.append(p)
    return out

# cria o csv com as colunas exigidas
def iniciar_csv():
    cabecalho = [
        'texto', 'M', 'hash_name', 'n', 'alpha',
        'max_bucket', 'avg_bucket', 'std_dev',
        'total_comp_success', 'avg_comp_success',
        'total_comp_fail', 'avg_comp_fail',
        'lin_total_comp_success', 'lin_avg_comp_success',
        'lin_total_comp_fail', 'lin_avg_comp_fail'
    ]
    with open('resultados.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(cabecalho)

def salvar(linha):
    with open('resultados.csv', 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(linha)

#Execução Principal

def executar(arq, nome):
    palavras = carregar_palavras(arq)
    unicas = palavras_unicas(palavras)
    n = len(unicas)

    funcoes = {
        'H1_soma': h_soma,
        'H2_posicional': h_posicional,
        'H3_polinomial': h_polinomial,
        'H4_xor': h_xor,
        'H_ruim': h_ruim
    }

    # tamanhos de M do roteiro
    for M in [97, 100, 997]:
        for nome_hash, f in funcoes.items():

            h = Hash(M, f)
            for p in unicas:
                h.put(p)

            # calcula metricas
            hist = histograma(h.tabela)
            dp = desvio_padrao(hist)
            alpha = n / M
            avg_bucket = alpha # a media do bucket é o proprio alpha

            # busca com sucesso
            h.reset()
            for p in unicas:
                h.contains(p)
            suc_total = h.comp
            suc_avg = suc_total / n

            # busca com falha
            falha_lista = gerar_falha(unicas)
            qtd_falha = len(falha_lista)
            h.reset()
            for p in falha_lista:
                h.contains(p)
            fal_total = h.comp
            fal_avg = fal_total / qtd_falha

            # baseline na lista linear (demora muito por causa da busca sequencial)
            lin = Linear()
            for p in unicas:
                lin.put(p)

            lin.reset()
            for p in unicas:
                lin.contains(p)
            lin_suc_total = lin.comp
            lin_suc_avg = lin_suc_total / n

            lin.reset()
            for p in falha_lista:
                lin.contains(p)
            lin_fal_total = lin.comp
            lin_fal_avg = lin_fal_total / qtd_falha

            # salva no csv
            salvar([
                nome, M, nome_hash, n, alpha,
                max_bucket(h.tabela), avg_bucket, dp,
                suc_total, suc_avg,
                fal_total, fal_avg,
                lin_suc_total, lin_suc_avg,
                lin_fal_total, lin_fal_avg
            ])

if __name__ == '__main__':
    iniciar_csv()
    executar('tale.txt', 'tale')
    executar('quincas_borba.txt', 'quincas')
