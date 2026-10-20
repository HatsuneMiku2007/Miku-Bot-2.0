import os
import random
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # <--- Importamos el servidor web para Render

# Cargar token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configuración de intenciones (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=["!", "miku!"], intents=intents)

# Contador de malas palabras por usuario
user_swears = {}

# ==========================================
# VISTAS INTERACTIVAS (BOTONES / MENÚS)
# ==========================================

class MikuHowAreYouView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Bien 😊", style=discord.ButtonStyle.green)
    async def bien(self, interaction: discord.Interaction, button: discord.ui.Button):
        respuestas = [
            "¡Me alegro muchísimo! 🎵 ¡Hoy es un gran día para cantar juntos!",
            "¡Qué buena noticia! ♪ ¡Esa energía me da ganas de cantar una nueva canción!",
            "¡Yay~! 39 por compartir tu alegría conmigo 💚"
        ]
        await interaction.response.send_message(random.choice(respuestas), ephemeral=True)

    @discord.ui.button(label="Más o menos 😐", style=discord.ButtonStyle.blurple)
    async def mas_o_menos(self, interaction: discord.Interaction, button: discord.ui.Button):
        respuestas = [
            "Ánimo... ¡Te dedico una melodía suave para alegrar tu día! 🎶",
            "A veces hay días así. ¡Tómate un té y escucha algo de música relajante! ☕",
            "¡Aquí estoy para acompañarte si quieres escuchar canciones! ♪"
        ]
        await interaction.response.send_message(random.choice(respuestas), ephemeral=True)

    @discord.ui.button(label="Mal 😢", style=discord.ButtonStyle.red)
    async def mal(self, interaction: discord.Interaction, button: discord.ui.Button):
        respuestas = [
            "Lo siento mucho... 💙 Recuerda que no estás solo/a, ¡te mando un abrazo musical fuerte!",
            "Ojalá pudiera darte un puerro de la suerte para hacerte sonreír... ¡Todo mejorará pronto! 🌿",
            "Si necesitas despejar la mente, escucha *Melt* o *Tell Your World*. ¡Te mando mucha fuerza! ✨"
        ]
        await interaction.response.send_message(random.choice(respuestas), ephemeral=True)


class CumplidosSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Te quiero", description="Decirle a Miku que la quieres", emoji="💙"),
            discord.SelectOption(label="Eres linda", description="Decirle a Miku que es muy bonita", emoji="✨"),
            discord.SelectOption(label="Te amo", description="Expresar tu amor por Miku", emoji="💖"),
        ]
        super().__init__(placeholder="Elige qué decirle a Miku...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        eleccion = self.values[0]
        if eleccion == "Te quiero":
            resp = random.choice([
                "¡Ehh!? 😳 ¡Yo también te quiero mucho! Thanks for supporting me! ♪",
                "¡Muchas gracias! 💙 ¡Tus palabras me dan fuerzas para cantar!"
            ])
        elif eleccion == "Eres linda":
            resp = random.choice([
                "¡A-Arigatou~! 😳 ¡Tú también eres genial!",
                "¡Qué tierno/a! 😊 ¡Me pones un poco tímida!"
            ])
        else:
            resp = random.choice([
                "¡Waaaa~! 😳😳 ¡Eso es muy directo! ¡39 (Sankyuu) por tanto amor! 💖",
                "¡Mi corazón hace *dokidoki*! 💓 ¡Prometo dar lo mejor en mi próximo concierto para ti!"
            ])
        
        await interaction.response.send_message(resp)
        msg = await interaction.original_response()
        await msg.add_reaction("😳")

class CumplidosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CumplidosSelect())


# ==========================================
# EVENTOS DEL BOT
# ==========================================

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Project SEKAI | !ayuda"))
    print(f"¡{bot.user} está lista y conectada en Render! 🎤")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    # Detección de insultos
    palabras_prohibidas = ["insulto1", "insulto2", "tonto", "idiota"]
    if any(word in content_lower for word in palabras_prohibidas):
        await message.add_reaction("❗")
        user_id = message.author.id
        user_swears[user_id] = user_swears.get(user_id, 0) + 1
        
        if user_swears[user_id] >= 7:
            await message.channel.send(
                f"⚠️ {message.author.mention}, ¡has dicho malas palabras 7 veces! "
                f"Por favor mantén un lenguaje respetuoso en el servidor. 😡"
            )
            user_swears[user_id] = 0

    # Reacciones a menciones
    if bot.user.mentioned_in(message):
        if "hola" in content_lower:
            respuestas_saludo = [
                f"¡Hola {message.author.mention}! 🎵 ¿Cómo estás?",
                f"¡39! ¡Hola {message.author.mention}! ♪ ¿Qué tal tu día?",
                f"¡Haii~! ¡Hola {message.author.mention}! ✨"
            ]
            await message.channel.send(random.choice(respuestas_saludo))
            
        elif "como estas" in content_lower or "cómo estás" in content_lower:
            await message.add_reaction("👍")
            respuestas_estado = [
                "¡Estoy genial y afinando mi voz para cantar! 🎤✨",
                "¡Muy bien! Estaba ensayando unos pasos de baile ♪",
                "¡Excelente! Lista para ayudarte en el servidor 😊"
            ]
            await message.channel.send(random.choice(respuestas_estado))

    elif content_lower in ["/hola", "!hola", "hola miku"]:
        respuestas = [
            f"¡Hola! 🎵 ¿Cómo estás hoy, {message.author.display_name}?",
            "¡39 (Sankyuu)! ¡Hola! ¿Listos para escuchar música? 🍹",
            "¡Haii~! ¡Hola! Miku reportándose ♪"
        ]
        await message.channel.send(random.choice(respuestas))

    await bot.process_commands(message)


# ==========================================
# COMANDOS DEL BOT
# ==========================================

@bot.command(name="comoestas", aliases=["cómoestás"])
async def como_estas(ctx):
    await ctx.message.add_reaction("👍")
    respuestas = [
        "¡Estoy súper bien y con muchas ganas de cantar! 🎤",
        "¡Excelente! Comiéndome un vegetal picado y practicando canciones 🌱",
        "¡Muy feliz de estar compartiendo con ustedes hoy! ♪"
    ]
    await ctx.send(random.choice(respuestas))

@bot.command(name="preguntaestado")
async def pregunta_estado(ctx):
    view = MikuHowAreYouView()
    await ctx.send(f"Hola {ctx.author.mention}, Miku te pregunta: **¿Cómo estás hoy?**", view=view)

@bot.command(name="puerro")
async def puerro(ctx):
    await ctx.message.add_reaction("🧅")
    respuestas = [
        "¡Aquí tienes un puerro / cebollín de la suerte! 🌿✨ ¡A que se ve delicioso!",
        "¡Te regalo este cebollín fresco! 🟢 *Empieza a bailar PoPiPo*",
        "¡Toma un cebollín! ¡Con esto tendrás energía todo el día! 🥬"
    ]
    await ctx.send(random.choice(respuestas))

@bot.command(name="QuienesMiku", aliases=["quienesmiku"])
async def quienes_miku(ctx):
    embed = discord.Embed(
        title="🎤 ¿Quién es Hatsune Miku? (初音ミク)",
        description="**Hatsune Miku** es un software de síntesis de voz (Vocaloid) desarrollado por Crypton Future Media. Su nombre significa *'El primer sonido del futuro'*.",
        color=discord.Color.from_rgb(57, 197, 187)
    )
    embed.add_field(
        name="🎵 Canciones Populares",
        value="• *The World is Mine*\n• *PoPiPo*\n• *Melt*\n• *Tell Your World*\n• *Senbonzakura*",
        inline=False
    )
    embed.add_field(
        name="❓ ¿Cómo funciona?",
        value="Es un banco de voz humano estilizado que permite a compositores de todo el mundo crear música ingresando letra y melodía.",
        inline=False
    )
    embed.add_field(
        name="🌐 Enlaces Oficiales",
        value="[Wiki Oficial de Hatsune Miku](https://vocaloid.fandom.com/wiki/Hatsune_Miku)\n[Canal de YouTube (39ch)](https://www.youtube.com/@HatsuneMiku)",
        inline=False
    )
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Hatsune_Miku_logo.svg/1200px-Hatsune_Miku_logo.svg.png")
    await ctx.send(embed=embed)

@bot.command(name="vocaloid")
async def vocaloid_info(ctx):
    embed = discord.Embed(
        title="🎧 ¿Qué es VOCALOID?",
        description="VOCALOID es un sintetizador de voz que permite crear canciones virtuales a partir de bancos de voz de personajes.",
        color=discord.Color.purple()
    )
    embed.add_field(name="💛 Kagamine Rin & Len", value="Gemelos/Espejos amarillos llenos de energía rock y pop.", inline=False)
    embed.add_field(name="🩷 Megurine Luka", value="Voz madura e internacional (Japonés/Inglés).", inline=False)
    embed.add_field(name="❤️ MEIKO", value="La primera Vocaloid japonesa con voz potente enfocada en pop y rock.", inline=False)
    embed.add_field(name="💙 KAITO", value="El primer Vocaloid masculino japonés, amante del helado.", inline=False)
    embed.add_field(name="💚 GUMI (Megpoid)", value="Voz muy expresiva y popular en el género Rock / Indie.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="vocaloidmusic")
async def recomendacion_musica(ctx):
    canciones = [
        {"titulo": "The World is Mine", "prod": "ryo (supercell)", "genero": "J-Pop", "dato": "Es considerada el 'himno' no oficial de Miku."},
        {"titulo": "Unknown Mother-Goose", "prod": "wowaka", "genero": "Rock Alternativo", "dato": "Uno de los temas más emblemáticos e influyentes."},
        {"titulo": "God-ish (Kami-poi)", "prod": "PinocchioP", "genero": "Electropop", "dato": "Superó decenas de millones de reproducciones rápidamente."},
        {"titulo": "Matryoshka", "prod": "Hachi (Kenshi Yonezu)", "genero": "Indie Rock", "dato": "Cantada por Miku y GUMI con un estilo caótico."},
        {"titulo": "Goodbye Declaration", "prod": "Chinozo", "genero": "Pop / Rock", "dato": "Cantada por Flower, se convirtió en un gran fenómeno viral."}
    ]
    c = random.choice(canciones)
    embed = discord.Embed(title=f"🎶 Recomendación: {c['titulo']}", color=discord.Color.gold())
    embed.add_field(name="Productor", value=c['prod'], inline=True)
    embed.add_field(name="Género", value=c['genero'], inline=True)
    embed.add_field(name="💡 Dato curioso", value=c['dato'], inline=False)
    await ctx.send(embed=embed)

@bot.command(name="youtubers")
async def rec_youtubers(ctx):
    yts = [
        "**Project Sekai Official** - Para ver videos oficiales, conciertos y 3D MV.",
        "**Mitchie M** - Conocido por hacer que la voz de Miku suene aterradoramente humana.",
        "**PinocchioP** - Productor clásico activo con canciones satíricas y profundas.",
        "**DECO*27** - Uno de los creadores más famosos y constantes de la historia de Vocaloid."
    ]
    await ctx.send(f"📺 Miku te recomienda ver el canal de: {random.choice(yts)}")

@bot.command(name="juegos")
async def menu_juegos(ctx):
    await ctx.send("🎮 **¡Hora de jugar!**\nUsa `!quiz` para responder preguntas o `!adivinanza` para adivinar el Vocaloid.")

@bot.command(name="quiz")
async def quiz_cmd(ctx):
    preguntas = [
        {"p": "¿Cuál es la comida / objeto representativo de Hatsune Miku?", "r": ["puerro", "cebollin", "cebollín"], "diff": "Fácil"},
        {"p": "¿Quién compuso la famosa canción 'World is Mine'?", "r": ["ryo", "supercell"], "diff": "Fácil"},
        {"p": "¿Qué número representa el juego de palabras del nombre de Miku (Sankyuu)?", "r": ["39"], "diff": "Difícil"}
    ]
    q = random.choice(preguntas)
    await ctx.send(f"🧩 **Quiz [{q['diff']}]**: {q['p']}\n*(Tienes 15 segundos para responder en el chat)*")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if any(res in msg.content.lower() for res in q['r']):
            await ctx.send(f"🎉 ¡Correcto {ctx.author.mention}! ¡39 por responder bien!")
        else:
            await ctx.send(f"❌ Nop~ La respuesta correcta era: **{q['r'][0]}**")
    except asyncio.TimeoutError:
        await ctx.send("⏰ ¡Se acabó el tiempo!")

@bot.command(name="adivinanza")
async def adivinanza_cmd(ctx):
    pistas = [
        {"pista": "Tengo cabello amarillo en forma de banana y me encanta el helado.", "resp": "kaito"},
        {"pista": "Somos gemelos/espejos de color amarillo y vestimos trajes de marinero.", "resp": "kagamine"},
        {"pista": "Mi pelo es de color rosa largo y canto bien tanto en inglés como en japonés.", "resp": "luka"}
    ]
    item = random.choice(pistas)
    await ctx.send(f"🔮 **Adivina el Vocaloid**: *\"{item['pista']}\"*")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if item['resp'] in msg.content.lower():
            await ctx.send("🎉 ¡Acertaste! ¡Eres todo un experto Vocaloid! ✨")
        else:
            await ctx.send(f"❌ ¡Uuuh, casi! El Vocaloid era **{item['resp'].capitalize()}**.")
    except asyncio.TimeoutError:
        await ctx.send("⏰ Tiempo agotado. ¡Sigue intentándolo!")

@bot.command(name="analizar")
@commands.has_permissions(manage_messages=True)
async def analizar_server(ctx):
    total = ctx.guild.member_count
    roles = len(ctx.guild.roles)
    embed = discord.Embed(title=f"📊 Análisis de {ctx.guild.name}", color=discord.Color.blue())
    embed.add_field(name="👥 Usuarios Totales", value=str(total))
    embed.add_field(name="🏷️ Cantidad de Roles", value=str(roles))
    await ctx.send(embed=embed)

@bot.command(name="expulsar")
@commands.has_permissions(kick_members=True)
async def expulsar_user(ctx, miembro: discord.Member, *, razon="No especificada"):
    await miembro.kick(reason=razon)
    await ctx.send(f"👢 {miembro.display_name} ha sido expulsado/a por Miku. Razón: {razon}")

@bot.command(name="banear")
@commands.has_permissions(ban_members=True)
async def banear_user(ctx, miembro: discord.Member, *, razon="No especificada"):
    await miembro.ban(reason=razon)
    await ctx.send(f"🔨 {miembro.display_name} ha sido baneado/a. Razón: {razon}")

@bot.tree.command(name="cumplidos", description="Dile algo lindo a Miku")
async def cumplidos_slash(interaction: discord.Interaction):
    view = CumplidosView()
    await interaction.response.send_message("¿Qué te gustaría decirle a Miku hoy? 💙", view=view)

@bot.command(name="ayuda", aliases=["comandos"])
async def ayuda_cmd(ctx):
    embed = discord.Embed(title="🎵 Comandos de Hatsune Miku Bot", color=discord.Color.from_rgb(57, 197, 187))
    embed.add_field(name="💬 Interacción", value="`!hola`, `!comoestas`, `!preguntaestado`, `/cumplidos`, Mencionarla (@Miku)", inline=False)
    embed.add_field(name="🥬 Diversión", value="`!puerro`, `!juegos`, `!quiz`, `!adivinanza`", inline=False)
    embed.add_field(name="📚 Info Vocaloid", value="`!QuienesMiku`, `!vocaloid`, `!vocaloidmusic`, `!youtubers`", inline=False)
    embed.add_field(name="🛠️ Admin", value="`!analizar`, `!expulsar @usuario`, `!banear @usuario`", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def setup_hook():
    await bot.tree.sync()

# INICIO DEL BOT Y DEL SERVIDOR WEB
if __name__ == "__main__":
    if TOKEN:
        keep_alive()  # <--- Inicia el mini servidor web para que Render detecte la app
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN no encontrado en las Variables de Entorno")
