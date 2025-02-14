from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

email_user = os.getenv('EMAIL_USER')
email_pass = os.getenv('EMAIL_PASSWORD')


# funcao que vai responder ao comando /start

sim = 0
nao = 0
votando = False


def carregar_votos():
    try:
        with open('votacao.json', 'r') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"sim": 0, "nao": 0}



def salvar_votos(votos):
    try:
        with open('votacao.json', 'w') as arquivo:
            json.dump(votos, arquivo)
    except IOError as e:
        print(f"Erro ao salvar votos: {e}")


def email(votos):
    #servidor
    servidor = smtplib.SMTP('smtp.gmail.com', 587)
    servidor.starttls()
    servidor.login(email_user, email_pass)

    lista_destinatarios = ['anabarbiero66@gmail.com']
    msg = EmailMessage()
    msg['Subject'] = 'Votação da enquete do Bot tranquilo'
    msg['From'] = 'anacarolinabarbiero@gmail.com'
    msg['To'] = ', '.join(lista_destinatarios)

    nome = lista_destinatarios[0].split('@')[0].capitalize()
    mensagem = 'Aqui vão os resultados da enquete: '
    msg.set_content(mensagem)
    
    msg.add_alternative(f"""
    <html>
    <body>
        <h1>Olá, {nome}!</h1> 
        <h2>{mensagem}</h2>          
        <p>Um novo voto foi registrado no bot!</p>
        <p>🗳️ <strong>Votação Atual:</strong></p>
        <p>✔️ Sim: {votos["sim"]} votos</p>
        <p>❌ Não: {votos["nao"]} votos</p>
        <p>📊 Total de votos: {votos["sim"] + votos["nao"]}</p>

        <p><strong>Atenciosamente,</strong></p>
        <p>Equipe do Bot tranquilo</p>
        <img src='https://i.pinimg.com/736x/c1/9f/01/c19f0108c3ea7a4e89deba3e7aefd953.jpg' alt='dog-paz'>
    </body>
    </html>
""", subtype='html')

    try:
        servidor.send_message(msg)  
        servidor.quit()
        print('E-mail enviado com sucesso')
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')




async def start(update: Update, context) -> None:
    await update.message.reply_text('Olá, sou apenas um Bot tranquilo vivendo uma vida tranquila. Como vai usuário tranquilo? Me envie uma mensagem e eu irei repeti-la tranquilamente... Digite /help para ver a lista de comandos de forma tranquila')

async def hello(update: Update, context) -> None:
    await update.message.reply_text('BOM DIA MUNDOOO')

async def oi(update: Update, context) -> None:
    await update.message.reply_text('Como você está?')

    
async def foto(update: Update, context) -> None:
    await update.message.reply_text('Aqui vai a imagem tranquila:')
    await update.message.reply_photo('https://i.pinimg.com/736x/ed/cd/7c/edcd7c58f984b2e2134282a450558b4f.jpg')
    await update.message.reply_photo('https://i.pinimg.com/736x/a4/90/c1/a490c10e7e2c54b2ea2a8e0dfdbc1f3a.jpg')


async def votar(update: Update, context) -> None:
    votos = carregar_votos()
    await update.message.reply_text('python é dificil?')
    if not context.args:  # Se o usuário n digitar nada
        await update.message.reply_text("Por favor, use '/votar sim' ou '/votar não' para registrar seu voto.")
        return

    voto = context.args[0].lower()

    if voto in ['sim', 's', 'sim.']:
        votos["sim"] += 1
        await update.message.reply_text('Voto registrado: SIM')
    elif voto in ['não', 'nao', 'n', 'não.']:
        votos["nao"] += 1
        await update.message.reply_text('Voto registrado: NÃO')
    else:
        await update.message.reply_text('Por favor, digite apenas "sim" ou "não".')
        return

    salvar_votos(votos)
    email(votos)


async def resultado(update: Update, context) -> None:
    global sim, nao
    votos = carregar_votos()
    total = votos['sim'] + votos['nao']

    if total == 0:
        await update.message.reply_text('Nenhum voto registrado ainda...')
        return

    percent_sim = (votos['sim'] / total) * 100
    percent_nao = (votos['nao'] / total) * 100

    resultado_msg = (f'Resultados da votação:\n✅Sim: {sim} votos ({percent_sim:.2f}%)\n❎ Não: {nao} votos ({percent_nao:.2f}%)\nTotal de votos: {total}')

    await update.message.reply_text(resultado_msg)


async def cute(update: Update, context) -> None:
    await update.message.reply_text('Aqui vai a animação tranquila:')
    await update.message.reply_animation('https://i.imgur.com/09cTiqV.gif')

async def help(update: Update, context) -> None:
    await update.message.reply_text(f'lista de comandos do bot tranquilo:\n/start - Inicia a conversa tranquilamente\n/hello - O bot tranquilo envia um hello word a sua forma\n/oi - O bot pergunta tranquilamente como você está\n/foto - o bot envia uma foto tranquila\n/cute - O bot lhe envia um gif tranquilo\n/votar - abre o espaço de votações para a enquete\n/porcentagem - O bot te envia a porcentagens dos votos realizados na enquete\n/help - Ve a lista de comandos')

#funcao pra repetir a mensagem que for enviada

async def echo(update: Update, context) -> None:
    user_message = update.message.text
    await update.message.reply_text(f'Você disse: {user_message}')


#execucao do bot agr

def main():
    token_bot = os.getenv('BOT_TOKEN')  # Carregar o token do bot
    application = Application.builder().token(token_bot).build()  # Criar a aplicação com o token

    # Registra os handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('hello', hello))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('oi', oi))
    application.add_handler(CommandHandler('foto', foto))
    application.add_handler(CommandHandler('cute', cute))
    application.add_handler(CommandHandler('votar', votar))
    application.add_handler(CommandHandler('porcentagem', resultado))
    application.add_handler(MessageHandler(filters.TEXT, echo))

    # Iniciar o bot
    print('Bot rodando...')
    application.run_polling()


main()








# update.message.reply_text('Python é muito dificil?')
#         await update.message.reply_poll(
#             question= 'Python é dificil?',
#             options=  ['sim', 'não' ],
#             is_anonymous= False 
#             )


# no codigo acima cria uma janela de votacao dentro do telegram no qual o usuário pode so apertar o botao e já registrar o voto