import time

import pygame
import os
import random

TELA_LARGURA = 500
TELA_ALTURA = 700

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))), # asa alta
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))), # asa meio
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))), # asa baixa
]

pygame.font.init()     # Fonte do texto de Pontução
FONTE_PONTOS = pygame.font.SysFont('arial', 50)   #50
FONTE_MENU = pygame.font.SysFont('arial', 30)

class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 28  #25
    VELOCIDADE_ROTACAO = 5  #20
    TEMPO_ANIMACAO = 5   #5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0 # para execução do movimento
        self.contagem_imagem = 0 # para uso de cada imagem
        self.imagem = self.IMGS[0]  # imagem inicial do pássaro

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo  # S = So + Vo.t + at²/2

        # restringir o deslocamento
        if deslocamento > 10:
            deslocamento = 10
        elif deslocamento < 0:
            deslocamento -= 0

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0 or self.y < (self.altura - 10 ):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo += 5
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -60:
            self.imagem = self.IMGS[0]

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)  # cria a imagem rotacionada
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center # pega o centro do retangulo da imagem na primeira posição
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem) # usa o centro do retangulo pra auxiliar a rotação da imagem
        tela.blit(imagem_rotacionada, retangulo.topleft) # printa na tela a imagem

    def get_mask(self): # divide o retangulo em pixels, para melhorar o sistema de colisão
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 180 # Abertura do cano
    VELOCIDADE = 7 # Velocidade que o Cano 'anda'

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True) # False para eixo x / True para flipar no eixo Y
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 400)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo) # defini a colisão, caso haja 2 pixel sobrepostos
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)
        # retorna um True ou False, caso exista um ponto de colisão do passaro com o cano

        if base_ponto or topo_ponto:    # Caso haja colisão
            return True                 # Retorne que houve colisão
        else:                           # Caso nao haja colisão
            return False                # Retorne que não há colisão


class Chao:
    VELOCIDADE = 7
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))



def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, -150))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255)) # 1 pra deixar o numero nao pixelado, (255,255,255) cor em RGB
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()

''' função não funcionando corretamente
def reiniciar(tela,menu,chao,pontos,cano,canos):
    espera = True
    while espera:
        tela.blit(IMAGEM_BACKGROUND, (0, -150))
        texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
        tela.blit(texto, (TELA_LARGURA - menu.get_width() - 40, TELA_ALTURA / 2 + 30))
        menu = FONTE_MENU.render(f"Aperte Barra de Espaço para Reiniciar", 0, (255, 255, 255))
        tela.blit(menu, (TELA_LARGURA - menu.get_width() - 40, TELA_ALTURA / 2 - 70))
        chao.desenhar(tela)
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    pontos = 0
                    passaros = [Passaro(150, 350)]
                    canos.remove(cano)
                    canos.append(Cano(600))
                    espera = False
'''

def main():
    passaros = [Passaro(150, 350)] # cria o passaro na posição 200,350
    chao = Chao(670)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA)) # cria a tela do tamanho definido no inicio
    pontos = 0
    relogio = pygame.time.Clock() # tempo de atualização da tela  por segundo (inclusa do pygame)

    espera = True
    rodando = False
    while espera:
        tela.blit(IMAGEM_BACKGROUND, (0, -150))
        menu = FONTE_MENU.render(f"Aperte Barra de Espaço para Iniciar", 0, (255, 255, 255)) # 1 pra deixar o numero nao pixelado, (255,255,255) cor em RGB
        tela.blit(menu, (TELA_LARGURA - menu.get_width() -40 , TELA_ALTURA/2 - 70))
        chao.desenhar(tela)
        pygame.display.update()

        for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        espera = False
                        rodando = True

    while rodando:
        relogio.tick(30) # 30 FPS

        # interação com o usuário
        for evento in pygame.event.get():  # FAZ UMA LISTA COM OS EVENTOS DO PYGAME
            if evento.type == pygame.QUIT:  # Quando apertar no X na aba superior
                rodando = False
                pygame.quit()         # fecha o programa
                quit()
            if evento.type == pygame.KEYDOWN:  # Quando apertar uma tecla, faz uma interação
                if evento.key == pygame.K_SPACE:  # se apertar SPACE
                    for passaro in passaros:
                        passaro.pular()          # o comando pular é executado

        # mover as coisas
        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)

                    espera = True     # função reiniciar()
                    while espera:
                        tela.blit(IMAGEM_BACKGROUND, (0, -150))
                        texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
                        tela.blit(texto, (TELA_LARGURA - menu.get_width() - 40, TELA_ALTURA / 2 + 30))
                        menu = FONTE_MENU.render(f"Aperte Barra de Espaço para Reiniciar", 0, (255, 255, 255))
                        tela.blit(menu, (TELA_LARGURA - menu.get_width() - 40, TELA_ALTURA / 2 - 70))
                        chao.desenhar(tela)
                        pygame.display.update()

                        for evento in pygame.event.get():
                            if evento.type == pygame.KEYDOWN:
                                if evento.key == pygame.K_SPACE:
                                    pontos = 0
                                    passaros = [Passaro(150, 350)]
                                    remover_canos = []
                                    canos.remove(cano)
                                    canos = [Cano(700)]
                                    espera = False

                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)

                espera = True # função reiniciar()
                while espera:
                    tela.blit(IMAGEM_BACKGROUND, (0, -150))
                    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
                    tela.blit(texto, (TELA_LARGURA - menu.get_width() - 40, TELA_ALTURA / 2 + 30))
                    menu = FONTE_MENU.render(f"Aperte Barra de Espaço para Reiniciar", 0, (255, 255, 255))
                    tela.blit(menu, (TELA_LARGURA - menu.get_width() - 40, TELA_ALTURA / 2 - 70))
                    chao.desenhar(tela)
                    pygame.display.update()

                    for evento in pygame.event.get():
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_SPACE:
                                pontos = 0
                                passaros = [Passaro(150, 350)]
                                remover_canos = []
                                canos.remove(cano)
                                canos = [Cano(700)]
                                espera = False


        desenhar_tela(tela, passaros, canos, chao, pontos)


if __name__ == '__main__':
    main()
