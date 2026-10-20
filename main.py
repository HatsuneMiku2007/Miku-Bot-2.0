import os
import random
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

# ==========================================
# RECONOCIMIENTO AUTOMÁTICO DE TOKEN
# ==========================================
# Lee directamente la variable de entorno configurada en tu servidor (ej. Render, Railway o tu PC)
TOKEN = os.getenv("DISCORD_TOKEN")

# Configuración de intenciones (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Inicializar bot con prefijos múltiples ("!" y "miku!")
bot = commands.Bot(command_prefix=["!", "miku!"], intents=intents)

# Diccionario para control de moderación (insultos)
user_swears = {}

# ==========================================
# VISTAS INTERACTIVAS (BOTONES Y MENÚS)
# ==========================================

class MikuHowAreYouView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Bien 😊", style=discord.ButtonStyle.green)
    async def bien(self, interaction: discord.Interaction, button: discord.ui.Button):
        respuestas = [
            "¡Me alegro muchísimo! 🎵 ¡Hoy es un gran día para cantar y pasarla bien juntos!",
            "¡Qué excelente noticia! ♪ ¡Esa energía me da inspiración para componer una nueva melodía!",
            "¡Yay~! 39 (Sankyuu) por compartir tu alegría conmigo 💚",
            "¡Genial! Así da gusto ensayar con una sonrisa ♪"
        ]
        await interaction.response.send_message(random.choice(respuestas), ephemeral=True)

    @discord.ui.button(label="Más o menos 😐", style=discord.ButtonStyle.blurple)
    async def mas_o_menos(self, interaction: discord.Interaction, button: discord.ui.Button):
        respuestas = [
            "Ánimo... ¡Te dedico una pista suave y relajante para endulzar tu día! 🎶",
            "A veces hay días grises. ¡Tómate un descanso, respira hondo y escucha tu canción favorita! ☕",
            "¡Aquí estoy para acompañarte! A veces un poco de música ayuda a despejar la mente ♪",
            "No te preocupes, mañana será un día mucho mejor. ¡Te mando fuerzas! ✨"
        ]
        await interaction.response.send_message(random.choice(respuestas), ephemeral=True)

    @discord.ui.button(label="Mal 😢", style=discord.ButtonStyle.red)
    async def mal(self, interaction: discord.Interaction, button: discord.ui.Button):
        respuestas = [
            "Lo siento tanto... 💙 Recuerda que no estás solo/a, ¡te mando un fuerte abrazo virtual!",
            "Ojalá pudiera darte un puerro mágico de la buena suerte para hacerte sonreír... ¡Todo pasará! 🌿",
            "Si necesitas desahogarte o solo escuchar música para calmarte, cuenta conmigo. ¡Mucho ánimo! ✨",
            "Un día malo no define tu vida. ¡Te mando un pedacito de mi energía musical para reconfortarte! 💙"
        ]
        await interaction.response.send_message(random.choice(respuestas), ephemeral=True)


class CumplidosSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Te quiero", description="Decirle a Miku que la quieres", emoji="💙"),
            discord.SelectOption(label="Eres linda", description="Decirle a Miku que es muy bonita", emoji="✨"),
            discord.SelectOption(label="Te amo", description="Expresar tu profundo amor por Miku", emoji="💖"),
            discord.SelectOption(label="Cantas hermoso", description="Alabar la voz de Miku", emoji="🎤"),
        ]
        super().__init__(placeholder="Elige qué decirle a Miku...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        eleccion = self.values[0]
        if eleccion == "Te quiero":
            resp = random.choice([
                "¡Ehh!? 😳 ¡Yo también te quiero muchísimo! Thank you for supporting me! ♪",
                "¡Qué palabras tan lindas! 💙 ¡Me das muchísima motivación para seguir cantando!"
            ])
        elif eleccion == "Eres linda":
            resp = random.choice([
                "¡A-Arigatou~! 😳 ¡Ay, me pones un poquito nerviosa y sonrojada!",
                "¡Muchas gracias! ✨ Hago lo posible por lucir genial en cada concierto para ustedes."
            ])
        elif eleccion == "Te amo":
            resp = random.choice([
                "¡Waaaa~! 😳😳 ¡Eso fue muy directo! ¡Mi corazón hace *dokidoki*! 💖",
                "¡Oh por dios! 💓 Prometo dar lo mejor de mí en el escenario siempre por ti."
            ])
        else:
            resp = random.choice([
                "¡Aww, 39! 🎤 ¡Me alegra que te guste mi voz digital!",
                "¡Gracias! Practico todos los días con mis bancos de voz para sonar perfecta para ti ♪"
            ])
        
        await interaction.response.send_message(resp)
        try:
            msg = await interaction.original_response()
            await msg.add_reaction("😳")
        except Exception:
            pass

class CumplidosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CumplidosSelect())


# ==========================================
# EVENTOS DE CONEXIÓN Y MENSAJES
# ==========================================

@bot.event
async def on_ready():
    print("\n" + "="*50)
    print(" 🟢 ¡HATSUNE MIKU SE HA CONECTADO A DISCORD CON ÉXITO! 🟢")
    print("="*50)
    print(f" • Nombre del Bot : {bot.user.name}")
    print(f" • ID de Usuario  : {bot.user.id}")
    print(f" • Latencia (Ping): {round(bot.latency * 1000)}ms")
    print(f" • Servidores Activos ({len(bot.guilds)}):")
    for guild in bot.guilds:
        print(f"    - 🌐 {guild.name} (Miembros: {guild.member_count})")
    print("="*50)
    print(" ¡El token del servidor fue reconocido perfectamente!\n")
    
    try:
        await bot.change_presence(activity=discord.Game(name="Project SEKAI | !ayuda"))
    except Exception as e:
        print(f"Aviso: No se pudo cambiar el estado inicial: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    # 1. Moderación de palabras prohibidas
    palabras_prohibidas = ["insulto1", "tonto", "idiota"]
    if any(word in content_lower for word in palabras_prohibidas):
        try:
            await message.add_reaction("❗")
        except Exception:
            pass
        
        user_id = message.author.id
        user_swears[user_id] = user_swears.get(user_id, 0) + 1
        
        if user_swears[user_id] >= 7:
            await message.channel.send(
                f"⚠️ {message.author.mention}, ¡has dicho palabras prohibidas 7 veces! "
                f"Por favor mantén un comportamiento respetuoso en el servidor. 😡"
            )
            user_swears[user_id] = 0

    # 2. Reacciones a Menciones directas
    if bot.user.mentioned_in(message):
        if "hola" in content_lower:
            respuestas_saludo = [
                f"¡Hola, {message.author.mention}! 🎵 ¿Qué tal va tu día?",
                f"¡39! ¡Haii~! Qué gusto saludarte, {message.author.mention} ♪",
                f"¡Hola hola! 🎤 Lista para cantar y ayudarte en lo que necesites, {message.author.mention}."
            ]
            await message.channel.send(random.choice(respuestas_saludo))
            return
        elif "como estas" in content_lower or "cómo estás" in content_lower:
            try:
                await message.add_reaction("👍")
            except Exception:
                pass
            respuestas_estado = [
                "¡Estoy genial y con mis sintetizadores al 100%! 🎤✨",
                "¡Muy feliz! Estaba ensayando unos pasos de baile nuevos para el próximo concierto ♪",
                "¡Excelente! Lista para acompañarte y escuchar buena música 😊"
            ]
            await message.channel.send(random.choice(respuestas_estado))
            return

    # 3. Saludos directos por texto
    elif content_lower in ["/hola", "!hola", "hola miku"]:
        respuestas = [
            f"¡Hola! 🎵 ¿Cómo estás hoy, {message.author.display_name}?",
            "¡39 (Sankyuu)! ¡Hola! ¿Listos para escuchar buena música y pasar el rato? 🍹",
            "¡Haii~! ¡Hola! Miku reportándose en el servidor ♪",
            "¡Hey! Qué alegría verte por aquí hoy. ¿Qué planes hay? ✨"
        ]
        await message.channel.send(random.choice(respuestas))
        return

    await bot.process_commands(message)


# ==========================================
# COMANDOS DE INTERACCIÓN Y VARIEDAD
# ==========================================

@bot.command(name="hola")
async def cmd_hola(ctx):
    respuestas = [
        f"¡Hola {ctx.author.mention}! 🎵 Qué gusto saludarte.",
        f"¡39! ¡Hola {ctx.author.mention}! ♪ ¿Qué te trae por aquí hoy?",
        f"¡Haii~! ¡Hola {ctx.author.mention}! Espero que tengas un día maravilloso ✨"
    ]
    await ctx.send(random.choice(respuestas))

@bot.command(name="comoestas", aliases=["cómoestás"])
async def como_estas(ctx):
    try:
        await ctx.message.add_reaction("👍")
    except Exception:
        pass
    respuestas = [
        "¡Estoy súper bien y con muchísimas ganas de cantar! 🎤",
        "¡Excelente! Comiéndome un rico vegetal picado y afinando mi voz 🌱",
        "¡Muy feliz de estar compartiendo con ustedes hoy en este servidor! ♪",
        "¡De maravilla! Lista para dar un gran espectáculo virtual ✨"
    ]
    await ctx.send(random.choice(respuestas))

@bot.command(name="preguntaestado")
async def pregunta_estado(ctx):
    view = MikuHowAreYouView()
    await ctx.send(f"Hola {ctx.author.mention}, Miku te pregunta: **¿Cómo estás hoy?**", view=view)

@bot.command(name="puerro", aliases=["cebollin"])
async def puerro(ctx):
    try:
        await ctx.message.add_reaction("🧅")
    except Exception:
        pass
    respuestas = [
        "¡Aquí tienes un puerro / cebollín de la suerte! 🌿✨ ¡A que se ve fresquísimo!",
        "¡Te regalo este cebollín verde! 🟢 *Empieza a bailar alegremente con su negi*",
        "¡Toma un cebollín! ¡Con esto tendrás energía ilimitada todo el día! 🥬",
        "¡Un negi fresco directo para ti! Cuídalo muy bien ♪"
    ]
    await ctx.send(random.choice(respuestas))

@bot.command(name="cantar")
async def cantar_cmd(ctx):
    canciones_fragmentos = [
        "🎵 *Sekai de ichiban ohime-sama... Sou iu atsukai kokoromete yo!* (World is Mine) 👑",
        "🍹 *Po-pi-po, po-pi-po, po-pi-po-pi-po-po... ¡Toma jugo de verduras!* (PoPiPo) 🥬",
        "🎶 *Melt, tokete shimaisou... suki nante ienai!* (Melt) 💕",
        "✨ *Tell your world, hibike kono koe... todoke sekaijyuu ni!* (Tell Your World) 🌍",
        "🌸 *Senbonzakura yoru ni magire, kimi no oiran doushi...* (Senbonzakura) ⚔️"
    ]
    await ctx.send(random.choice(canciones_fragmentos))

@bot.command(name="cafe", aliases=["jugo"])
async def cafe_cmd(ctx):
    bebidas = [
        "☕ Te preparé un café calentito bien cargado para recargar energías.",
        "🍹 ¡Aquí tienes un vaso de jugo de verduras PoPiPo bien frío y saludable!",
        "🧋 Te invito un té con leche y perlas de tapioca. ¡Disfrútalo!",
        "🍵 Un té verde tradicional perfecto para relajarse un rato ♪"
    ]
    await ctx.send(random.choice(bebidas))


# ==========================================
# COMANDOS INFORMATIVOS Y CULTURALES
# ==========================================

@bot.command(name="QuienesMiku", aliases=["quienesmiku"])
async def quienes_miku(ctx):
    embed = discord.Embed(
        title="🎤 ¿Quién es Hatsune Miku? (初音ミク)",
        description="**Hatsune Miku** es un software de síntesis de voz (Vocaloid) desarrollado por Crypton Future Media. Su nombre significa *'El primer sonido del futuro'*.",
        color=discord.Color.from_rgb(57, 197, 187)
    )
    embed.add_field(
        name="🎵 Canciones Icónicas",
        value="• *The World is Mine*\n• *PoPiPo*\n• *Melt*\n• *Tell Your World*\n• *Senbonzakura*",
        inline=False
    )
    embed.add_field(
        name="❓ ¿Cómo funciona?",
        value="Es un banco de voz sintetizado basado en muestras de voz humana, permitiendo a compositores de todo el mundo crear canciones increíbles.",
        inline=False
    )
    embed.add_field(
        name="🌐 Enlaces Oficiales",
        value="[Wiki Oficial de Hatsune Miku](https://vocaloid.fandom.com/wiki/Hatsune_Miku)\n[Canal de YouTube (39ch)](https://www.youtube.com/@HatsuneMiku)",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name="vocaloid")
async def vocaloid_info(ctx):
    embed = discord.Embed(
        title="🎧 ¿Qué es VOCALOID?",
        description="VOCALOID es un software sintetizador de voz que permite dar vida musical a personajes virtuales.",
        color=discord.Color.purple()
    )
    embed.add_field(name="💛 Kagamine Rin & Len", value="Los gemelos/espejos amarillos llenos de energía pop y rock.", inline=False)
    embed.add_field(name="🩷 Megurine Luka", value="Voz madura, elegante y bilingüe (Japonés/Inglés).", inline=False)
    embed.add_field(name="❤️ MEIKO", value="La primera Vocaloid japonesa con una voz potente y cálida.", inline=False)
    embed.add_field(name="💙 KAITO", value="El primer Vocaloid masculino japonés, gran amante de los helados.", inline=False)
    embed.add_field(name="💚 GUMI (Megpoid)", value="Una voz extremadamente versátil muy popular en el rock e indie.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="vocaloidmusic")
async def recomendacion_musica(ctx):
    canciones = [
        {"titulo": "The World is Mine", "prod": "ryo (supercell)", "genero": "J-Pop", "dato": "Es considerada un himno clásico absoluto de Miku."},
        {"titulo": "Unknown Mother-Goose", "prod": "wowaka", "genero": "Rock Alternativo", "dato": "Una obra maestra emocional e influyente."},
        {"titulo": "God-ish (Kami-poi)", "prod": "PinocchioP", "genero": "Electropop", "dato": "Un éxito moderno con millones de reproducciones."},
        {"titulo": "Matryoshka", "prod": "Hachi (Kenshi Yonezu)", "genero": "Indie Rock", "dato": "Un dueto icónico y caótico entre Miku y GUMI."},
        {"titulo": "Goodbye Declaration", "prod": "Chinozo", "genero": "Pop / Rock", "dato": "Un fenómeno viral masivo en la escena actual."}
    ]
    c = random.choice(canciones)
    embed = discord.Embed(title=f"🎶 Recomendación musical: {c['titulo']}", color=discord.Color.gold())
    embed.add_field(name="Productor (P-Name)", value=c['prod'], inline=True)
    embed.add_field(name="Género", value=c['genero'], inline=True)
    embed.add_field(name="💡 Dato curioso", value=c['dato'], inline=False)
    await ctx.send(embed=embed)

@bot.command(name="youtubers")
async def rec_youtubers(ctx):
    yts = [
        "**Project Sekai Official** - Para ver videos oficiales, historias, eventos y conciertos 3D.",
        "**Mitchie M** - Famoso mundialmente por lograr que la voz de Miku suene hiperrealista y humana.",
        "**PinocchioP** - Productor clásico con canciones profundas, pegadizas y llenas de significado.",
        "**DECO*27** - Uno de los creadores más legendarios, prolíficos y exitosos de la historia de Vocaloid."
    ]
    await ctx.send(f"📺 Miku te recomienda visitar el canal de: {random.choice(yts)}")


# ==========================================
# MINIJUEGOS (QUIZ Y ADIVINANZAS)
# ==========================================

@bot.command(name="juegos")
async def menu_juegos(ctx):
    await ctx.send("🎮 **¡Sala de Juegos Vocaloid!**\nUsa `!quiz` para responder preguntas a contratiempo o `!adivinanza` para adivinar al personaje.")

@bot.command(name="quiz")
async def quiz_cmd(ctx):
    preguntas = [
        {"p": "¿Cuál es la comida u objeto representativo y favorito de Hatsune Miku?", "r": ["puerro", "cebollin", "cebollín"], "diff": "Fácil"},
        {"p": "¿Quién compuso la famosa canción clásica 'World is Mine'?", "r": ["ryo", "supercell"], "diff": "Fácil"},
        {"p": "¿Qué número representa el juego de palabras japonés del nombre de Miku (Sankyuu / Thank you)?", "r": ["39"], "diff": "Difícil"}
    ]
    q = random.choice(preguntas)
    await ctx.send(f"🧩 **Quiz [{q['diff']}]**: {q['p']}\n*(Tienes 15 segundos para responder escribiendo en el chat)*")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if any(res in msg.content.lower() for res in q['r']):
            await ctx.send(f"🎉 ¡Correcto, {ctx.author.mention}! ¡39 (Sankyuu) por responder bien! ✨")
        else:
            await ctx.send(f"❌ ¡Uuuh, no! La respuesta correcta era: **{q['r'][0]}**")
    except asyncio.TimeoutError:
        await ctx.send("⏰ ¡Se acabó el tiempo! Será para la próxima.")

@bot.command(name="adivinanza")
async def adivinanza_cmd(ctx):
    pistas = [
        {"pista": "Tengo el cabello rubio amarrado en dos coletas con forma de banana y amo el helado.", "resp": "kaito"},
        {"pista": "Somos gemelos rubios de la familia de espejos y vestimos trajes marineros.", "resp": "kagamine"},
        {"pista": "Mi pelo es de color rosa largo y canto de manera fluida tanto en inglés como en japonés.", "resp": "luka"}
    ]
    item = random.choice(pistas)
    await ctx.send(f"🔮 **Adivina el personaje**: *\"{item['pista']}\"*")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if item['resp'] in msg.content.lower():
            await ctx.send("🎉 ¡Acertaste por completo! ¡Se nota que conoces muy bien el mundillo Vocaloid! ✨")
        else:
            await ctx.send(f"❌ ¡Casi lo logras! El personaje era **{item['resp'].capitalize()}**.")
    except asyncio.TimeoutError:
        await ctx.send("⏰ Tiempo agotado. ¡Sigue practicando!")


# ==========================================
# COMANDOS ADMINISTRATIVOS Y DE UTILIDAD
# ==========================================

@bot.command(name="analizar")
@commands.has_permissions(manage_messages=True)
async def analizar_server(ctx):
    total = ctx.guild.member_count
    roles = len(ctx.guild.roles)
    embed = discord.Embed(title=f"📊 Análisis del servidor: {ctx.guild.name}", color=discord.Color.blue())
    embed.add_field(name="👥 Usuarios Totales", value=str(total), inline=True)
    embed.add_field(name="🏷️ Cantidad de Roles", value=str(roles), inline=True)
    embed.set_footer(text="¡Miku analizando el servidor con éxito! ♪")
    await ctx.send(embed=embed)

@bot.command(name="expulsar")
@commands.has_permissions(kick_members=True)
async def expulsar_user(ctx, miembro: discord.Member, *, razon="No especificada"):
    await miembro.kick(reason=razon)
    await ctx.send(f"👢 {miembro.display_name} ha sido expulsado/a del servidor por orden de Miku. Razón: {razon}")

@bot.command(name="banear")
@commands.has_permissions(ban_members=True)
async def banear_user(ctx, miembro: discord.Member, *, razon="No especificada"):
    await miembro.ban(reason=razon)
    await ctx.send(f"🔨 {miembro.display_name} ha sido baneado/a del servidor. Razón: {razon}")

@bot.command(name="ayuda", aliases=["comandos"])
async def ayuda_cmd(ctx):
    embed = discord.Embed(title="🎵 Menú de Comandos de Hatsune Miku", color=discord.Color.from_rgb(57, 197, 187))
    embed.add_field(name="💬 Interacción Social", value="`!hola`, `!comoestas`, `!preguntaestado`, `/cumplidos`, Mencionarla (@Miku)", inline=False)
    embed.add_field(name="🥬 Diversión y Música", value="`!puerro`, `!cantar`, `!cafe`, `!juegos`, `!quiz`, `!adivinanza`", inline=False)
    embed.add_field(name="📚 Cultura Vocaloid", value="`!QuienesMiku`, `!vocaloid`, `!vocaloidmusic`, `!youtubers`", inline=False)
    embed.add_field(name="🛠️ Administración", value="`!analizar`, `!expulsar`, `!banear`", inline=False)
    embed.set_footer(text="¡Gracias por usar a Miku Bot! ♪ 39~")
    await ctx.send(embed=embed)

# Comando Slash interactivo de cumplidos
@bot.tree.command(name="cumplidos", description="Dile algo lindo a Miku")
async def cumplidos_slash(interaction: discord.Interaction):
    view = CumplidosView()
    await interaction.response.send_message("¿Qué te gustaría decirle a Miku hoy? 💙", view=view)

@bot.event
async def setup_hook():
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Aviso al sincronizar comandos slash: {e}")

# ==========================================
# INICIO DEL BOT
# ==========================================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: No se encontró la variable de entorno 'DISCORD_TOKEN'. Asegúrate de configurarla en tu servidor.")
    else:
        bot.run(TOKEN)
