from PIL import Image, ImageDraw, ImageFont
import requests
import os
from datetime import datetime

# LISTA DE CAMPEONATOS DE FUTEBOL A SEREM PROCESSADOS
CHAMPIONSHIPS = [
    "soccer_uefa_champs_league",
    "soccer_conmebol_copa_libertadores",
    "soccer_brazil_campeonato",
]

# CHAVE DA API
API_KEY = "MUDE A API"

#######################ALTERE OS DIRETORIOS########################


# DIRETÓRIO DE SAÍDA PARA IMAGENS GERADAS
OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Área de Trabalho', 'gerarimg', 'imagens_jogos')
os.makedirs(OUTPUT_DIR, exist_ok=True)
# CAMINHO PARA A IMAGEM DE FUNDO PADRÃO
DEFAULT_BACKGROUND_PATH = "C:/Users/rafae/OneDrive/Área de Trabalho/gerarimg/background/default_background.jpg"
# CARREGAR A FONTE
FONT_PATH = "C:/Users/rafae/OneDrive/Área de Trabalho/gerarimg/teste.ttf"
FONT_SIZE = 40
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)

def draw_text_with_shadow(draw, text, position, font, fill, shadow_offset=(2, 2), shadow_color=(0, 0, 0)):
    # DESENHAR TEXTO COM SOMBRA
    shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
    draw.text(shadow_position, text, font=font, fill=shadow_color)
    draw.text(position, text, font=font, fill=fill)

# CRIANDO IMAGENS PARA CADA CAMPEONATO
for championship in CHAMPIONSHIPS:
    try:
        # TENTAR CARREGAR A IMAGEM DE FUNDO ESPECÍFICA
        background_path = f"C:/Users/rafae/OneDrive/Área de Trabalho/gerarimg/background/{championship}.jpg"
        try:
            background = Image.open(background_path)
        except FileNotFoundError:
            # SE NÃO ENCONTRAR A IMAGEM ESPECÍFICA, USA A PADRÃO
            background = Image.open(DEFAULT_BACKGROUND_PATH)

        # FAZ A REQUISIÇÃO À API
        response = requests.get(f"https://api.the-odds-api.com/v4/sports/{championship}/odds?regions=uk&apiKey={API_KEY}")
        response.raise_for_status()
        data = response.json()

        # CRIAR UMA PASTA PARA O CAMPEONATO
        championship_dir = os.path.join(OUTPUT_DIR, championship)
        os.makedirs(championship_dir, exist_ok=True)

        for jogo in data:
            try:
                time1 = jogo['home_team']
                time2 = jogo['away_team']
                odds_time1 = [odds['price'] for odds in jogo['bookmakers'][0]['markets'][0]['outcomes'] if odds['name'] == time1]
                odds_time2 = [odds['price'] for odds in jogo['bookmakers'][0]['markets'][0]['outcomes'] if odds['name'] == time2]
                
                media_odds_time1 = sum(odds_time1) / len(odds_time1) if odds_time1 else 0
                media_odds_time2 = sum(odds_time2) / len(odds_time2) if odds_time2 else 0
                data_jogo = datetime.fromisoformat(jogo['commence_time']).date().strftime("%d/%m")

                img = background.copy()
                d = ImageDraw.Draw(img)

                # DEFINIR TEXTO PARA OS TIMES E ODDS
                text1 = f"{time1} ({media_odds_time1:.2f})"
                text2 = f"{time2} ({media_odds_time2:.2f})"
                vs_text = "VS"

                # DESENHAR TEXTO NA IMAGEM
                text1_width, text1_height = d.textbbox((0, 0), text1, font=FONT)[2:]
                text2_width, text2_height = d.textbbox((0, 0), text2, font=FONT)[2:]
                vs_width, vs_height = d.textbbox((0, 0), vs_text, font=FONT)[2:]

                total_width = text1_width + vs_width + text2_width + 60
                x_start = (img.width - total_width) / 2

                # DESENHAR OS TIMES E "VS"
                draw_text_with_shadow(d, text1, (x_start, img.height - text1_height - 50), FONT, (255, 255, 0))
                draw_text_with_shadow(d, vs_text, (x_start + text1_width + 30, img.height - vs_height - 50), FONT, (255, 255, 0))
                draw_text_with_shadow(d, text2, (x_start + text1_width + vs_width + 60, img.height - text2_height - 50), FONT, (255, 255, 0))

                # DESENHAR A DATA
                data_texto = f"Data: {data_jogo}"
                data_width, data_height = d.textbbox((0, 0), data_texto, font=FONT)[2:]
                data_x = (img.width - data_width) / 2
                data_y = img.height - text1_height - text2_height - vs_height - data_height - 70
                draw_text_with_shadow(d, data_texto, (data_x, data_y), FONT, (255, 255, 255))

                # SALVANDO A IMAGEM NA PASTA DO CAMPEONATO
                img_name = f"{time1} vs {time2}.png".replace(" ", "_")
                img_path = os.path.join(championship_dir, img_name)
                img.save(img_path)

            except Exception as e:
                print(f"Erro ao processar o jogo {time1} vs {time2}: {e}")

    except Exception as e:
        print(f"Erro ao acessar a API para {championship}: {e}")

# MENSAGEM FINAL APÓS A GERAÇÃO DAS IMAGENS
print(f"Imagens geradas nas pastas: {OUTPUT_DIR}")
