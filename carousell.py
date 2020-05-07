#! python3
import bs4, requests, time, json
import pandas as pd
import os

from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

#   This page must be in recent and sorted by descending
page = str(os.getenv('PAGE'))
resellers = str(os.getenv('RESELLERS')).split(", ")


bot_token = str(os.getenv('BOT_TOKEN'))
bot_chatID = str(os.getenv('BOT_CHATID'))

prevItems = pd.DataFrame(columns=['username', 'name'])

def requestForPage(page):
    #   Download page
    getPage = requests.get(page)
    getPage.raise_for_status() #if error it will stop the program

    #   Parse text for items
    menu = bs4.BeautifulSoup(getPage.text, 'html.parser')
    main = menu.select('._3egzkmmXgV')[0]

    itemsHTML = main.select(".An6bc8d5sQ._9IlksbU0Mo._2t71A7rHgH")
    df = pd.DataFrame(columns=['username', 'name'])
    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    for i, itemHTML in enumerate(itemsHTML, start=1):
        username = itemHTML.select("._1gJzwc_bJS._2NNa9Zomqk.mT74Grr7MA.nCFolhPlNA.lqg5eVwdBz.uxIDPd3H13._30RANjWDIv")[0]
        name = itemHTML.select("._1gJzwc_bJS._2rwkILN6KA.mT74Grr7MA.nCFolhPlNA.lqg5eVwdBz.uxIDPd3H13._30RANjWDIv")[0]
        if username.getText() in resellers:
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - Filter away resellers: " , username.getText())
        else:
            df.loc[i] = [username.getText(), name.getText()]

    return df

def telegram_bot_sendtext(bot_message):
    # print(bot_message)
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message.to_string()

    response = requests.get(send_text)

    return response.json()

def compareDFs(df1, df2):
    return pd.concat([df1,df2]).drop_duplicates(keep=False)


while True:
    #   Request for New page
    newItems = requestForPage(page)
    #   Compare and get updated items
    difference = compareDFs(prevItems, newItems)
    #   Save for comparison later
    prevItems = newItems

    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if prevItems.empty or difference.empty:
        print('DataFrame is empty as of ', dt_string)
    else:
        print("Difference as of ", dt_string)
        print(difference)
        #   Send Difference
        telegram_bot_sendtext(difference)
    time.sleep(int(os.getenv('SLEEP_TIME')))