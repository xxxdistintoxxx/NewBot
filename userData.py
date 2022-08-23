import os
from dotenv import load_dotenv
import vk_api
from dateutil.parser import parse as du_parse
from dateutil.relativedelta import relativedelta
from datetime import datetime


def check_age(date):
    lst = date.split('.')
    lst.reverse()
    date = '.'.join(lst)
    bd = du_parse(date)
    td = datetime.now()
    delta = relativedelta(td, bd).years
    return delta


def check_user_data(user_id):
    load_dotenv('tokens.env')
    search_token = os.getenv('USER_TOKEN')
    vk = vk_api.VkApi(token=search_token).get_api()
    inf = vk.users.get(user_ids=user_id, fields='city,relation,sex,bdate')[0]
    if inf['is_closed']:
        return False
    else:
        result = {}
        try:
            city = inf['city']['title']
            result['city'] = city
        except BaseException:
            result['city'] = ''

        try:
            bdate = inf['bdate']
            age = str(check_age(bdate))
            result['age'] = age
        except BaseException:
            result['age'] = ''

        try:
            sex = inf['sex']
            result['sex'] = str(sex)
        except BaseException:
            result['sex'] = ''

        try:
            mrst = inf['relation']
            result['stat'] = mrst
        except BaseException:
            result['stat'] = ''

        return result



