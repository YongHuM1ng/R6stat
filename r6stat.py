import base64
import os
import time
from hoshino import Service
import requests
import traceback
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

sv = Service('r6s战绩查询')

file_path = os.path.dirname(__file__)
font_bold = os.path.join(file_path, "ScoutCond-BoldItalic.otf")
font_regular = os.path.join(file_path, "ScoutCond-RegularItalic.otf")
mmrlevel = {'COPPER ': '紫铜', 'BRONZE ': '青铜', 'SILVER ': '白银', 'GOLD ': '黄金', 'PLATINUM ': '白金',
            'DIAMOND ': '钻石',
            'CHAMPIONS ': '冠军'}


@sv.on_rex('r6')
async def r6(bot, ev):
    msg = ev['raw_message']
    if msg == 'R6':
        name = ev['sender']['card']
        isimg = True
    elif msg[:3] == 'R6 ':
        name = msg[3:]
        isimg = True
    elif msg == 'r6':
        name = ev['sender']['card']
        isimg = False
    elif msg[:3] == 'r6 ':
        name = msg[3:]
        isimg = False
    else:
        return
    r = requests.get('https://r6.tracker.network/api/v0/overwolf/player', params={'name': name}, timeout=10)
    r.encoding = 'utf-8'
    data = r.json()
    if not data['success']:
        if data['reason'] == 'InvalidName':
            await bot.send(ev, '没有这个游戏ID', at_sender=True)
            return
        await bot.send(ev, '出现错误，错误原因：%s' % data['reason'], at_sender=True)
    if isimg:
        try:
            for i in range(len(data['seasons'])):
                if data['seasons'][i]['season'] == data['currentSeason']:
                    if data['seasons'][i]['regionLabel'] == 'CASUAL':
                        season1 = data['seasons'][i]
                if data['seasons'][i]['season'] == data['currentSeason']:
                    if data['seasons'][i]['regionLabel'] == 'RANKED':
                        season2 = data['seasons'][i]

            avatar = Image.open(BytesIO(requests.get(data['avatar']).content)).resize((150, 150))
            casualimg = Image.open(BytesIO(requests.get(season1['img']).content))
            rankimg = Image.open(BytesIO(requests.get(season2['img']).content)).convert('RGBA')

            back = Image.open(os.path.join(file_path, "back.png"))
            draw = ImageDraw.Draw(back)

            draw.text((515, 105), f'SEASON{data["currentSeason"]}', fill="#FFFFFF",
                      font=ImageFont.truetype(font_bold, size=24))
            back.paste(avatar, (78, 184))
            draw.text((256, 192), f'LEVEL {data["level"]}', fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=36))
            draw.text((256, 230), data['name'], fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=96))

            back.paste(casualimg, (125, 412), mask=casualimg)
            draw.text((181 - ImageFont.truetype(font_bold, size=16).getsize(season1['rankName'])[0] / 2, 518),
                      season1['rankName'], fill="#FFFFFF", font=ImageFont.truetype(font_bold, size=16))
            draw.text((181 - ImageFont.truetype(font_bold, size=48).getsize(str(season1['mmr']))[0] / 2, 530),
                      str(season1['mmr']), fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))

            draw.text((262, 446), str(round(season1['kd'], 2)), fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=48))
            draw.text((384, 446), str(season1['kills']), fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))
            draw.text((491, 446),
                      str(round(season1['kills'] / season1['kd'])) if season1['kd'] != 0 else '0',
                      fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))

            draw.text((262, 521), str(season1['winPct']), fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=48))
            draw.text((384, 521), str(season1['wins']), fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))
            draw.text((491, 521), str(round(season1['wins'] / (season1['winPct'] / 100) - season1['wins'])) if season1[
                                                                                                                   'winPct'] != 0 else '0',
                      fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))

            back.paste(rankimg, (125, 676), mask=rankimg)
            draw.text((181 - ImageFont.truetype(font_bold, size=16).getsize(season2['rankName'])[0] / 2, 782),
                      season2['rankName'], fill="#FFFFFF", font=ImageFont.truetype(font_bold, size=16))
            draw.text((181 - ImageFont.truetype(font_bold, size=48).getsize(str(season2['mmr']))[0] / 2, 794),
                      str(season2['mmr']), fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))

            draw.text((262, 674), str(round(season2['kd'], 2)), fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=48))
            draw.text((384, 674), str(season2['kills']), fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))
            draw.text((491, 674),
                      str(round(season2['kills'] / season2['kd'])) if season2['kd'] != 0 else '0',
                      fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))

            draw.text((262, 749), str(season2['winPct']), fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=48))
            draw.text((384, 749), str(season2['wins']), fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))
            draw.text((491, 749), str(round(season2['wins'] / (season2['winPct'] / 100) - season2['wins'])) if season2[
                                                                                                                   'winPct'] != 0 else '0',
                      fill="#FFFFFF", font=ImageFont.truetype(font_regular, size=48))

            draw.text((262, 824), season2['maxRank']['rankName'], fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=48))
            draw.text((491, 824), str(season2['maxRank']['mmr']), fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=48))

            draw.text((629, 925), time.strftime("%Y-%m-%d %H:%M", time.localtime()), fill="#FFFFFF",
                      font=ImageFont.truetype(font_regular, size=24))

            bio = BytesIO()
            back.save(bio, format='PNG')
            cqimg = f'[CQ:image,file=base64://{base64.b64encode(bio.getvalue()).decode()}]'
            await bot.send(ev, cqimg)
        except requests.exceptions.ConnectionError:
            await bot.send(ev, '网络错误，请重试', at_sender=True)
        except Exception as e:
            await bot.send(ev, '出现错误\nname=%s\n%s' % (name, traceback.format_exc()), at_sender=True)
    else:
        try:
            for i in range(len(data['seasons'])):
                if data['seasons'][i]['season'] == data['currentSeason']:
                    if data['seasons'][i]['regionLabel'] == 'CASUAL':
                        season = data['seasons'][i]
            for i in mmrlevel:
                season['rankName'] = season['rankName'].replace(i, mmrlevel[i])
            await bot.send(ev,
                           f'[CQ:image,file={data["avatar"]}]\n'
                           f'{data["name"]}  等级:{data["level"]}\n'
                           f'KD:{season["kd"]:.2f}         胜率:{season["winPct"]:.0f}%\n'
                           f'休闲分:{season["mmr"]}  {season["rankName"]}\n'
                           f'详细信息:https://r6.tracker.network/profile/pc/{data["name"]}/\n'
                           f'连接用时{r.elapsed.total_seconds()}秒')
        except requests.exceptions.ConnectionError:
            await bot.send(ev, '网络错误，请重试', at_sender=True)
        except Exception as e:
            await bot.send(ev, '出现错误\nname=%s\n%s' % (name, traceback.format_exc()), at_sender=True)