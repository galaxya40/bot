import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

# Ustawienia bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
def search_olx(query):
    url = f"https://www.olx.pl/oferty/q-{query.replace(' ', '-')}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Zgłosi błąd, jeśli odpowiedź jest nieprawidłowa
    except Exception as e:
        print(f"Błąd żądania HTTP: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    offers = soup.find_all('div', {'data-cy': 'l-card'})  # Znajdujemy wszystkie oferty

    results = []
    for offer in offers[:10]:  # Limitujemy do pierwszych 5 ofert
        try:
            # Sprawdzanie i pobieranie tytułu
            title_element = offer.find('h6', {'class': 'css-16v5mdi'})
            title = title_element.text.strip() if title_element else "to ogloszenie nie ma tytulu"

            # Sprawdzanie i pobieranie ceny
            price_element = offer.find('p', {'data-testid ': 'ad-price  '})
            price = price_element.text.strip() if price_element else "Brak ceny"

            # Sprawdzanie i pobieranie linku
            link_element = offer.find('a')
            if link_element:
                link = link_element['href']
                if not link.startswith('http'):
                    link = f"https://www.olx.pl{link}"
            else:
                link = "Brak linku"

            # Tworzymy wynik
            result = f"**{title}**\n{price}\n{link}"
            results.append(result)
        except Exception as e:
            print(f"Błąd parsowania oferty: {e}")
            continue

    return results if results else None

@bot.command()
async def olx(ctx, *, query):
    try:
        await ctx.send(f"szukam: '{query}'...")
        results = search_olx(query)

        if not results:
            await ctx.send("nie mam dla ciebie ofert")
        else:
            # Podziel wyniki na fragmenty, aby nie przekroczyć limitu 2000 znaków w jednej wiadomości
            for result in results:
                if len(result) > 2000:
                    for i in range(0, len(result), 2000):
                        await ctx.send(result[i:i+2000])
                else:
                    await ctx.send(result)
    except Exception as e:
        await ctx.send("Przepraszam, wystąpił błąd. Spróbuj ponownie później.")
        print(f"Błąd w komendzie olx: {e}")

@bot.event
async def on_ready():
    print(f'zostalem uruchomiony jako  {bot.user}')

bot.run('')
