import random
import discord

def load() -> None:
    global embeds, color_list
    embeds = []
    color_list = [0x3F704D,0x4D6D70,0x704D67,0x6D704D,0x50704D,0x704D4D,0x5B704D,0x704D56,0x4D7070,0x704E3D]


    with open('help.txt') as file:
        raw_text = file.read()

    pages = raw_text.split('#page#')
    for page in pages:
        embed = discord.Embed()

        if '#footer#' not in page:
            embed.description = page
        else:
            split = page.split('#footer#')


            embed.description = split[0]
            embed.set_footer(text=split[1])
        embeds.append(embed)

    print(' [ INFO ]'.ljust(15) + 'Initialized help message.')


def get_page(page: int):
    embed = embeds[page]
    embed.color = random.choice(color_list)
    return embed