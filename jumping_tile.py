#imports
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

#inicio do programa
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

temporizador = pygame.time.Clock()
fps = 60
largura = 720
altura = 720
tela = pygame.display.set_mode((largura, altura))

pygame.display.set_caption('Jumping Tile')

#Definir as fontes de textos
fonte_nome = pygame.font.SysFont('Raleway Black Italic', 30)
fonte = pygame.font.SysFont('Bauhaus 93', 70)
fonte_pontuacao = pygame.font.SysFont('Bauhaus 93', 30)

#Definir as variaveis do jogo
tamanho_do_ladrilho = 36
game_over = 0
main_menu = True
level = 1
pontuacao = 0

#Definir cores
branco = (255, 255, 255)
azul = (0, 0, 255)
vermelho = (255, 0, 0)


#CARREGAR IMAGENS:
logo_jogo = pygame.image.load('img/logotipo.png')
logo_escala = pygame.transform.scale(logo_jogo, (350, 350))
lua_img = pygame.image.load('img/lua.png')
lua_escala = pygame.transform.scale(lua_img, (80, 80))
bg_img = pygame.image.load('img/bg_noite.jpg')
reiniciar_imagem = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

#Carregar sons
pygame.mixer.music.load('img/musica_fundo.wav')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
clique_som = pygame.mixer.Sound('img/clique_som.wav')
moeda_som = pygame.mixer.Sound('img/moeda_som.wav')
pular_som = pygame.mixer.Sound('img/pulo_som.wav')
game_over_som = pygame.mixer.Sound('img/game_over_som.wav')

#Função para escrever texto na tela
def escrever_texto(text, font, text_cor, x, y):
    img = font.render(text, True, text_cor)
    tela.blit(img, (x, y))
    

#Função para redefinir o nível
def reset_level(level):
    jogador.reset(100, altura - 130)
    vilao_grupo.empty()
    moedas_grupo.empty()
    plataforma_grupo.empty()
    larva_grupo.empty()
    exit_grupo.empty()

    #carregar dados de nível e criar mundo
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        dados_cenario = pickle.load(pickle_in)
    cenario = Mundo(dados_cenario)
    pontuacao_moeda = Moedas(tamanho_do_ladrilho//2, tamanho_do_ladrilho//2)
    moedas_grupo.add(pontuacao_moeda)
    return cenario


class Botoes():
    def __init__(self, x, y, imagem):
        self.imagem = imagem
        self.rect= self.imagem.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def Desenhar(self):
        acao = False
        # obtem a posição do mouse
        pos = pygame.mouse.get_pos()

        #verificar as condições do mouse e clicar
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                acao = True
                self.clicked = True
                clique_som.play()
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #desenha o botao
        tela.blit(self.imagem, self.rect)
        
        return acao


def desenhar_grade():
    for linha in range(0, 6):
        pygame.draw.line(tela, (255, 255, 255), (0, linha * tamanho_do_ladrilho), (largura, linha * tamanho_do_ladrilho))
        pygame.draw.line(tela, (255, 255, 255), (linha * tamanho_do_ladrilho, 0), (linha * tamanho_do_ladrilho, altura))

class Jogador():
    def __init__(self, x, y):
        self.reset(x, y)
         
    #função para atualizar
    def update(self, game_over):
        dx = 0
        dy = 0
        tempo_caminhada = 5
        debulhar_colisao = 20

        if game_over == 0:
            #Pressionar as teclas:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.pular == False and self.no_ar == False:
                pular_som.play()
                self.vel_y = - 15
                self.pular = True
            if key[pygame.K_UP] == False:
                self.pular = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direção = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direção = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direção == 1:
                    self.image = self.imagens_direita[self.index]
                if self.direção == -1:
                    self.image = self.imagens_esquerda[self.index]

            #Fazer a animação
            if self.counter > tempo_caminhada:
                self.counter = 0
                self.index +=1 
                if self.index >= len(self.imagens_direita):
                    self.index = 0
                if self.direção == 1:
                    self.image = self.imagens_direita[self.index]
                if self.direção == -1:
                    self.image = self.imagens_esquerda[self.index]

            #Adicionar gravidade
            self.vel_y +=1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #Checar as colisões
            self.no_ar = True
            for ladrilho in cenario.ladrilho_lista:
                #Checar a colisão na direção x
                if ladrilho[1].colliderect(self.rect.x + dx, self.rect.y, self.largura, self.altura):
                    dx = 0
                    
                #checar a colisao na direçao y
                if ladrilho[1].colliderect(self.rect.x, self.rect.y + dy, self.largura, self.altura):
                    #verifique se abaixo do solo e cair
                    if self.vel_y < 0:
                        dy = ladrilho[1].bottom - self.rect.top
                        self.vel_y = 0
                    #verifique se acima do solo e pulando
                    elif self.vel_y >= 0:
                        dy = ladrilho[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.no_ar = False

            #checar colisões com o inimigo 
            if pygame.sprite.spritecollide(self, vilao_grupo, False):
                game_over = -1 
                game_over_som.play()
            #checar colisões com a larva 
            if pygame.sprite.spritecollide(self, larva_grupo, False):
                game_over = -1
                game_over_som.play()

            #checar colisões com a saída 
            if pygame.sprite.spritecollide(self, exit_grupo, False):
                game_over = 1

            #checar a colisão com as plataformas
            for plataform in plataforma_grupo:
                #colisão na direção x
                if plataform.rect.colliderect(self.rect.x + dx, self.rect.y, self.largura, self.altura):
                    dx = 0
                #colisão na direção x
                if plataform.rect.colliderect(self.rect.x, self.rect.y + dy, self.largura, self.altura):
                    #verificar abaixo da plataforma
                    if abs((self.rect.top + dy) - plataform.rect.bottom) < debulhar_colisao:
                        self.vel_y = 0
                        dy = plataform.rect.bottom - self.rect.top
                    #verificar acima da plataforma
                    elif abs((self.rect.bottom + dy) - plataform.rect.top) < debulhar_colisao:
                        self.rect.bottom = plataform.rect.top - 1
                        self.no_ar = False
                        dy = 0
                    #mover o jogador para o lado junto com a plataforma
                    if plataform.mover_x != 0:
                        self.rect.x += plataform.mover_direcao



            #atualizar as coordenadas do jogador
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image

            escrever_texto('GAME OVER!', fonte, vermelho, (largura// 2) - 170, altura// 2)
            if self.rect.y > 20:
                self.rect.y -= 5
                
        #desenhar o jogador na tela
        tela.blit(self.image, self.rect)
        
        return game_over

    def reset(self, x, y):
        self.imagens_direita = []
        self.imagens_esquerda = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_direita = pygame.image.load(rf'img/menina{num}.png') #movimentação do personagem
            img_direita = pygame.transform.scale(img_direita, (27, 54))
            img_esquerda = pygame.transform.flip(img_direita, True, False)
            self.imagens_direita.append(img_direita)
            self.imagens_esquerda.append(img_esquerda)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.imagens_direita[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.largura = self.image.get_width()
        self.altura = self.image.get_height()
        self.vel_y = 0
        self.pular = False
        self.direção = 0
        self.no_ar = True
class Mundo():
    def __init__(self, dados):
        self.ladrilho_lista = []

        #carregar imagens
        ladrilho_imagem = pygame.image.load('img/ladrilho.jpg')
        barra_imagem = pygame.image.load('img/barra.jpg')

        linha_count = 0
        for linha in dados:
            col_count = 0
            for ladrilho in linha:
                if ladrilho == 1:
                    img = pygame.transform.scale(ladrilho_imagem, (tamanho_do_ladrilho, tamanho_do_ladrilho))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tamanho_do_ladrilho
                    img_rect.y = linha_count * tamanho_do_ladrilho
                    ladrilho = (img, img_rect)
                    self.ladrilho_lista.append(ladrilho)
                if ladrilho == 2:
                    img = pygame.transform.scale(barra_imagem, (tamanho_do_ladrilho, tamanho_do_ladrilho))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tamanho_do_ladrilho
                    img_rect.y = linha_count * tamanho_do_ladrilho
                    ladrilho = (img, img_rect)
                    self.ladrilho_lista.append(ladrilho)
                if ladrilho == 3:
                    # 25 para que o inimigo não saia do bloco
                    vilao = Inimigo(col_count * tamanho_do_ladrilho - 25, linha_count * tamanho_do_ladrilho)
                    vilao_grupo.add(vilao)
                if ladrilho == 4:
                    plataforma = Plataforma(col_count * tamanho_do_ladrilho, linha_count * tamanho_do_ladrilho, 1, 0)
                    plataforma_grupo.add(plataforma)
                if ladrilho == 5:
                    plataforma = Plataforma(col_count * tamanho_do_ladrilho, linha_count * tamanho_do_ladrilho, 0, 1)
                    plataforma_grupo.add(plataforma)
                if ladrilho == 6:
                    larva = Larva(col_count * tamanho_do_ladrilho, linha_count * tamanho_do_ladrilho + (tamanho_do_ladrilho//2))
                    larva_grupo.add(larva)
                if ladrilho == 7:
                    moedas = Moedas(col_count * tamanho_do_ladrilho + (tamanho_do_ladrilho//2), linha_count * tamanho_do_ladrilho - (tamanho_do_ladrilho//2))
                    moedas_grupo.add(moedas)
                if ladrilho == 8:
                    exit = Exit(col_count * tamanho_do_ladrilho, linha_count * tamanho_do_ladrilho - (tamanho_do_ladrilho//2))
                    exit_grupo.add(exit)
                col_count += 1
            linha_count += 1
    def bloco(self):
        for ladrilho in self.ladrilho_lista:
            tela.blit(ladrilho[0], ladrilho[1])
            #pygame.draw.rect(tela, (255, 255, 255), ladrilho[1], 2)

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mover_direcao = 1
        self.movimento_contador = 0
    
    def update(self):
        self.rect.x += self.mover_direcao
        self.movimento_contador +=1 
        if abs(self.movimento_contador) > 50:
            self.mover_direcao *= -1
            self.movimento_contador *= -1

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, mover_x, mover_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/plataforma_movimento.jpg')
        self.image = pygame.transform.scale(img, (tamanho_do_ladrilho, tamanho_do_ladrilho//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movimento_contador = 0
        self.mover_direcao = 1
        self.mover_x = mover_x
        self.mover_y = mover_y

    def update(self):
        self.rect.x += self.mover_direcao * self.mover_x
        self.rect.y += self.mover_direcao * self.mover_y
        self.movimento_contador +=1
        if abs(self.movimento_contador) > 50:
            self.mover_direcao *= -1
            self.movimento_contador *= -1
            

class Larva(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tamanho_do_ladrilho, tamanho_do_ladrilho//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tamanho_do_ladrilho, int(tamanho_do_ladrilho * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Moedas(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tamanho_do_ladrilho//2, int(tamanho_do_ladrilho//2)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    

jogador = Jogador(100, altura - 116)

vilao_grupo = pygame.sprite.Group()
plataforma_grupo = pygame.sprite.Group()
larva_grupo = pygame.sprite.Group()
moedas_grupo = pygame.sprite.Group()
exit_grupo = pygame.sprite.Group()

#Criar moeda fictícia para mostrar a pontuação
pontuacao_moeda = Moedas(tamanho_do_ladrilho // 2, tamanho_do_ladrilho//2)
moedas_grupo.add(pontuacao_moeda)


#carregar dados de nível e criar mundo
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    dados_cenario = pickle.load(pickle_in)
cenario = Mundo(dados_cenario)

#criar botoes:
reiniciar_botao = Botoes(largura // 2 - 50, altura // 2 + 100, reiniciar_imagem)
start_botao = Botoes(largura // 2 - 300, (altura//2) + 80, start_img)
exit_botao = Botoes(largura // 2 + 55, (altura//2) + 80, exit_img)

#main
#Criar variável para o jogo rodar:
run = True
while run: 
    #Corrige a taxa de quadros para garantir consistência ao jogo (mesmo tempo em cada computador)
    temporizador.tick(fps)
    tela.blit(bg_img, (0, 0))
    tela.blit(lua_escala, (50, 60))



    #ativar os botões
    if main_menu == True:
        tela.blit(logo_escala, (180, 20))
        escrever_texto('Feito por: Evellyn Rodrigues', fonte_pontuacao, branco, 185, 650)

        if exit_botao.Desenhar() == True:
            run = False

        if start_botao.Desenhar():
            main_menu = False		
        
    else:
        cenario.bloco()
    
        if game_over == 0:
            #para parar as animações
            vilao_grupo.update()
            plataforma_grupo.update()
            #atualizaçao de pontuação
            #verifique se a moeda foi coletada
            if pygame.sprite.spritecollide(jogador, moedas_grupo, True):
                pontuacao += 1
                moeda_som.play()
            escrever_texto('X' + str(pontuacao), fonte_pontuacao, branco, tamanho_do_ladrilho - 10, 5)

        vilao_grupo.draw(tela)
        plataforma_grupo.draw(tela)
        larva_grupo.draw(tela)
        moedas_grupo.draw(tela)
        exit_grupo.draw(tela)

        game_over = jogador.update(game_over)

        #se o jogador morrer
        if game_over == -1:
            if reiniciar_botao.Desenhar():
                dados_cenario = []
                jogador.reset(100, altura - 116)
                game_over = 0
                pontuacao -= 1
        try:

            #se o jogador completar o nivel
            if game_over == 1:
                #reiniciar o jogo e ir para o próximo nível
                level += 1
                dados_cenario = []
                cenario = reset_level(level)
                game_over = 0
            escrever_texto(f'NÍVEL: {level}', fonte_pontuacao, branco, tamanho_do_ladrilho + 550, 5)

        except UnboundLocalError:
            escrever_texto('VOCÊ GANHOU!', fonte, vermelho, (largura// 2) - 205, altura// 2)
            escrever_texto(f'Você conseguiu {pontuacao} moedas de um total de 70!', fonte_nome, branco, (largura// 2) - 200, (altura// 2) - 50)
            if reiniciar_botao.Desenhar():
                level = 1
                #reset level
                dados_cenario = []
                cenario = reset_level(level)
                game_over = 0
                pontuacao = 0

    # criar manipulador de eventos para fechar o jogo:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()


pygame.quit()
