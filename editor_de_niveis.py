import pygame
import pickle
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

# janela do jogo
tamanho_do_ladrilho = 32
cols = 20
margem = 100
largura = tamanho_do_ladrilho * cols
altura = (tamanho_do_ladrilho * cols) + margem

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Editor de nível')


#carregar images
bg_img = pygame.image.load('img/bg_noite.jpg')
bg_img = pygame.transform.scale(bg_img, (largura, altura - margem))
ladrilho_img = pygame.image.load('img/ladrilho.jpg')
barra_img = pygame.image.load('img/barra.jpg')
vilao_img = pygame.image.load('img/blob.png')
platform_x_img = pygame.image.load('img/plataforma_x.png')
platform_y_img = pygame.image.load('img/plataforma_y.png')
larva_img = pygame.image.load('img/lava.png')
coin_img = pygame.image.load('img/coin.png')
exit_img = pygame.image.load('img/exit.png')
save_img = pygame.image.load('img/save_btn.png')
load_img = pygame.image.load('img/load_btn.png')


#variáveis do jogo
clicked = False
level = 1

#cores
branco = (255, 255, 255)
verde = (144, 201, 120)

font = pygame.font.SysFont('Futura', 24)

#criar lista de blocos vazios
dados_cenario = []
for linha in range(20):
	l = [0] * 20
	dados_cenario.append(l)

#criar limite
for ladrilho in range(0, 20):
	dados_cenario[19][ladrilho] = 2
	dados_cenario[0][ladrilho] = 1
	dados_cenario[ladrilho][0] = 1
	dados_cenario[ladrilho][19] = 1

#função para saída de texto na tela
def desenhar_texto(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	tela.blit(img, (x, y))

def desenhar_grade():
	for c in range(21):
		#linhas verticais
		pygame.draw.line(tela, branco, (c * tamanho_do_ladrilho, 0), (c * tamanho_do_ladrilho, altura - margem))
		#linhas horizontais
		pygame.draw.line(tela, branco, (0, c * tamanho_do_ladrilho), (largura, c * tamanho_do_ladrilho))


def desenhar_cenario():
	for linha in range(20):
		for col in range(20):
			if dados_cenario[linha][col] > 0:
				if dados_cenario[linha][col] == 1:
					#blocos de ladrilhos
					img = pygame.transform.scale(ladrilho_img, (tamanho_do_ladrilho, tamanho_do_ladrilho))
					tela.blit(img, (col * tamanho_do_ladrilho, linha * tamanho_do_ladrilho))
				if dados_cenario[linha][col] == 2:
					#blocos de barras
					img = pygame.transform.scale(barra_img, (tamanho_do_ladrilho, tamanho_do_ladrilho))
					tela.blit(img, (col * tamanho_do_ladrilho, linha * tamanho_do_ladrilho))
				if dados_cenario[linha][col] == 3:
					#blocos dos inimigos
					img = pygame.transform.scale(vilao_img, (tamanho_do_ladrilho, int(tamanho_do_ladrilho * 0.75)))
					tela.blit(img, (col * tamanho_do_ladrilho, linha * tamanho_do_ladrilho + (tamanho_do_ladrilho * 0.25)))
				if dados_cenario[linha][col] == 4:
					#mover plataforma horizontalmente
					img = pygame.transform.scale(platform_x_img, (tamanho_do_ladrilho, tamanho_do_ladrilho // 2))
					tela.blit(img, (col * tamanho_do_ladrilho, linha * tamanho_do_ladrilho))
				if dados_cenario[linha][col] == 5:
					#mover a plataforma verticalmente
					img = pygame.transform.scale(platform_y_img, (tamanho_do_ladrilho, tamanho_do_ladrilho // 2))
					tela.blit(img, (col * tamanho_do_ladrilho, linha * tamanho_do_ladrilho))
				if dados_cenario[linha][col] == 6:
					#larvas
					img = pygame.transform.scale(larva_img, (tamanho_do_ladrilho, tamanho_do_ladrilho // 2))
					tela.blit(img, (col * tamanho_do_ladrilho, linha * tamanho_do_ladrilho + (tamanho_do_ladrilho // 2)))
				if dados_cenario[linha][col] == 7:
					#moedas
					img = pygame.transform.scale(coin_img, (tamanho_do_ladrilho // 2, tamanho_do_ladrilho // 2))
					tela.blit(img, (col * tamanho_do_ladrilho + (tamanho_do_ladrilho // 4), linha * tamanho_do_ladrilho + (tamanho_do_ladrilho // 4)))
				if dados_cenario[linha][col] == 8:
					#saida
					img = pygame.transform.scale(exit_img, (tamanho_do_ladrilho, int(tamanho_do_ladrilho * 1.5)))
					tela.blit(img, (col * tamanho_do_ladrilho, linha * tamanho_do_ladrilho - (tamanho_do_ladrilho // 2)))



class Botoes():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def desenhar(self):
		acao = False

		#obter a posição do mouse
		pos = pygame.mouse.get_pos()

		#verificar quando o mouse for clicado
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				acao = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#desenhar o botão
		tela.blit(self.image, (self.rect.x, self.rect.y))

		return acao

#criar imagens e salvar botões
save_button = Botoes(largura // 2 - 150, altura - 80, save_img)
load_button = Botoes(largura // 2 + 50, altura - 80, load_img)

#main
run = True
while run:

	clock.tick(fps)

	#desenhar o fundo
	tela.fill(verde)
	tela.blit(bg_img, (0, 0))

	#salvar os níveis
	if save_button.desenhar():
		#save os níveis em arquivos binarios
		pickle_out = open(f'level{level}_data', 'wb')
		pickle.dump(dados_cenario, pickle_out)
		pickle_out.close()
	if load_button.desenhar():
		#carregar os níveis
		if path.exists(f'level{level}_data'):
			pickle_in = open(f'level{level}_data', 'rb')
			dados_cenario = pickle.load(pickle_in)


	#desenhar grade e blocos de nível
	desenhar_grade()
	desenhar_cenario()


	#Mostrar o nível atual
	desenhar_texto(f'Level: {level}', font, branco, tamanho_do_ladrilho, altura - 60)
	desenhar_texto('Press UP or DOWN to change level', font, branco, tamanho_do_ladrilho, altura - 40)

	#manipula os eventos
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		#clicar no mouse para alterar os blocos
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tamanho_do_ladrilho
			y = pos[1] // tamanho_do_ladrilho
			#verificar se as coordenadas estão dentro da área do bloco
			if x < 20 and y < 20:
				#atualiza o bloco
				if pygame.mouse.get_pressed()[0] == 1:
					dados_cenario[y][x] += 1
					if dados_cenario[y][x] > 8:
						dados_cenario[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					dados_cenario[y][x] -= 1
					if dados_cenario[y][x] < 0:
						dados_cenario[y][x] = 8
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#pressiona a tecla para cima e para baixo para alterar o número de nível
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	pygame.display.update()

pygame.quit()
